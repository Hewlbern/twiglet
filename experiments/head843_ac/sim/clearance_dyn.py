"""Trajectory-synchronized clearance on the AC mesh scene.

Joint angles come from the simulator (radians). They are converted to degrees and
applied with the scene's own forward kinematics (geomlib.make_fk), which stores
meshes in millimetres in the assembly frame.

This is discrete samples of the simulated trajectory plus one linearly interpolated
joint midpoint between samples. It is not a continuous triangle swept volume.

Locked keeper ids F4, G3, D9 and wig v6b0 are not renamed or edited. If those names
are absent from the scene, the result says so and does not claim those locks were checked.
"""
import os, json, math
import numpy as np
import trimesh
from trimesh.transformations import transform_points

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, os.path.join(ROOT, "geom"))
import geomlib as G

PRIORITY_RULES = (
    "head_assembly vs each arm link",
    "head_assembly vs trunk_assembly",
    "trunk_assembly vs each leg link that is not a kinematic neighbor",
    "forearm and finger vs trunk_assembly",
    "left foot/shin vs right foot/shin",
)

def _thin(mesh, n):
    if len(mesh.faces) <= n:
        return mesh, "kept"
    method = "quadric"
    try:
        out = mesh.simplify_quadric_decimation(face_count=int(n))
        if 0 < len(out.faces) <= int(n * 1.25):
            return out, "quadric"
        method = f"quadric_left_{len(out.faces)}"
    except Exception as exc:
        method = "quadric_fail"
    idx = np.linspace(0, len(mesh.faces) - 1, int(n)).astype(int)
    thin = trimesh.Trimesh(mesh.vertices, mesh.faces[idx], process=False)
    return thin, "face_subset_after_" + method

def _link_mesh(parts, cap):
    meshes = [G.TM(V, F) for _n, V, F, _k in parts]
    cat = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]
    return _thin(cat, cap)

def build(scene_path=None, face_cap=2200, head_cap=4500):
    items, joints = G.load_scene(scene_path)
    Z = np.load(scene_path or G.default_scene_path(), allow_pickle=True)
    meta = json.loads(str(Z["meta"]))
    excluded = []
    groups = {}
    names = {}
    for ln, n, k, V, F in items:
        if str(k).startswith("sim_") or str(n).startswith("sim_"):
            excluded.append(dict(link=ln, name=n, kind=k, reason="legacy simulator visual copy stored in the scene; not a printed part"))
            continue
        groups.setdefault(ln, []).append((n, V, F, k))
        names.setdefault(ln, []).append(n)
    meshes = {}
    how = {}
    for ln, parts in groups.items():
        cap = head_cap if ln == "head_assembly" else face_cap
        meshes[ln], how[ln] = _link_mesh(parts, cap)
    neighbors = []
    for jn, par, ch, p, ax, rng in joints:
        neighbors.append(dict(joint=jn, parent=par, child=ch, reason="kinematic neighbor; parts are expected to meet at the joint"))
    neighbor_set = {tuple(sorted((a["parent"], a["child"]))) for a in neighbors}
    links = sorted(meshes)
    arms = [l for l in links if l in G.ARMA or l.startswith("upper_arm") or l.startswith("fore_arm") or l.startswith("finger")]
    legs = [l for l in links if "knee" in l or "foot" in l or "roll_to_pitch" in l or l.startswith("hip_roll")]
    priority = set()
    def add(a, b):
        if a == b or a not in meshes or b not in meshes:
            return
        if tuple(sorted((a, b))) in neighbor_set:
            return
        priority.add(tuple(sorted((a, b))))
    for l in arms:
        add("head_assembly", l)
        add("trunk_assembly", l)
    add("head_assembly", "trunk_assembly")
    for l in legs:
        add("trunk_assembly", l)
    for a, b in (("foot_assembly", "foot_assembly_2"),
                 ("knee_and_ankle_assembly_2", "knee_and_ankle_assembly_4"),
                 ("knee_and_ankle_assembly_2", "foot_assembly_2"),
                 ("knee_and_ankle_assembly_4", "foot_assembly")):
        add(a, b)
    others = []
    for i, a in enumerate(links):
        for b in links[i + 1:]:
            key = tuple(sorted((a, b)))
            if key in neighbor_set or key in priority:
                continue
            others.append(key)
    cms = {}
    for ln, mesh in meshes.items():
        cm = trimesh.collision.CollisionManager()
        cm.add_object(ln, mesh)
        cms[ln] = cm
    lock_names = [n for ln, n, k in meta["items"] if any(tok in n for tok in ("F4", "G3", "D9", "v6b0", "wigv6"))]
    return dict(fk=G.make_fk(joints), cms=cms, meshes=meshes, how=how, excluded=excluded,
                neighbors=neighbors, neighbor_set=neighbor_set, priority=sorted(priority), others=others,
                names=names, meta_source=meta.get("source"), lock_name_hits=lock_names,
                face_counts={ln: int(len(meshes[ln].faces)) for ln in meshes},
                part_names_head=names.get("head_assembly", []))

def _set(cms, Tw):
    for ln, cm in cms.items():
        cm.set_transform(ln, Tw.get(ln, np.eye(4)))

def contacts(ctx, qdeg, pairs, distance=True):
    Tw = ctx["fk"](qdeg)
    _set(ctx["cms"], Tw)
    hit = []
    dist = {}
    for a, b in pairs:
        key = f"{a}|{b}"
        c = ctx["cms"][a].in_collision_other(ctx["cms"][b], return_data=False)
        if c:
            hit.append(key)
        if not distance:
            continue
        try:
            dist[key] = float(ctx["cms"][a].min_distance_other(ctx["cms"][b]))
        except Exception:
            dist[key] = 0.0 if c else None
    return hit, dist

def stance_contacts(ctx, qdeg):
    hit, dist = contacts(ctx, qdeg, ctx["priority"])
    return hit, {k: v for k, v in dist.items() if v is not None and v <= 0.0}

def evaluate_trajectory(ctx, samples_rad, stance_rad, label, hz=25.0):
    """samples_rad: list of {joint: radians} at uniform spacing 1/hz."""
    stance = {k: math.degrees(v) for k, v in stance_rad.items()}
    rest_hit, rest_touch = stance_contacts(ctx, stance)
    rest_set = set(rest_hit)
    new_hits = {}
    min_dist = {f"{a}|{b}": 1e9 for a, b in ctx["priority"]}
    series = []
    n = 0
    n_mid = 0
    worst = None
    prev = None
    for qrad in samples_rad:
        qdeg = {k: math.degrees(v) for k, v in qrad.items()}
        poses = [qdeg]
        if prev is not None:
            mid = {k: 0.5 * (prev[k] + qdeg.get(k, prev[k])) for k in prev}
            poses.append(mid)
            n_mid += 1
        for q in poses:
            is_mid = q is not qdeg
            hit, dist = contacts(ctx, q, ctx["priority"], distance=not is_mid)
            n += 1
            for h in hit:
                if h not in rest_set:
                    new_hits[h] = new_hits.get(h, 0) + 1
            if dist and not is_mid:
                vals = [v for v in dist.values() if v is not None]
                if vals:
                    series.append(round(float(min(vals)), 3))
            for k, v in dist.items():
                if v is None:
                    continue
                if v < min_dist.get(k, 1e9):
                    min_dist[k] = v
                    if worst is None or v < worst[0]:
                        worst = (v, k, {kk: round(q.get(kk, 0.0), 2) for kk in (
                            "left_knee", "right_knee", "head_yaw", "head_pitch", "shoulder_L", "elbow_L")})
        if (len(samples_rad) > 0) and (n % 8 == 0):
            hit_o, _ = contacts(ctx, qdeg, ctx["others"], distance=False)
            for h in hit_o:
                new_hits["other:" + h] = new_hits.get("other:" + h, 0) + 1
        prev = qdeg
    finite = {k: round(v, 3) for k, v in min_dist.items() if v < 1e8}
    closest = sorted(finite.items(), key=lambda kv: kv[1])[:12]
    return dict(label=label, samples=len(samples_rad), queries=n, midpoints=n_mid,
                sample_hz=hz,
                interpolation="one linear joint-space midpoint between samples; not a continuous swept volume",
                stance_contacts_excluded=sorted(rest_set),
                stance_nonpositive_distance_mm=rest_touch,
                new_contacts=new_hits,
                new_contact_pair_count=len(new_hits),
                min_distance_mm_closest=closest,
                min_distance_mm=None if not closest else closest[0][1],
                min_distance_pair=None if not closest else closest[0][0],
                worst_pose_deg=None if worst is None else worst[2],
                min_distance_series_mm=series)

def frame_spotcheck(scene_path, xml_path):
    """Compare one head-yaw pose: scene FK centroid vs MuJoCo body-frame placement of the same vertices."""
    import mujoco
    items, joints = G.load_scene(scene_path)
    fk = G.make_fk(joints)
    fringe = None
    for ln, n, k, V, F in items:
        if n == "head3_fringe":
            fringe = np.asarray(V, float)
            break
    if fringe is None:
        return dict(ok=False, reason="head3_fringe missing")
    # subsample vertices
    step = max(1, len(fringe) // 4000)
    V = fringe[::step]
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)
    d.qpos[:] = m.qpos0
    mujoco.mj_kinematics(m, d)
    bt = m.body("trunk_assembly").id
    hd = m.body("head_assembly").id
    def body_T(bid):
        Rt = d.xmat[bt].reshape(3, 3); pt = d.xpos[bt]
        R = Rt.T @ d.xmat[bid].reshape(3, 3)
        p = Rt.T @ (d.xpos[bid] - pt) * 1000.0
        M = np.eye(4); M[:3, :3] = R; M[:3, 3] = p
        return M
    T0 = body_T(hd)
    Vb = transform_points(V, np.linalg.inv(T0))
    def set_yaw(deg):
        j = m.joint("head_yaw").id
        d.qpos[:] = m.qpos0
        d.qpos[m.jnt_qposadr[j]] = math.radians(deg)
        mujoco.mj_kinematics(m, d)
    errs = {}
    for deg in (0.0, 20.0):
        set_yaw(deg)
        Tm = body_T(hd)
        cm = transform_points(Vb, Tm).mean(0)
        cs = transform_points(V, fk({"head_yaw": deg})["head_assembly"]).mean(0)
        errs[str(deg)] = round(float(np.linalg.norm(cm - cs)), 3)
    return dict(part="head3_fringe", vertices_used=int(len(V)), centroid_error_mm=errs,
                note="Error between scene FK and AC XML body frames. Inertials in the XML are not these vertices.")
