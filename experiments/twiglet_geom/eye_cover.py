"""Eye coverage: does the wig hang in front of the digital-eye openings? (logic from hair-v3.40/checks/eye_who.py)
For each eye, take the bezel centre e and the eye axis n (from the head-ball centre C through e). Count the wig triangles whose
centres lie inside a 26.7 mm radius cylinder about that axis, in front of the plane 12 mm behind the bezel centre.
PASS: 0 triangles for both eyes (hair budget "eye 0/0").   usage: python eye_cover.py"""
import json, os, numpy as np
import geomlib as G
items, _ = G.load_scene(); C = np.array(json.load(open(os.path.join(G.HERE, "scene", "head_meta.json")))["ball_C_asm_mm"])
w = [G.TM(V, F) for ln, n, k, V, F in items if n == "head3_fringe"][0]; out = {}
for sd in "LR":
    V = [V for ln, n, k, V, F in items if n == f"head3_eye_bezel_{sd}"][0].astype(float); e = (V.min(0) + V.max(0)) / 2
    n = (e - C) / np.linalg.norm(e - C); u = np.cross(n, [0, 0, 1]); u /= np.linalg.norm(u); v = np.cross(n, u)
    c = w.triangles_center; d = (c - e) @ n; x = (c - e) @ u; y = (c - e) @ v; m = (d > -12) & (x * x + y * y < 26.7 ** 2)
    out[f"eye_{sd}"] = dict(wig_triangles_in_eye_cylinder=int(m.sum()), eye_centre_mm=e.round(2).tolist()); print(sd, out[f"eye_{sd}"])
out["pass"] = all(out[f"eye_{s}"]["wig_triangles_in_eye_cylinder"] == 0 for s in "LR"); G.save("eye_cover_v334_wig344.json", out)
