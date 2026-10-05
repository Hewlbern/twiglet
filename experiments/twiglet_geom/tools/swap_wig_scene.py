"""Runs from the repo: replaces the wig (item head3_fringe) in a measurement scene with another wig STL given in the
hair pipeline's head-pkl frame (= the FINAL_WIG_model_frame.stl the hair pipeline exports), using the pkl->asm transform
stored in the scene (eye_bezel_L vertex correspondence, see export_scene.py), decimated to 40k faces like the original.
usage: python tools/swap_wig_scene.py [in.npz] [wig_model_frame.stl] [out.npz]
default: scene/scene_v334_wig340.npz + print/mods/Twiglet/wig_v3.44/FINAL_WIG_model_frame.stl -> scene/scene_v334_wig344.npz"""
import os, sys, json, numpy as np, trimesh
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); REPO = os.path.dirname(os.path.dirname(HERE))
a = sys.argv[1:] + [None] * 3
src = a[0] or os.path.join(HERE, "scene", "scene_v334_wig344.npz")
wig = a[1] or os.path.join(REPO, "print", "mods", "Twiglet", "wig_v3.44", "FINAL_WIG_model_frame.stl")
dst = a[2] or os.path.join(HERE, "scene", "scene_v334_wig344.npz")
Z = np.load(src); meta = json.loads(str(Z["meta"])); R = np.array(meta["wig_pkl_to_asm"]["R"]); t = np.array(meta["wig_pkl_to_asm"]["t"])
w = trimesh.load(wig); w = trimesh.Trimesh(np.asarray(w.vertices) @ R.T + t, w.faces, process=False)
w = w.simplify_quadric_decimation(face_count=40000) if len(w.faces) > 40000 else w
out = {k: Z[k] for k in Z.files if k != "meta"}
i = [k for k, (ln, n, kk) in enumerate(meta["items"]) if n == "head3_fringe"]; assert len(i) == 1; i = i[0]
out[f"V{i}"] = np.asarray(w.vertices, np.float32); out[f"F{i}"] = np.asarray(w.faces, np.int32)
meta["source"] = meta["source"].split(" + ")[0] + " + wig " + os.path.relpath(wig, REPO) + f" ({len(w.faces)} faces)"
out["meta"] = np.array(json.dumps(meta)); np.savez_compressed(dst, **out); print(dst, os.path.getsize(dst) / 1e6, "MB", meta["source"])
