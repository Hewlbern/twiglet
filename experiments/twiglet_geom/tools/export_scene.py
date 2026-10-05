"""PROVENANCE ONLY (needs the original build workspace, not the repo): writes scene/scene_v334_wig340.npz.
The scene is the v3.34b rest-pose measurement scene (asm frame, mm), i.e. body-v3.34-body measure/mlib.load_scene(scene_for("v334_current")).
In it, head3_fringe (the old v3.30 wig) is replaced by the hair v3.40 wig (hair-v3.40/out/wig_y2.stl, head-pkl frame -> asm frame through the
eye_bezel_L vertex correspondence, decimated to 40k faces). This is exactly what hair-v3.40/checks/arm_head_check.py does.
It also stores the 19 joints (name, parent, child, point mm, axis, range) used for forward kinematics.
usage (on the build box): WS=$WORK/twiglet-odm-robot python export_scene.py"""
import os, sys, json, pickle, numpy as np, trimesh
WS = os.environ["WS"]; B = os.path.join(WS, "body-v3.34-body"); H = os.path.join(WS, "hair-v3.40")
sys.path.insert(0, os.path.join(B, "measure")); import mlib as ML, measure_parts as MP
items = ML.load_scene(MP.scene_for("v334_current")); joints = pickle.load(open(os.path.join(B, ".cache", "scene_base.pkl"), "rb"))["joints"]
P = pickle.load(open(os.path.join(H, ".cache", "head_parts.pkl"), "rb"))
A = np.asarray(P["eye_bezel_L"][0], float); Bv = [V for ln, n, k, V, F in items if n == "head3_eye_bezel_L"][0].astype(float); del P
ma, mb = A.mean(0), Bv.mean(0); U, Sg, Vt = np.linalg.svd((Bv - mb).T @ (A - ma)); Dm = np.eye(3)
if np.linalg.det(U @ Vt) < 0: Dm[2, 2] = -1
Rm = U @ Dm @ Vt; t = mb - Rm @ ma; print("pkl->asm resid", float(np.abs(A @ Rm.T + t - Bv).max()))
w = trimesh.load(os.path.join(H, "out", "wig_y2.stl")); w = trimesh.Trimesh(np.asarray(w.vertices) @ Rm.T + t, w.faces, process=False)
wig = w.simplify_quadric_decimation(face_count=40000) if len(w.faces) > 40000 else w
items = [it for it in items if it[1] != "head3_fringe"] + [("head_assembly", "head3_fringe", "head3", np.asarray(wig.vertices, np.float32), np.asarray(wig.faces, np.int32))]
out = {}; meta = []
for i, (ln, n, k, V, F) in enumerate(items):
    out[f"V{i}"] = np.asarray(V, np.float32); out[f"F{i}"] = np.asarray(F, np.int32); meta.append([ln, n, k])
J = [[jn, par, ch, [float(x) for x in p], [float(x) for x in ax], [float(x) for x in rng]] for jn, par, ch, p, ax, rng in joints]
out["meta"] = np.array(json.dumps({"items": meta, "joints": J, "wig_pkl_to_asm": {"R": Rm.tolist(), "t": t.tolist()},
                                   "source": "body-v3.34-body scene_for('v334_current') + hair-v3.40 wig_y2 (40k)"}))
dst = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scene", "scene_v334_wig340.npz")
np.savez_compressed(dst, **out); print(dst, len(items), os.path.getsize(dst) / 1e6, "MB")
