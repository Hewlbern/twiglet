"""Print-file check for every STL in print/mods/Twiglet/: watertight, number of bodies, volume, extents, fits the Bambu P1S
(256 x 256 x 256 mm), and an inward-ray wall survey (thickness percentiles, % of surface under 1.2 mm; 2000 samples per part).
PASS: watertight, 1 body, fits the P1S. Walls are informative (decorative tips and fit features are thin on purpose).
usage: python print_check.py [subfolder ...]   e.g. python print_check.py wig_v3.44"""
import os, sys, glob, numpy as np, trimesh
import geomlib as G
ROOT = os.path.join(os.path.dirname(os.path.dirname(G.HERE)), "print", "mods", "Twiglet")
subs = sys.argv[1:] or ["body_v3.34", "head_v3.30", "wig_v3.44"]
def walls(m, n=2000):
    pts, fi = trimesh.sample.sample_surface(m, n, seed=0); nr = m.face_normals[fi]; o = pts - nr * 0.02
    loc, ri, _ = m.ray.intersects_location(o, -nr, multiple_hits=False); d = np.full(len(pts), np.inf); d[ri] = np.linalg.norm(loc - o[ri], axis=1); d = d[np.isfinite(d)]
    p = np.percentile(d, [0.5, 2, 50]); return dict(p0_5=round(p[0], 2), p2=round(p[1], 2), median=round(p[2], 2), pct_below_1p2=round(float((d < 1.2).mean() * 100), 2))
out = {}; bad = []
for s in subs:
    for f in sorted(glob.glob(os.path.join(ROOT, s, "*.stl"))):
        if "_model_frame" in os.path.basename(f): continue   # same mesh in the head model frame (for the sims), not a print file
        m = trimesh.load(f, force="mesh"); ext = (m.bounds[1] - m.bounds[0]).round(1)
        r = dict(watertight=bool(m.is_watertight), bodies=len(m.split(only_watertight=False)), vol_cm3=round(float(m.volume) / 1000, 2), extents_mm=ext.tolist(),
                 fits_p1s=bool((np.sort(ext) <= 256).all()), faces=len(m.faces))
        if "--no-walls" not in sys.argv:
            # the ray survey on the 300-400k-face head shells needs ~5 GB of RAM: decimate those to 60k faces for the wall survey only
            mw = m.simplify_quadric_decimation(face_count=60000) if len(m.faces) > 100000 else m
            r["walls_mm"] = walls(mw); r["walls_on_decimated_60k"] = mw is not m
        r["pass"] = r["watertight"] and r["bodies"] == 1 and r["fits_p1s"]; out[f"{s}/{os.path.basename(f)}"] = r
        if not r["pass"]: bad.append(f"{s}/{os.path.basename(f)}")
        print(s, os.path.basename(f), r, flush=True)
out["_summary"] = dict(parts=len(out), failing=bad); print("summary", out["_summary"]); G.save("print_check.json", out)
