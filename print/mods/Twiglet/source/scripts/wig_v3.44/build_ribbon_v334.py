"""v3.34 RIBBON wig builder (+ split sub-locks, pointed tips, layer steps; see loft()). v3.33 RIBBON wig builder (flat felt sections with turns; derived from the v3.30 builder). Each lock = a FLAT RIBBON (wide, TK-mm blade,
slight centre fold), twisted about its spine (tw0 -> tw1 deg, root -> tip), lifted so the low edge stays on the seat, bonded to the seat by a narrow keel.
Per-lock overrides via --ovr snippet: s['tw0'], s['tw1'], s['twp'], s['crease'], s['tk'], s['keel'], s['liftk'].
Original docstring:
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
         FACES=int(arg("--faces", 700000)), ARM_H=float(arg("--armh", 0.55)), ARM_PH=(66.0, 106.0), ARM_TH=(56.0, 70.0), HS=float(arg("--hs", 0.8)), WS=float(arg("--ws", 1.15)),
         TK=float(arg("--tk", 2.6)), TW=float(arg("--twist", 30.0)), CREASE=float(arg("--crease", 10.0)), KEEL=float(arg("--keel", 0.3)), LIFTK=float(arg("--liftk", 0.8)), NSEG=int(arg("--nseg", 6)), CLOSE=float(arg("--close", 0.0)), LENS=float(arg("--lens", 0.62)), LIPMIN=float(arg("--lipmin", 0.0)), SEATGRID=arg("--seatgrid"), PT=int(arg("--pt", 0)), PTE=float(arg("--pte", 2.5)), TIPW=float(arg("--tipw", 1.6)))
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
_SG = {}
def seat_lookup(C, X):
    """bilinear seat radius (seat grid json: th 0..180 x ph -180..180) at the directions of points X (n x 3)"""
    if not G["SEATGRID"]: return None
    if "r" not in _SG:
        J = json.load(open(os.path.join(HERE, G["SEATGRID"]))); _SG.update(th=np.array(J["th"]), ph=np.array(J["ph"]), r=np.array(J["r"]))
    d = X - C; rr = np.linalg.norm(d, axis=1); th = np.degrees(np.arccos(np.clip(d[:, 2] / rr, -1, 1))); ph = np.degrees(np.arctan2(d[:, 1], d[:, 0]))
    T, P_, R = _SG["th"], _SG["ph"], _SG["r"]
    fi = np.clip((th - T[0]) / (T[1] - T[0]), 0, len(T) - 1.001); fj = np.clip((ph - P_[0]) / (P_[1] - P_[0]), 0, len(P_) - 1.001)
    i0, j0 = fi.astype(int), fj.astype(int); a, b = fi - i0, fj - j0
    rs = R[i0, j0] * (1 - a) * (1 - b) + R[i0 + 1, j0] * a * (1 - b) + R[i0, j0 + 1] * (1 - a) * b + R[i0 + 1, j0 + 1] * a * b
    return rr, rs
def ribbon_section(hw, hc, tk, tau, crease, keel, depth, n):
    """closed CCW polygon (lat, up) with a fixed vertex count: flat blade (half-width hw, thickness tk, centre fold `crease` deg, rounded edges)
    rotated by tau about its centre (0, hc), + a keel (half-width keel*hw) from the blade underside down to -depth"""
    k = max(n // 10, 3); cr = math.tan(math.radians(crease) / 2)
    def blade(lat, side):                                      # side +1 top face, -1 underside (mid-surface fold + thickness)
        m = hc - cr * np.abs(lat)                              # fold: centre high, edges low (roof-like flat facets)
        tl = tk * (G.get("LENS_CUR", G["LENS"]) + (1 - G.get("LENS_CUR", G["LENS"])) * np.sqrt(np.clip(1 - (lat / hw) ** 2, 0, 1)))   # lens: edges >= 0.62 tk
        return m + side * tl / 2
    kw = max(keel * hw, 1.2)
    # vertex budget: top 3k, right edge k, underside right k, keel right k, keel bottom 0 (shared), keel left k, underside left k, left edge k  -> 9k? use n = 9k
    lat_top = np.linspace(hw, -hw, 3 * k, endpoint=False)
    P = [(x, blade(x, 1)) for x in lat_top]
    a = np.linspace(math.pi / 2, 3 * math.pi / 2, k, endpoint=False)               # left rounded edge
    yc = blade(-hw, 0) if False else hc - cr * hw; te = tk * G.get("LENS_CUR", G["LENS"]) / 2
    P += [(-hw + te * 0.9 * math.cos(t), yc + te * math.sin(t)) for t in a]
    lu = np.linspace(-hw, -kw, k, endpoint=False); P += [(x, blade(x, -1)) for x in lu]   # underside left
    yk = blade(-kw, -1); zz = np.linspace(yk, -depth, k, endpoint=False); P += [(-kw, z) for z in zz]   # keel left
    P += [(-kw + 2 * kw * t, -depth) for t in np.linspace(0, 1, k, endpoint=False)]   # keel bottom
    zz = np.linspace(-depth, blade(kw, -1), k, endpoint=False); P += [(kw, z) for z in zz]   # keel right
    ru = np.linspace(kw, hw, k, endpoint=False); P += [(x, blade(x, -1)) for x in ru]     # underside right
    a = np.linspace(-math.pi / 2, math.pi / 2, k, endpoint=False); P += [(hw + te * 0.9 * math.cos(t), yc + te * math.sin(t)) for t in a]
    P = np.array(P, float)
    # twist the blade part about (0, hc); the keel's lower end stays at -depth (shear the keel so it meets the rotated blade)
    c, s_ = math.cos(math.radians(tau)), math.sin(math.radians(tau))
    blade_pts = P[:, 1] > -depth + 1e-6
    lat, up = P[:, 0], P[:, 1] - hc
    lat2, up2 = lat * c - up * s_, lat * s_ + up * c
    w = np.clip((P[:, 1] - (-depth)) / max(hc - (-depth), 1e-6), 0, 1) ** 2         # keel: blend from un-rotated (bottom) to rotated (top)
    out = np.c_[lat * (1 - w) + lat2 * w, (up * (1 - w) + up2 * w) + hc]
    return out
def loft(C, s):
    """v3.34: one spine -> one or more flat ribbons ("split": narrower sub-locks side by side, each its own length, twist, pointed tip and
    layer lift = stepped overlap with a shadow line); s['lift'] = extra mm for the whole lock (layer order between locks)."""
    A = catmull(np.c_[s["co"], s["r"] * G["WS"], np.maximum(s["h"] * G["HS"], s["lip"] + 0.3)], G["NT"]); B0, hw0, H0 = A[:, :3], np.maximum(A[:, 3], 1.6), A[:, 4]
    T0 = np.gradient(B0, axis=0); T0 /= np.linalg.norm(T0, axis=1)[:, None]; N0 = B0 - C; N0 -= (N0 * T0).sum(1)[:, None] * T0; N0 /= np.linalg.norm(N0, axis=1)[:, None]; L0 = np.cross(N0, T0)
    subs = s.get("subs") or [dict(c=0.0, w=1.0, len=1.0, tw=1.0, lift=0.0)]
    obs = []
    for js, sb in enumerate(subs):
        nt0 = len(B0); t0 = np.linspace(0, 1, nt0); ntj = max(int(round(nt0 * sb.get("len", 1.0))), 8)
        B, hwb, H, T, N, L = B0[:ntj], hw0[:ntj], H0[:ntj], T0[:ntj], N0[:ntj], L0[:ntj]; t = t0[:ntj] / t0[ntj - 1]
        pt = sb.get("pt", s.get("pt", G["PT"]))                                   # pointed tip: width x (1 - u^PTE)^0.5 over the last part
        pte = sb.get("pte", s.get("pte", G["PTE"]))                               # per-sub / per-lock point exponent (higher = point only at the very end)
        prof = np.clip(1 - t ** pte, 0, 1) ** sb.get("ptp", s.get("ptp", 0.5)) if pt else np.ones_like(t)   # v3.42: per-lock profile power ptp (0.5 = round-shouldered point, 1 = long straight-sided triangular taper)
        hw = np.maximum(hwb * sb.get("w", 1.0) * np.maximum(prof, 0.0), G["TIPW"])
        B = B + L * ((sb.get("c", 0.0) + sb.get("fan", 0.0) * t ** 1.5) * hwb)[:, None]   # lateral offset (fraction of the parent half-width); fan = extra offset growing to the tip (locks diverge)
        G["LENS_CUR"] = s.get("lens", G["LENS"])   # v3.39: per-lock lens (edge/centre thickness ratio; lower = rounder pillow section); default = global
        tk = s.get("tk", G["TK"]); tw0, tw1, twp = s.get("tw0", 0.0), s.get("tw1", s.get("tw_sign", 1.0) * G["TW"]), s.get("twp", 1.3)
        tw1 = tw1 * sb.get("tw", 1.0); tw0 = tw0 * sb.get("tw", 1.0)
        crease, keel, liftk = s.get("crease", G["CREASE"]), s.get("keel", G["KEEL"]), s.get("liftk", G["LIFTK"])
        lift = s.get("lift", 0.0) + sb.get("lift", 0.0)
        n = 9 * max(G["NA"] // 8, 3); V = []; nt = len(B)
        for i in range(nt):
            tau = tw0 + (tw1 - tw0) * t[i] ** twp
            hwi = hw[i]; cr = math.tan(math.radians(crease) / 2)
            hc = max(liftk * H[i] - tk / 2, tk / 2 + 0.2 + cr * hwi)
            hc = max(hc, tk / 2 + 0.3 + hwi * abs(math.sin(math.radians(tau))) * 0.9 + cr * hwi)
            if G["LIPMIN"] > 0:
                te = tk * G.get("LENS_CUR", G["LENS"]) / 2; hc = max(hc, G["LIPMIN"] + te + hwi * abs(math.sin(math.radians(tau))) + cr * hwi * math.cos(math.radians(tau)))
            hc += lift * min(1.0, t[i] / 0.25)                                       # layer step (eased in from the root)
            hc += (sb.get("flick", s.get("flick", 0.0))) * max(0.0, (t[i] - 0.55) / 0.45) ** 2   # v3.37: tip flick = radial lift growing over the last 45 % (felt blade tips curling outward); default 0
            P = ribbon_section(hwi, hc, tk, tau, crease, keel, G["DEPTH"], n)
            if G["SEATGRID"] and G["LIPMIN"] > 0:
                k_ = max(n // 10, 3); under = np.r_[np.arange(3 * k_, 5 * k_), np.arange(8 * k_, 10 * k_)]
                for _it in range(3):
                    X = B[i] + L[i] * P[under, 0:1] + N[i] * P[under, 1:2]; rr, rs = seat_lookup(C, X); deficit = float(np.max(rs + G["LIPMIN"] - rr))
                    if deficit <= 0.05: break
                    hc += deficit * 1.05; P = ribbon_section(hwi, hc, tk, tau, crease, keel, G["DEPTH"], n)
            V += list(B[i] + L[i] * P[:, 0:1] + N[i] * P[:, 1:2])
        hc_end = hc if G["LIPMIN"] > 0 else 0.3 * H[-1]
        na = len(P); V += [B[0] + N[0] * 0.3 * H[0] - T[0] * 0.5 * hw[0], B[-1] + N[-1] * hc_end + T[-1] * 0.6 * hw[-1]]
        F = [(i * na + j, i * na + (j + 1) % na, (i + 1) * na + (j + 1) % na, (i + 1) * na + j) for i in range(nt - 1) for j in range(na)]
        c0, c1 = nt * na, nt * na + 1; F += [(c0, (j + 1) % na, j) for j in range(na)] + [(c1, (nt - 1) * na + j, (nt - 1) * na + (j + 1) % na) for j in range(na)]
        me = bpy.data.meshes.new(s["name"] + f"_m{js}"); me.from_pydata([tuple(v) for v in V], [], F); me.update(); me.validate()
        ob = bpy.data.objects.new(s["name"] + f"_solid{js}", me); bpy.context.scene.collection.objects.link(ob); obs.append(ob)
    return obs
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
sol = [o for s in SP for o in loft(C, s)]
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
if G["CLOSE"] > 0:                                                            # morphological closing (dilate -> voxel union -> erode): fills the thin slits where ribbon edges overlap
    for sgn in (1.0, -1.0):
        m = W.modifiers.new("cl", "DISPLACE"); m.direction = "NORMAL"; m.strength = sgn * G["CLOSE"]; m.mid_level = 0.0; bpy.ops.object.modifier_apply(modifier="cl")
        W.data.remesh_voxel_size = G["VOXEL"]; bpy.ops.object.voxel_remesh()
    print("closed", G["CLOSE"], len(W.data.polygons), flush=True)
for k in range(G["SM_IT"]):                                                   # Taubin lambda/mu smoothing as alternating Smooth modifiers (no shrink, fast)
    for nm, fac in (("sm_a", G["SM_LAMBDA"]), ("sm_b", -G["SM_LAMBDA"] - 0.03)):
        m = W.modifiers.new(nm, "SMOOTH"); m.factor = fac; m.iterations = 1; bpy.ops.object.modifier_apply(modifier=nm)
print("smoothed", flush=True); nf = len(W.data.polygons)
NOTCH = globals().get("NOTCH", [])                                           # v3.41: V-notches between fringe tips (set by the variant .rib.py): each = a spherical
for k_, nt_ in enumerate(NOTCH):                                               # polygon (th, ph) about C, swept radially r 60..200 -> closed frustum, EXACT boolean DIFFERENCE
    pts_ = [np.radians(p_) for p_ in nt_["poly"]]; ring_ = []
    for a_, b_ in zip(pts_, pts_[1:] + pts_[:1]):
        da_ = np.array([math.sin(a_[0]) * math.cos(a_[1]), math.sin(a_[0]) * math.sin(a_[1]), math.cos(a_[0])]); db_ = np.array([math.sin(b_[0]) * math.cos(b_[1]), math.sin(b_[0]) * math.sin(b_[1]), math.cos(b_[0])])
        om_ = math.acos(np.clip(da_ @ db_, -1, 1))
        for u_ in np.linspace(0, 1, 8, endpoint=False): ring_.append((math.sin((1 - u_) * om_) * da_ + math.sin(u_ * om_) * db_) / max(math.sin(om_), 1e-9))
    n_ = len(ring_); Vc_ = [tuple(C + 60.0 * d_) for d_ in ring_] + [tuple(C + 200.0 * d_) for d_ in ring_]
    if "ax" in nt_:                                                            # view-aligned notch: the polygon on the r = R0 sphere extruded along a fixed axis (e.g. +x = forward)
        ax_ = np.array(nt_["ax"], float); ax_ /= np.linalg.norm(ax_); r0_ = nt_.get("r0", 104.0); b0_, b1_ = nt_.get("back", 15.0), nt_.get("fwd", 60.0)
        Vc_ = [tuple(C + r0_ * d_ - b0_ * ax_) for d_ in ring_] + [tuple(C + r0_ * d_ + b1_ * ax_) for d_ in ring_]
    Fc_ = [tuple(range(n_ - 1, -1, -1)), tuple(range(n_, 2 * n_))] + [(j_, (j_ + 1) % n_, n_ + (j_ + 1) % n_, n_ + j_) for j_ in range(n_)]
    mc_ = bpy.data.meshes.new(f"notch{k_}"); mc_.from_pydata(Vc_, [], Fc_); mc_.update(); mc_.validate(); oc_ = bpy.data.objects.new(f"NOTCH_{k_}", mc_); bpy.context.scene.collection.objects.link(oc_)
    if nt_.get("both") and "ax" in nt_:                                        # one cutter = convex hull of the view-aligned prism AND the radial frustum (r 60..200) of the polygon
        bmh_ = bmesh.new(); [bmh_.verts.new(v_) for v_ in Vc_ + [tuple(C + nt_.get("rr", (95.0, 125.0))[0] * d_) for d_ in ring_] + [tuple(C + nt_.get("rr", (95.0, 125.0))[1] * d_) for d_ in ring_]]
        bmesh.ops.convex_hull(bmh_, input=list(bmh_.verts)); bmh_.to_mesh(mc_); bmh_.free(); mc_.update()
    bpy.context.view_layer.objects.active = oc_; bpy.ops.object.select_all(action="DESELECT"); oc_.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    bm_ = W.modifiers.new(f"notch{k_}", "BOOLEAN"); bm_.operation = "DIFFERENCE"; bm_.solver = "EXACT"; bm_.object = oc_
    bpy.context.view_layer.objects.active = W; bpy.ops.object.modifier_apply(modifier=bm_.name); oc_.hide_set(True); oc_.hide_render = True
    print("notch", k_, nt_.get("name", ""), len(W.data.polygons), flush=True)
if NOTCH:                                                                      # re-voxelise (watertight, manifold again after the booleans; edges rounded ~0.35 mm) + light Taubin
    W.data.remesh_voxel_size = G["VOXEL"]; W.data.remesh_voxel_adaptivity = 0.0; bpy.context.view_layer.objects.active = W; bpy.ops.object.voxel_remesh()
    if G.get("NOTCH_OPEN", 0) > 0:                                             # morphological OPENING (erode -> voxel -> dilate -> voxel): the knife-edge wedges where an inclined notch wall
        for sgn in (-1.0, 1.0):                                                # meets a lock surface (< 2 x OPEN thick) are trimmed back to a blunt >= ~2 x OPEN edge
            m = W.modifiers.new("op", "DISPLACE"); m.direction = "NORMAL"; m.strength = sgn * G["NOTCH_OPEN"]; m.mid_level = 0.0; bpy.ops.object.modifier_apply(modifier="op")
            W.data.remesh_voxel_size = G["VOXEL"]; bpy.ops.object.voxel_remesh()
        print("opened", G["NOTCH_OPEN"], len(W.data.polygons), flush=True)
    for k in range(G.get("NOTCH_SM", 3)):
        for nm, fac in (("sm_a", G["SM_LAMBDA"]), ("sm_b", -G["SM_LAMBDA"] - 0.03)):
            m = W.modifiers.new(nm, "SMOOTH"); m.factor = fac; m.iterations = 1; bpy.ops.object.modifier_apply(modifier=nm)
    nf = len(W.data.polygons); print("notched + remeshed", nf, flush=True)
if nf > G["FACES"]:
    d = W.modifiers.new("dec", "DECIMATE"); d.ratio = G["FACES"] / nf; bpy.ops.object.modifier_apply(modifier="dec")
bpy.ops.object.select_all(action="DESELECT"); W.select_set(True); bpy.context.view_layer.objects.active = W
bpy.ops.wm.stl_export(filepath=OUT, export_selected_objects=True, apply_modifiers=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
print("WIG_OK", OUT, "faces", len(W.data.polygons), "remesh faces", nf, json.dumps(G))
