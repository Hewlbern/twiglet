"""v3.33 wig fusion = the UNCHANGED v3.30 procedural attachment (hair_v330.wig_blend: crown shell + seat + 4 pin bosses/holes + key tongue + hat band
+ arm/trunk relief + eye/snout/collar cuts) applied to a Blender locks STL. The lock shapes themselves come from Blender (blender/build_wig_v333.py).
Usage: fuse_v333.py <locks.stl> <tag>  -> out/wig_<tag>.stl (head-pkl frame) + out/wig_<tag>.json (mesh gate, mass, eye cover, overlaps)"""
import os, sys, json, pickle, time, numpy as np, trimesh
B30 = os.path.join(os.environ.get("WORK", "WORK_NOT_SET"), "twiglet-odm-robot", "body-v3.30"); HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [B30, os.path.dirname(B30)]
os.environ.pop("HAIR_OVR", None)
import hair_v330 as HV, head_v37 as H37
LOCKS_STL, TAG = sys.argv[1], sys.argv[2]; os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
EXTRA = os.environ.get("FUSE_OVR")                 # optional snippet run on HV before the fusion (relief tweaks); empty for the as-v3.30 attachment
if EXTRA: exec(open(EXTRA).read())
t0 = time.time()
P = pickle.load(open(os.path.join(HERE, ".cache", "head_parts.pkl"), "rb")); mk = lambda k: trimesh.Trimesh(*P[k], process=False)
R = {k: mk(k) for k in P if not k.startswith("_")}; meta = P["_meta"]; C = np.array(meta["ball_C"]); Rb = meta["ball_R"]
cones = []
for sd in "LR":
    c0 = R[f"eye_bezel_{sd}"].bounds.mean(0); ax = (c0 - C) / np.linalg.norm(c0 - C); cones.append((ax, 29.0, 105.8))
env = HV.Envelope(C, [], cones, r_min=Rb - 0.5, cache=os.path.join(HERE, ".cache", "env_v314.npz"))
bez_c = {sd: R[f"eye_bezel_{sd}"].bounds.mean(0) for sd in "LR"}
cuts = []
for sd in "LR":
    h = R[f"eye_bezel_{sd}"].convex_hull.copy(); h.apply_transform(trimesh.transformations.scale_matrix(1.012, bez_c[sd])); cuts.append(h)
sn = R["snout"].convex_hull.copy(); sn.apply_transform(trimesh.transformations.scale_matrix(1.02, R["snout"].bounds.mean(0))); cuts.append(sn)
for sd in "LR":                                     # the v3.30 wig was cut with the (larger) v3.29 collar hulls -> same cutters
    cc = trimesh.load(os.path.join(B30, "blender", "trim_v330", f"chin_collar_{sd}_v329.stl")).convex_hull; cc.apply_transform(trimesh.transformations.scale_matrix(1.02, cc.bounds.mean(0))); cuts.append(cc)
HV.BLEND["STL"] = os.path.abspath(LOCKS_STL)
fr, nparts, nl, head_cut, dropped = HV.wig_blend(env, cuts, HV.SMOOTH["SUB"])
print("fused", round(time.time() - t0, 1), "s", flush=True)
V, A = fr.volume, fr.area
info = dict(tag=TAG, locks_stl=os.path.abspath(LOCKS_STL), parts_before_keep=nparts, dropped_mm3=dropped, watertight=bool(fr.is_watertight), winding=bool(fr.is_winding_consistent),
            bodies=len(fr.split(only_watertight=False)), faces=len(fr.faces), extents=np.round(fr.extents, 1).tolist(), volume_cm3=round(V / 1000, 2), area_cm2=round(A / 100, 1),
            sim_g=round(HV.sim_mass(fr), 1), g_4p5=round(1.24e-3 * (min(V, A * 0.8) + 0.045 * max(0.0, V - A * 0.8)), 1),
            moment_gmm=round(HV.sim_mass(fr) * (fr.center_mass[0] - HV.X_AXIS)), com=np.round(fr.center_mass, 2).tolist(), eye_cover=H37.eye_cover(fr, C, bez_c))
_ac = (fr.triangles_center * fr.area_faces[:, None]).sum(0) / A; _mw = 1.24e-3 * A * 0.8; _mi = 1.24e-3 * 0.045 * max(0.0, V - A * 0.8)   # 4.5 % basis: 0.8 mm skin at the area centroid + infill at the volume centroid
_c45 = (_mw * _ac + _mi * fr.center_mass) / (_mw + _mi); info.update(com_4p5=np.round(_c45, 2).tolist(), moment_4p5_gmm=round((_mw + _mi) * (_c45[0] - HV.X_AXIS)))
for k in ("head_upper", "head_lower", "snout", "eye_bezel_L", "eye_bezel_R", "chin_collar_L", "chin_collar_R", "display_carrier_L", "display_carrier_R"):
    x = trimesh.boolean.intersection([fr, R[k]], engine="manifold"); info.setdefault("overlaps_mm3", {})[k] = round(abs(x.volume) if not x.is_empty else 0.0, 2)
fr.export(os.path.join(HERE, "out", f"wig_{TAG}.stl")); json.dump(info, open(os.path.join(HERE, "out", f"wig_{TAG}.json"), "w"), indent=1)
print(json.dumps(info), flush=True); print("total", round(time.time() - t0, 1), "s")
