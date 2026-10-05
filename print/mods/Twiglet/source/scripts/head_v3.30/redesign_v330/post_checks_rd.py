"""post-redesign checks (v3.30 head-range redesign): (1) overlaps of the new head_lower / collars / head_yaw_to_roll with every other head part and
the head hardware (pre-redesign baseline alongside), (2) head-split lift (head_upper + wig lifted 0.5-80 mm) vs head_lower / collars,
(3) eye coverage, (4) neck part vs head side over roll -30..30 (2 deg) and vs head_pitch_to_yaw over yaw -160..160 (5 deg), (5) thin features
(< 1.2 mm, raster opening) new vs old on sections through every changed feature.  python blender/redesign_v330/post_checks_rd.py"""
import os, sys, json, math, pickle, numpy as np, trimesh
from trimesh.transformations import rotation_matrix
from scipy import ndimage
from matplotlib.path import Path
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path[:0] = [HERE, os.path.dirname(HERE)]
RD = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(HERE, "blender", "out_v330")
M2L = np.array([-2.1, 0.0, -66.0]); L2P = np.array([4.125, -0.1, -105.751])
R = pickle.load(open(os.path.join(HERE, ".cache", "head_v330.pkl"), "rb"))          # model frame, redesigned parts loaded
old = {n: trimesh.load(os.path.join(RD, "in", f"{n}_v330a.stl")) for n in ("head_lower", "chin_collar_L", "chin_collar_R")}
def iv(a, b):
    if not (np.all(a.bounds[0] < b.bounds[1]) and np.all(b.bounds[0] < a.bounds[1])): return 0.0
    x = trimesh.boolean.intersection([a, b], engine="manifold", check_volume=False); return round(abs(x.volume) if not x.is_empty else 0.0, 3)
out = {"overlaps_mm3": {}, "overlaps_pre_mm3": {}}
others = ("head_upper", "snout", "eye_bezel_L", "eye_bezel_R", "display_carrier_L", "display_carrier_R", "fringe")
for n in ("head_lower", "chin_collar_L", "chin_collar_R"):
    for k in others + tuple(x for x in ("head_lower", "chin_collar_L", "chin_collar_R") if x != n):
        out["overlaps_mm3"][f"{n} x {k}"] = iv(R[n], R[k]); out["overlaps_pre_mm3"][f"{n} x {k}"] = iv(old[n], old[k] if k in old else R[k])
# hardware in the head (link frame, from the rev C model) + neck mechanism
M = pickle.load(open(os.path.join(HERE, "revC", ".cache", "v3model.pkl"), "rb"))
HW = {n: m for n, m, k in M["links"]["head_assembly"] if not n.startswith("head3_") and k not in ("eyering",)}
NECK = {n: m for n, m, k in M["links"]["neck_yaw_assembly"]}; HP = [m for n, m, k in M["links"]["head_pitch_to_yaw"]][0]
J = {j[0]: j for j in M["joints"]}; del M
HL = R["head_lower"].copy(); HL.apply_translation(M2L); CL = {s: R[f"chin_collar_{s}"].copy().apply_translation(M2L) for s in "LR"}
HL0 = old["head_lower"].copy(); HL0.apply_translation(M2L)
out["hardware_overlaps_mm3"] = {f"head_lower x {n}": (iv(HL, m), iv(HL0, m)) for n, m in HW.items()}
# (4) neck vs head side over roll; neck vs head_pitch_to_yaw over yaw
nk = NECK["v3_head_yaw_to_roll"]; head_side = dict(head_lower=HL, chin_collar_L=CL["L"], chin_collar_R=CL["R"], **{f"hw:{n}": m for n, m in HW.items()})
cm = trimesh.collision.CollisionManager()
for n, m in head_side.items(): cm.add_object(n, m.simplify_quadric_decimation(face_count=150000) if len(m.faces) > 150000 else m)
pr, ax = J["head_roll"][3], J["head_roll"][4]; roll = {}
for a in range(-30, 31, 2):
    T = rotation_matrix(math.radians(a), ax, point=pr)
    for n in head_side: cm.set_transform(n, T)
    c, nm = cm.in_collision_single(nk, return_names=True); roll[a] = sorted(nm) if c else []
out["neck_vs_head_roll"] = {k: v for k, v in roll.items() if v} or "clear -30..30"
py, ay = J["head_yaw"][3], J["head_yaw"][4]; yaw = {}
cy = trimesh.collision.CollisionManager(); cy.add_object("hp", HP)
for a in range(-160, 161, 5):
    T = rotation_matrix(math.radians(a), ay, point=py); c = cy.in_collision_single(nk, transform=T)
    c2 = any(cy.in_collision_single(m, transform=T) for m in (HL.simplify_quadric_decimation(face_count=150000), ))
    if c or c2: yaw[a] = dict(neck=bool(c), head_lower=bool(c2))
out["neck_head_vs_head_pitch_to_yaw_yaw"] = yaw or "clear -160..160"
# (2) lift + (3) eye cover
out["lift_overlap_mm3"] = {}
for dz in (0.5, 2, 5, 10, 20, 40, 80):
    v = 0.0
    for nm in ("head_upper", "fringe"):
        u = R[nm].copy(); u.apply_translation([0, 0, dz])
        for t in ("head_lower", "chin_collar_L", "chin_collar_R"): v += iv(u, R[t]) if dz > 0.5 or t != "head_lower" else 0.0
    out["lift_overlap_mm3"][str(dz)] = round(v, 3)
import head_v37 as H37
C = np.array(R["_meta"]["ball_C"]); bez_c = {sd: R[f"eye_bezel_{sd}"].bounds.mean(0) for sd in "LR"}; out["eye_cover"] = H37.eye_cover(R["fringe"], C, bez_c)
# (5) thin features
def thin_area(m, o, n, pix=0.05, w=1.2):
    s = m.section(plane_origin=o, plane_normal=n); tot = 0.0
    if s is None: return 0.0
    n = np.asarray(n, float); n /= np.linalg.norm(n); u = np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.array([1.0, 0, 0]); u /= np.linalg.norm(u); v = np.cross(n, u)
    for e in s.discrete:
        uv = np.c_[(e - o) @ u, (e - o) @ v]; lo = uv.min(0) - 1; hi = uv.max(0) + 1
        if np.prod((hi - lo) / pix) > 4e7: continue
        gx, gy = np.meshgrid(np.arange(lo[0], hi[0], pix), np.arange(lo[1], hi[1], pix))
        ins = Path(uv).contains_points(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
        k = int(round(w / 2 / pix)); yy, xx = np.mgrid[-k:k + 1, -k:k + 1]; disk = xx ** 2 + yy ** 2 <= k * k
        tot += (ins & ~ndimage.binary_opening(ins, structure=disk)).sum() * pix * pix
    return tot
def radial(a, cx=9.7):
    t = np.radians(a); return np.array([cx, 0, 0.0]), np.array([-np.sin(t), np.cos(t), 0.0])
secs = {"head_lower": [("y", [0, y, 0], [0, 1, 0]) for y in (-14, -8, 0, 8, 14)] + [("x", [x, 0, 0], [1, 0, 0]) for x in (-38.2, -36, -33, -31)]
                      + [("phi", *radial(a)) for a in (28, -28, 52, -52, 97, -97, 103, -103, 140, 180)],
        "chin_collar_L": [("phi", *radial(a)) for a in (26, 28, 30, 50, 52, 54, 62, 63.8)], "chin_collar_R": [("phi", *radial(a)) for a in (-26, -28, -30, -50, -52, -54, -62, -63.8)]}
th = {}
for n, L in secs.items():
    new_m = HL if n == "head_lower" else CL[n[-1]]; old_m = HL0 if n == "head_lower" else old[n].copy().apply_translation(M2L); rows = []
    for tag, o, nn in L:
        a, b = thin_area(new_m, np.array(o, float), nn), thin_area(old_m, np.array(o, float), nn); rows.append((tag, np.round(o, 1).tolist(), round(a, 3), round(b, 3)))
    th[n] = dict(max_extra_thin_mm2=round(max(r[2] - r[3] for r in rows), 3), rows=rows)
nk0 = trimesh.load(os.path.join(RD, "in", "head_yaw_to_roll_v39.stl")); nk0.apply_translation(-L2P); rows = []
for tag, o, nn in [("y", [0, y, 0], [0, 1, 0]) for y in (-33, -20, -8, 0, 8, 20, 33)] + [("x", [x, 0, 0], [1, 0, 0]) for x in (-36, -30, -26, -20, -13)] + [("z", [0, 0, z], [0, 0, 1]) for z in (108, 115, 120)]:
    a, b = thin_area(nk, np.array(o, float), nn), thin_area(nk0, np.array(o, float), nn); rows.append((tag, o, round(a, 3), round(b, 3)))
th["head_yaw_to_roll"] = dict(max_extra_thin_mm2=round(max(r[2] - r[3] for r in rows), 3), rows=rows)
out["thin_lt_1.2mm"] = th
out["vol_cm3"] = {n: round(R[n].volume / 1000, 3) for n in ("head_lower", "chin_collar_L", "chin_collar_R")}; out["vol_cm3"]["head_yaw_to_roll"] = round(nk.volume / 1000, 3)
json.dump(out, open(os.path.join(RD, "post_checks_rd.json"), "w"), indent=1, default=str)
print(json.dumps({k: (v if k not in ("thin_lt_1.2mm",) else {n: x["max_extra_thin_mm2"] for n, x in v.items()}) for k, v in out.items()}, default=str))
