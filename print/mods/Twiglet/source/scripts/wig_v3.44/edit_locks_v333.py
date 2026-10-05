"""v3.33 lock editing IN BLENDER (headless): opens a lock-spine .blend (collection 'LockSpines', the v3.30 format: Bezier point co = spine point on
the wig seat, radius = half width, softbody weight = crest height), applies the edit table of a variant file, saves the edited .blend, then the
caller rebuilds the lock solids with build_wig_v333.py --from-blend <saved>.
  blender -b <in.blend> -P edit_locks_v333.py -- --variant variants/vX.py --save <out.blend>
Edit table (variant file defines EDITS = {lock-prefix: dict(...)}, NEW = [dict(...)], DROP = [prefix]):
  per point t in [0,1] (root -> tip):  th' = th0 + (th - th0) * ths + dth * t^tp ;  ph' = ph + dph * t^pp   (deg, about the wig centre C)
  then the point is re-seated on the v3.30 seat surface (seat_grid.json = hair_v330.seat_r), so the lock still sits on the same seat/flare.
  w: half-width x (w0 + (w1 - w0) t) ; h: crest x (h0 + (h1 - h0) t) ; npts: resample count ; tipw: min tip half-width (blunt end)
NEW locks: dict(name, th=[...], ph=[...], w=[half widths], h=[crests], lip, p_top, off) on the seat (Catmull-Rom'd by the builder)."""
import bpy, sys, os, json, math
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:]
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, arg("--grid", "seat_grid.json")))); TH = np.array(G["th"]); PH = np.array(G["ph"]); RR = np.array(G["r"]); C = np.array(bpy.context.scene["wig_C"])
def seat(th, ph):
    ph = (ph + 180.0) % 360.0 - 180.0; i = np.clip((th - TH[0]) / 1.0, 0, len(TH) - 1.001); j = np.clip((ph - PH[0]) / 2.0, 0, len(PH) - 1.001)
    i0, j0 = int(i), int(j); a, b = i - i0, j - j0
    return (RR[i0, j0] * (1 - a) * (1 - b) + RR[i0 + 1, j0] * a * (1 - b) + RR[i0, j0 + 1] * (1 - a) * b + RR[i0 + 1, j0 + 1] * a * b)
def sph(th, ph): t, p = math.radians(th), math.radians(ph); return np.array([math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t)])
def onseat(th, ph): return C + seat(th, ph) * sph(th, ph)
def thph(co): d = np.asarray(co) - C; r = np.linalg.norm(d); return math.degrees(math.acos(d[2] / r)), math.degrees(math.atan2(d[1], d[0]))
ns = {}; exec(open(arg("--variant")).read(), ns); EDITS = ns.get("EDITS", {}); NEW = ns.get("NEW", []); DROP = ns.get("DROP", [])
col = bpy.data.collections["LockSpines"]; log = []
def set_points(ob, rows):
    """rows: list of (co, radius, weight) -> rebuild the spline with AUTO handles"""
    cu = ob.data; cu.splines.clear(); sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(rows) - 1)
    for p, (c, r, w) in zip(sp.bezier_points, rows):
        p.co = tuple(c); p.handle_left_type = p.handle_right_type = "AUTO"; p.radius = float(r); p.weight_softbody = float(np.clip(w, 0.01, 100.0))
for ob in list(col.objects):
    if any(ob.name.startswith(d) for d in DROP): _nm = ob.name; bpy.data.objects.remove(ob); log.append(("drop", _nm)); continue
    key = [k for k in EDITS if ob.name.startswith(k)]
    if not key and not ns.get("RESEAT_ALL"): continue
    e = EDITS[key[0]] if key else {}; sp = ob.data.splines[0]; M = np.array(ob.matrix_world)
    co = np.array([(M @ np.r_[p.co[:3], 1.0])[:3] for p in sp.bezier_points]); r = np.array([p.radius for p in sp.bezier_points]); h = np.array([p.weight_softbody for p in sp.bezier_points])
    tp = np.array([thph(c) for c in co]); th, ph = tp[:, 0], np.unwrap(np.radians(tp[:, 1])) * 180 / math.pi
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(co, axis=0), axis=1))]; t = s / s[-1]
    th2 = th[0] + (th - th[0]) * e.get("ths", 1.0) + e.get("dth", 0.0) * t ** e.get("tp", 1.5)
    ph2 = ph + e.get("dph", 0.0) * t ** e.get("pp", 1.5) + e.get("ph_all", 0.0)
    w0, w1 = e.get("w", (1.0, 1.0)) if isinstance(e.get("w", 1.0), (tuple, list)) else (e.get("w", 1.0),) * 2
    h0, h1 = e.get("h", (1.0, 1.0)) if isinstance(e.get("h", 1.0), (tuple, list)) else (e.get("h", 1.0),) * 2
    r2 = r * (w0 + (w1 - w0) * t); h2 = h * (h0 + (h1 - h0) * t)
    if "tipw" in e: r2 = np.maximum(r2, e["tipw"] * np.clip((t - 0.5) * 2, 0, 1))
    rows = [(onseat(a, b) - np.array(M[:3, 3]), rr, hh) for a, b, rr, hh in zip(th2, ph2, r2, h2)]
    set_points(ob, rows); log.append(("edit", ob.name, round(float(th2[-1]), 1), round(float(ph2[-1]), 1)))
for nl in NEW:
    th, ph = np.asarray(nl["th"], float), np.asarray(nl["ph"], float)
    cu = bpy.data.curves.new(nl["name"], "CURVE"); cu.dimensions = "3D"; ob = bpy.data.objects.new(nl["name"], cu); col.objects.link(ob)
    ob["lip"] = nl.get("lip", 2.0); ob["p_top"] = nl.get("p_top", 1.4); ob["off"] = nl.get("off", 0.0)
    set_points(ob, [(onseat(a, b), rr, hh) for a, b, rr, hh in zip(th, ph, nl["w"], nl["h"])]); log.append(("new", nl["name"]))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(arg("--save")), compress=True)
print("EDIT_OK", json.dumps(log))
