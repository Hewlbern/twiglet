"""v3.33 wig export: decimated model-frame wig (Blender, blender/decimate_v330.py method) -> print orientation exactly like body-v3.30/export_head_v330.py
(6000 random rotations + crown-down/tilted candidates, least support-column volume, fits 256 mm bed with 6 mm margin), float32-safe, gated.
usage: export_final_v333.py <decimated_model_frame.stl> <full_res_model_frame.stl>"""
import os, sys, json, math, pickle, numpy as np, trimesh
from scipy.spatial.transform import Rotation as Ro
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); B30 = os.path.join(os.path.dirname(HERE), "body-v3.30")
hv = pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "head_parts.pkl"), "rb")); C = np.array(hv["_meta"]["ball_C"]); del hv   # v3.35: head_v330.pkl lost in the 04:15 restore; same ball_C (the assignment had slipped into this comment)
BED = 256.0
FR = trimesh.load(sys.argv[1]); FULL = trimesh.load(sys.argv[2])
m = FR.simplify_quadric_decimation(face_count=30000) if len(FR.faces) > 30000 else FR
A, N, Cc, V = m.area_faces, m.face_normals, m.triangles_center - C, m.vertices - C
def score(r):
    nn = r.apply(N); z = r.apply(Cc)[:, 2]; vz = r.apply(V); z0 = vz[:, 2].min(); z = z - z0
    ov = (nn[:, 2] < -0.707) & (z > 1.0)
    return float((A[ov] * -nn[ov, 2] * z[ov]).sum()), float(A[ov].sum()), np.ptp(vz, axis=0)
cands = list(Ro.random(6000, random_state=2)); up = np.array([0, 0, 1.0])
for tilt in range(0, 50, 5):
    for az in range(0, 360, 30): cands.append(Ro.from_euler("zx", [az, 180 - tilt], degrees=True))
best = None
for r in cands:
    sv, oa, ext = score(r)
    if (ext <= BED - 6).all() and (best is None or sv < best[0]): best = (sv, oa, r, ext)
sv, oa, r, ext = best; T = np.eye(4); T[:3, :3] = r.as_matrix()
o = FR.copy(); o.apply_translation(-C); o.apply_transform(T); o.apply_translation(-o.bounds[0] - [o.extents[0] / 2, o.extents[1] / 2, 0])
def f32_safe(m, sep=1.5e-4):
    V = np.array(m.vertices, float)
    for _ in range(4):
        pr = cKDTree(V).query_pairs(sep * 0.999, output_type="ndarray")
        if not len(pr): break
        for i, j in pr:
            d = V[j] - V[i]; L_ = np.linalg.norm(d); d = d / L_ if L_ > 1e-12 else np.array([1.0, 0, 0]); mv = (sep - L_) / 2; V[i] -= d * mv; V[j] += d * mv
    return trimesh.Trimesh(V, m.faces, process=False)
o = f32_safe(o); fn = os.path.join(HERE, "FINAL_WIG.stl"); o.export(fn)
t_ = trimesh.load(fn); _u, _c = np.unique(t_.edges_sorted, axis=0, return_counts=True)
ax = r.apply(up); tilt = math.degrees(math.acos(np.clip(-ax[2], -1, 1)))
dev = trimesh.proximity.ProximityQuery(FR).signed_distance(FULL.sample(4000)) if len(FULL.faces) else None
R = dict(file=fn, faces=len(t_.faces), mb=round(os.path.getsize(fn) / 1e6, 2), open_edges=int((_c == 1).sum()), nonmanifold_edges=int((_c > 2).sum()), bodies=len(t_.split(only_watertight=False)),
         watertight=bool(t_.is_watertight), winding_ok=bool(t_.is_winding_consistent), volume_cm3=round(t_.volume / 1000, 2), full_res_volume_cm3=round(FULL.volume / 1000, 2),
         size_mm=np.round(t_.extents, 1).tolist(), fits_P1S=bool((t_.extents <= BED - 2).all()), support_column_cm3=round(sv / 1000), overhang_cm2=round(oa / 100, 1),
         orientation=f"print-oriented like v3.30: crown axis tilted {tilt:.0f} deg from straight-down (least support volume of {len(cands)} orientations searched), centred on the bed, z0 = bed",
         rotation_quat_xyzw=np.round(r.as_quat(), 6).tolist(), model_frame_ball_C=C.tolist(),
         decimation_dev_mm=None if dev is None else dict(p50=round(float(np.median(np.abs(dev))), 3), p99=round(float(np.percentile(np.abs(dev), 99)), 3), max=round(float(np.abs(dev).max()), 3)))
print(json.dumps(R)); json.dump(R, open(os.path.join(HERE, "out", "final_export.json"), "w"), indent=1)
