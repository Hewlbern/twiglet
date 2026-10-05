"""loads the Blender redesign outputs (blender/out_v330/head_lower, chin_collar_L/R (model frame), head_yaw_to_roll (print frame)) into
.cache/head_v330.pkl and both v3model.pkl (head_assembly: head3_head_lower / collars, roll_bearing moved +12.1 mm in x on the roll axis;
neck_yaw_assembly: v3_head_yaw_to_roll). Pre-redesign copies: *_prerd.pkl."""
import os, shutil, pickle, gc, json, numpy as np, trimesh
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); O = os.path.join(HERE, "blender", "out_v330")
M2L = np.array([-2.1, 0.0, -66.0]); L2P = np.array([4.125, -0.1, -105.751]); DXB = 12.1
def ld(n):
    m = trimesh.load(os.path.join(O, n + ".stl"), process=True); m.merge_vertices(); assert m.is_volume and len(m.split(only_watertight=False)) == 1, n; return m
new = {n: ld(n) for n in ("head_lower", "chin_collar_L", "chin_collar_R", "head_yaw_to_roll")}
hp = os.path.join(HERE, ".cache", "head_v330.pkl")
if not os.path.exists(hp.replace(".pkl", "_prerd.pkl")): shutil.copy(hp, hp.replace(".pkl", "_prerd.pkl"))
R = pickle.load(open(hp, "rb")); before = {n: round(R[n].volume / 1000, 3) for n in ("head_lower", "chin_collar_L", "chin_collar_R")}
for n in ("head_lower", "chin_collar_L", "chin_collar_R"): R[n] = new[n]
R["_meta"]["redesign_v330"] = dict(vol_cm3={n: round(new[n].volume / 1000, 3) for n in new}, vol_before_cm3=before, src="blender/redesign_v330.py", bearing_dx_mm=DXB)
pickle.dump(R, open(hp, "wb")); del R; gc.collect(); rep = {}
for mp in (os.path.join(HERE, ".cache", "v3model.pkl"), os.path.join(HERE, "revC", ".cache", "v3model.pkl")):
    if not os.path.exists(mp.replace(".pkl", "_prerd.pkl")): shutil.copy(mp, mp.replace(".pkl", "_prerd.pkl"))
    M = pickle.load(open(mp, "rb")); L = M["links"]["head_assembly"]; done = []
    for i, (n, m, k) in enumerate(L):
        if n in ("head3_head_lower", "head3_chin_collar_L", "head3_chin_collar_R"):
            nm = new[n[6:]].copy(); nm.apply_translation(M2L); L[i] = (n, nm, k); done.append(n)
        elif n == "roll_bearing.stl":
            if m.bounds[0][0] < -45: nm = m.copy(); nm.apply_translation([DXB, 0, 0]); L[i] = (n, nm, k); done.append(n)
    L[:] = [it for it in L if it[0] != "ballast_back"]
    bal = trimesh.load(os.path.join(HERE, "blender", "redesign_v330", "ballast_25g.stl")); L.append(("ballast_back", bal, "elec_ballast")); done.append("ballast_back")   # link frame, 25 g (gen_mjcf_v3 FIXED)
    N = M["links"]["neck_yaw_assembly"]
    for i, (n, m, k) in enumerate(N):
        if n == "v3_head_yaw_to_roll": nm = new["head_yaw_to_roll"].copy(); nm.apply_translation(-L2P); N[i] = (n, nm, k); done.append(n)
    if "new" in M and "head_yaw_to_roll" in M["new"]: M["new"]["head_yaw_to_roll"] = [m for n, m, k in N if n == "v3_head_yaw_to_roll"][0]
    pickle.dump(M, open(mp, "wb")); rep[os.path.relpath(mp, HERE)] = done; del M; gc.collect()
print("LOADED", json.dumps(rep), json.dumps({n: round(m.volume / 1000, 3) for n, m in new.items()}))
