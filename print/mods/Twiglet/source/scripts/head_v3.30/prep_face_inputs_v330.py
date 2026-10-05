"""Data hand-off for blender/face_v330_bpy.py (NO geometry editing here): writes the unchanged v3.29 parts as STL plus the interface
parameters (ball, split, carrier posts, socket frame, pod pieces at their v3.29 position) to blender/in_v329/."""
import os, sys, json, pickle, numpy as np, trimesh
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ROOT, os.path.join(ROOT, "head-v3-digital-eyes", "scripts")]
import parts_head3 as P3, parts_head2_base as H, head_recut as HR, head_v312 as H12
OUT = os.path.join(HERE, "blender", "in_v329"); os.makedirs(OUT, exist_ok=True)
hv = pickle.load(open(os.path.join(HERE, ".cache", "head_v329.pkl"), "rb")); m = hv["_meta"]
from scipy.spatial import cKDTree
def f32_safe(m, sep=1.5e-4):
    """float32 hand-off: Blender stores float32, which snaps float64-distinct vertices < ~3e-5 mm apart onto each other ('kissing' edges ->
    non-manifold input for the booleans). Push such pairs apart to `sep` (sub-micron, no visible change) so the STL stays watertight."""
    V = np.array(m.vertices, float); n = 0
    for _ in range(4):
        pr = cKDTree(V).query_pairs(sep * 0.999, output_type="ndarray")
        if not len(pr): break
        for i, j in pr:
            d = V[j] - V[i]; L = np.linalg.norm(d); d = d / L if L > 1e-12 else np.array([1.0, 0, 0]); mv = (sep - L) / 2
            V[i] -= d * mv; V[j] += d * mv; n += 1
    return trimesh.Trimesh(V, m.faces, process=False), n
rep = {}
for k in ("head_upper", "head_lower", "eye_bezel_L", "eye_bezel_R", "display_carrier_L", "display_carrier_R", "snout", "chin_collar_L", "chin_collar_R"):
    mm, n = f32_safe(hv[k]); fn = os.path.join(OUT, k + ".stl"); mm.export(fn)
    t = trimesh.load(fn); rep[k] = (n, bool(t.is_watertight), len(t.split(only_watertight=False)))
print("f32 hand-off (pairs moved, watertight after float32 STL, bodies):", rep)
S = m["S"]; Q = HR.Q_LOCAL; Tm = trimesh.transformations.scale_matrix(S, Q)
u, v, w = H.snout_frame(); M = H.placeM(H.SN_P, u, v, w); Psock = Q + S * (np.array(H.SN_P) - Q)
SN = dict(H12.SN); SN.update(YAW=-4.0, PITCH=22.0, PLUG=True)
t0 = H.dirv(SN["YAW"], SN["PITCH"]); u2, v2, w2 = H.frame(t0, up=(0, 0, -1)); P0 = Psock + SN["SH_U"] * u2 + SN["SH_V"] * v2
posts = []
for sd in "LR":
    t = np.array(m["disp_offset"][sd]); pts, _ = P3._post_xy(sd); zt = P3.post_top_z(sd) + t[2]
    posts += [[float(p[0] + t[0]), float(p[1] + t[1]), float(zt)] for p in pts]
    for i, pp in enumerate(P3.pod_pieces(sd)):
        pp = pp.copy(); pp.apply_translation(t); pp.export(os.path.join(OUT, f"pod_{sd}{i}.stl"))
eyes = {sd: hv[f"eye_bezel_{sd}"].bounds.mean(0).tolist() for sd in "LR"}
P = dict(C=m["ball_C"], Rb=m["ball_R"], zsplit=m["zsplit"], S=S, eye_centre_v329=eyes, posts=posts, POST_R=P3.POST_R, POST_INS_D=P3.POST_INS_D, POST_INS_R=P3.POST_INS_R,
         sock_M=(Tm @ M).tolist(), SN_RB=H.SN_RB, snout=dict(SN, P0=P0.tolist(), u=list(u2), v=list(v2), w=list(w2)))
json.dump(P, open(os.path.join(OUT, "params.json"), "w"), indent=1, default=float)
print("prep ok", OUT)
