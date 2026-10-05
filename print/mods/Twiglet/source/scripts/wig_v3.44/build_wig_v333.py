"""v3.30 Blender wig builder (run headless):
  blender -b -P blender/build_wig_v330.py -- [--from-blend blender/wig_v330.blend] [--json blender/locks_v330.json]
Each lock = one Bezier spine curve object 'L<ii> <name>' in collection 'LockSpines' (the editable source):
  control point co  = spine point ON the wig seat (mm, model frame; x forward, y robot's left, z up)
  point radius      = HALF-width of the lock there (mm)
  point weight (Softbody 'Weight' in the N panel) = crest height above the seat (mm)
  object custom props: lip (mm, vertical side wall before the rounded top), p_top (section superellipse exponent), off (crest lean -0.7..0.7)
Build: each spine -> Catmull-Rom resample (NT rings) -> lofted section (rounded superellipse top on a LIP-mm near-vertical side wall, buried DEPTH mm
under the seat) -> all locks joined -> voxel remesh (union, VOXEL mm) -> volume-preserving Laplacian smooth (soft partings, no creases)
-> decimate -> blender/wig_locks_v330.stl (+ wig_v330.blend saved with spines + result). The seat/crown/pins/key/hat band are added in hair_v330.wig()."""
import bpy, bmesh, sys, os, json, math
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
HERE = os.path.dirname(os.path.abspath(__file__))
JS = arg("--json", os.path.join(HERE, "locks_v330.json")); FROM = arg("--from-blend"); OUT = arg("--out", os.path.join(HERE, "wig_locks_v333.stl"))
BLEND = arg("--blend", os.path.join(HERE, "hair_v333_locks.blend"))
G = dict(NT=int(arg("--nt", 96)), NA=int(arg("--na", 32)), SUBD=int(arg("--subd", 2)), DEPTH=4.0, LIP=2.0, P_TOP=float(arg("--ptop", 1.4)), P_BOT=6.0, VOXEL=float(arg("--voxel", 0.7)), SM_LAMBDA=float(arg("--lam", 0.5)), SM_IT=int(arg("--it", 20)),
         FACES=int(arg("--faces", 700000)), ARM_H=float(arg("--armh", 0.55)), ARM_PH=(66.0, 106.0), ARM_TH=(56.0, 70.0), HS=float(arg("--hs", 0.8)), WS=float(arg("--ws", 1.15)))
OVR = arg("--ovr")                     # optional python snippet (variant hook) executed after the spines are read: edit SP (list of dicts) / G
def catmull(Pts, n):
    """centripetal Catmull-Rom through the control rows Pts (k x d) -> n rows (first 3 columns used for the parametrisation)"""
    P = np.asarray(Pts, float); k = len(P); P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    d = np.linalg.norm(np.diff(P[:, :3], axis=0), axis=1) ** 0.5; tk = np.r_[0, np.cumsum(np.maximum(d, 1e-6))]
    s = np.linspace(tk[1], tk[k], n); out = []
    for u in s:
        i = min(max(np.searchsorted(tk, u) - 1, 1), k - 1); t0, t1, t2, t3 = tk[i - 1:i + 3]; p0, p1, p2, p3 = P[i - 1:i + 3]
        a1 = (t1 - u) / (t1 - t0) * p0 + (u - t0) / (t1 - t0) * p1; a2 = (t2 - u) / (t2 - t1) * p1 + (u - t1) / (t2 - t1) * p2; a3 = (t3 - u) / (t3 - t2) * p2 + (u - t2) / (t3 - t2) * p3
        b1 = (t2 - u) / (t2 - t0) * a1 + (u - t0) / (t2 - t0) * a2; b2 = (t3 - u) / (t3 - t1) * a2 + (u - t1) / (t3 - t1) * a3
        out.append((t2 - u) / (t2 - t1) * b1 + (u - t1) / (t2 - t1) * b2)
    return np.array(out)
def spines_from_json(js):
    D = json.load(open(js)); C = np.array(D["C"]); SP = []
    for lk in D["locks"]:
        B, W, H = np.array(lk["B"]), np.array(lk["W"]), np.array(lk["H"]); n = len(B)
        idx = sorted(set(list(range(0, n - 6, 3)) + list(range(n - 6, n))))                     # ~18 control points, denser at the tip (round end)
        SP.append(dict(name="L%02d %s" % (lk["i"], lk["name"]), co=B[idx], r=W[idx] / 2, h=H[idx], lip=G["LIP"], p_top=G["P_TOP"], off=float(lk.get("off", 0.0))))
    return C, SP
def spines_from_blend():
    C = np.array(bpy.context.scene["wig_C"]); SP = []
    for ob in sorted(bpy.data.collections["LockSpines"].objects, key=lambda o: o.name):
        sp = ob.data.splines[0]; M = np.array(ob.matrix_world)
        co = np.array([(M @ np.r_[p.co[:3], 1.0])[:3] for p in sp.bezier_points]); r = np.array([p.radius for p in sp.bezier_points]); h = np.array([p.weight_softbody for p in sp.bezier_points])
        SP.append(dict(name=ob.name, co=co, r=r, h=h, lip=ob.get("lip", G["LIP"]), p_top=ob.get("p_top", G["P_TOP"]), off=ob.get("off", 0.0)))
    return C, SP
def make_spine_objects(C, SP):
    col = bpy.data.collections.get("LockSpines") or bpy.data.collections.new("LockSpines")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects): bpy.data.objects.remove(ob)
    for s in SP:
        cu = bpy.data.curves.new(s["name"], "CURVE"); cu.dimensions = "3D"; sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(s["co"]) - 1)
        for p, c, r, h in zip(sp.bezier_points, s["co"], s["r"], s["h"]):
            p.co = c; p.handle_left_type = p.handle_right_type = "AUTO"; p.radius = float(r); p.weight_softbody = float(np.clip(h, 0.01, 100.0))
        ob = bpy.data.objects.new(s["name"], cu); ob["lip"] = s["lip"]; ob["p_top"] = s["p_top"]; ob["off"] = s["off"]; col.objects.link(ob)
    bpy.context.scene["wig_C"] = list(map(float, C))
def loft(C, s):
    A = catmull(np.c_[s["co"], s["r"] * G["WS"], np.maximum(s["h"] * G["HS"], s["lip"] + 0.3)], G["NT"]); B, hw, H = A[:, :3], np.maximum(A[:, 3], 1.6), A[:, 4]
    T = np.gradient(B, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = B - C; N -= (N * T).sum(1)[:, None] * T; N /= np.linalg.norm(N, axis=1)[:, None]; L = np.cross(N, T)
    a = np.linspace(0, 2 * math.pi, G["NA"], endpoint=False); x, y = np.cos(a), np.sin(a); V = []
    for i in range(len(B)):
        top = y >= 0; pe = np.where(top, s["p_top"], G["P_BOT"])
        X = np.sign(x) * np.abs(x) ** (2 / pe); Y = np.sign(y) * np.abs(y) ** (2 / pe)
        lip = min(s["lip"], 0.6 * H[i]); up = np.where(top, lip + (H[i] - lip) * Y, lip + (lip + G["DEPTH"]) * Y)
        lat = X * hw[i] + s["off"] * hw[i] * 0.4 * np.clip(Y, 0, 1) * (1 - X * X)
        V += list(B[i] + L[i] * lat[:, None] + N[i] * up[:, None])
    na, nt = G["NA"], len(B); V += [B[0] + N[0] * 0.5 * H[0] - T[0] * 0.5 * hw[0], B[-1] + N[-1] * 0.5 * H[-1] + T[-1] * 0.6 * hw[-1]]
    F = [(i * na + j, i * na + (j + 1) % na, (i + 1) * na + (j + 1) % na, (i + 1) * na + j) for i in range(nt - 1) for j in range(na)]
    c0, c1 = nt * na, nt * na + 1; F += [(c0, (j + 1) % na, j) for j in range(na)] + [(c1, (nt - 1) * na + j, (nt - 1) * na + (j + 1) % na) for j in range(na)]
    me = bpy.data.meshes.new(s["name"] + "_m"); me.from_pydata([tuple(v) for v in V], [], F); me.update(); me.validate()
    ob = bpy.data.objects.new(s["name"] + "_solid", me); bpy.context.scene.collection.objects.link(ob); return ob
if FROM: bpy.ops.wm.open_mainfile(filepath=FROM); C, SP = spines_from_blend()
else:
    bpy.ops.wm.read_factory_settings(use_empty=True); C, SP = spines_from_json(JS); make_spine_objects(C, SP)
for s in SP:                                                                      # arm relief: crest heights eased down (smoothly) where the raised forearms pass the head sides
    d = s["co"] - C; th = np.degrees(np.arccos(d[:, 2] / np.linalg.norm(d, axis=1))); aph = np.abs(np.degrees(np.arctan2(d[:, 1], d[:, 0])))
    ss = lambda u: (lambda c: c * c * (3 - 2 * c))(np.clip(u, 0, 1))
    zp = ss((aph - G["ARM_PH"][0]) / 8.0) * ss((G["ARM_PH"][1] - aph) / 8.0); zt = ss((th - G["ARM_TH"][0]) / (G["ARM_TH"][1] - G["ARM_TH"][0]))
    s["h"] = s["h"] * (1 - (1 - G["ARM_H"]) * zp * zt)
TWEAK = {"L00": dict(h=1.12), "L01": dict(h=1.12), "L02": dict(h=1.12), "L03": dict(h=1.12), "L04": dict(h=1.12), "L15": dict(h=1.12), "L16": dict(h=1.12),   # v3.30 per-lock tweaks:
         "L13": dict(r=0.8), "L14": dict(r=0.8)}            # fringe / front-side / temple layers fuller (x1.12 crest), sideburns narrower (x0.8 width, clear of the raised forearms)
if "--no-tweak" not in argv:
    for s in SP:
        tw = TWEAK.get(s["name"][:3], {}); s["h"] = s["h"] * tw.get("h", 1.0); s["r"] = s["r"] * tw.get("r", 1.0)
if OVR: exec(open(OVR).read())
for ob in [o for o in bpy.data.objects if o.name.startswith("WIG")]: bpy.data.objects.remove(ob)
sol = [loft(C, s) for s in SP]
for o in sol:                                                                     # Catmull-Clark subdivision of every lofted lock -> smooth, facet-free surfaces before the union
    if G["SUBD"] > 0:
        m = o.modifiers.new("subd", "SUBSURF"); m.levels = m.render_levels = G["SUBD"]
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="subd")
bpy.ops.object.select_all(action="DESELECT")
for o in sol: o.select_set(True)
bpy.context.view_layer.objects.active = sol[0]; bpy.ops.object.join(); W = bpy.context.view_layer.objects.active; W.name = "WIG_locks"
# make every lock's normals point outward before the remesh (the voxel remesher unions the closed solids)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
print("joined", len(W.data.polygons), flush=True)
W.data.remesh_voxel_size = G["VOXEL"]; W.data.remesh_voxel_adaptivity = 0.0; bpy.ops.object.voxel_remesh()
print("remeshed", len(W.data.polygons), flush=True)
for k in range(G["SM_IT"]):                                                   # Taubin lambda/mu smoothing as alternating Smooth modifiers (no shrink, fast)
    for nm, fac in (("sm_a", G["SM_LAMBDA"]), ("sm_b", -G["SM_LAMBDA"] - 0.03)):
        m = W.modifiers.new(nm, "SMOOTH"); m.factor = fac; m.iterations = 1; bpy.ops.object.modifier_apply(modifier=nm)
print("smoothed", flush=True); nf = len(W.data.polygons)
if nf > G["FACES"]:
    d = W.modifiers.new("dec", "DECIMATE"); d.ratio = G["FACES"] / nf; bpy.ops.object.modifier_apply(modifier="dec")
bpy.ops.object.select_all(action="DESELECT"); W.select_set(True); bpy.context.view_layer.objects.active = W
bpy.ops.wm.stl_export(filepath=OUT, export_selected_objects=True, apply_modifiers=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
print("WIG_OK", OUT, "faces", len(W.data.polygons), "remesh faces", nf, json.dumps(G))
