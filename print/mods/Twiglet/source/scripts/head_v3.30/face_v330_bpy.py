"""v3.30 FACE edits in Blender 4.2 (bpy, EXACT booleans). Mike: 'make sure this is all done with blender'.
  blender -b -P blender/face_v330_bpy.py -- [--dz 4.0] [--no-save]
Inputs: blender/in_v329/*.stl + params.json (unchanged v3.29 parts + interface data, written by prep_face_inputs_v330.py).
Edits (all bpy):
 1. EYE BEZELS: round revolved rings, smaller dark disc (R_OUT 35.4 / window 29.8 / spigot 34.2), 4 mm lower (eye frame shifted -DZ in z).
 2. SNOUT: re-aimed yaw -4 / pitch +22 (v3.29 -12 / -6): revolved cone tube (OD 65 -> 72, 3 mm rounded mouth rim) + conical bore,
    flush to the ball; keyed spigot + flush plug on the UNCHANGED head_lower socket frame; minus bezel hulls, pod lift sweeps and the head-split lift cylinder.
 3. SHELLS: old eye facet / bore refilled (ball-wall cap, rho <= 49.5 about the v3.29 eye axis), then facet / blend / bore / ring pocket / grain rings /
    backing ring re-cut about the lowered eye frame (flat wood rim to rho 42, blend to 49). head_upper fill keeps 0.25 mm off head_lower.
 4. DISPLAY CARRIERS moved down DZ; their 2 M3 posts in head_lower shortened DZ with heat-set insert holes re-drilled; pod + bezel lift sweeps extended.
Outputs: blender/out_v330/*.stl, blender/out_v330/face_info.json, blender/head_v330.blend (collections v329_input / tools / v330)."""
import bpy, bmesh, json, math, os, sys, time
from mathutils import Vector, Matrix
A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d): return type(d)(A[A.index(k) + 1]) if k in A else d
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); BL = os.path.join(HERE, "blender")
IN = os.path.join(BL, "in_v329"); OUT = os.path.join(BL, "out_v330"); os.makedirs(OUT, exist_ok=True)
P = json.load(open(os.path.join(IN, "params.json")))
DZ = arg("--dz", 4.0); SOLVER = arg("--solver", "MANIFOLD" if bpy.app.version >= (4, 5, 0) else "EXACT")   # Blender 4.5 LTS: Manifold solver (robust + fast)
R_OUT, R_WIN, R_SPIG, R_BORE, RF, RB, R_PL, BACK_T, RING_H = 35.4, 29.8, 34.2, 34.5, 42.0, 49.0, 44.0, 4.6, 1.3   # BACK_T 4.6 (v3.15: 2.6): new backing ring swallows the old v3.29-axis one (no thin step)
C = Vector(P["C"]); Rb = P["Rb"]; ZS = P["zsplit"]; T0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def coll(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); return c
CIN, CT, CO = coll("v329_input"), coll("tools"), coll("v330")
def link(o, c):
    for c0 in list(o.users_collection): c0.objects.unlink(o)
    c.objects.link(o); return o
def log(*a): print(f"[{time.time() - T0:6.1f}s]", *a, flush=True)
def imp(name):
    bpy.ops.wm.stl_import(filepath=os.path.join(IN, name + ".stl")); o = bpy.context.selected_objects[0]; o.name = name + "_v329"
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(o.data); bm.free(); return link(o, CIN)
def obj_from_bm(name, bm, c=None):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); (c or CT).objects.link(o); return o
def dup(o, name, c=None, t=(0, 0, 0)):
    n = o.copy(); n.data = o.data.copy(); n.name = name; (c or CT).objects.link(n)
    n.data.transform(Matrix.Translation(Vector(t))); return n
def frame(ax):
    ax = Vector(ax).normalized(); u = ax.cross(Vector((0, 0, 1))).normalized(); v = ax.cross(u); return ax, u, v
def revolve(name, origin, ax, prof, n=128):
    """closed (rho, a) profile revolved about the axis through origin (manifold: on-axis points become single poles)"""
    ax, u, v = frame(ax); origin = Vector(origin); bm = bmesh.new(); rings = []
    for r, a in prof:
        if r < 1e-6: rings.append([bm.verts.new(origin + ax * a)])
        else: rings.append([bm.verts.new(origin + ax * a + r * (math.cos(t) * u + math.sin(t) * v)) for t in [2 * math.pi * i / n for i in range(n)]])
    m = len(rings)
    for i in range(m):
        A_, B_ = rings[i], rings[(i + 1) % m]
        if len(A_) == 1 and len(B_) == 1: continue
        for j in range(n):
            j2 = (j + 1) % n
            if len(A_) == 1: bm.faces.new((A_[0], B_[j], B_[j2]))
            elif len(B_) == 1: bm.faces.new((A_[j], B_[0], A_[j2]))
            else: bm.faces.new((A_[j], B_[j], B_[j2], A_[j2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); o = obj_from_bm(name, bm)
    return o
def ico(name, c, r, sub=7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r); bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c)); return obj_from_bm(name, bm)
def cyl(name, p0, p1, r, n=64):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()); bmesh.ops.rotate(bm, verts=bm.verts, matrix=q.to_matrix()); bmesh.ops.translate(bm, verts=bm.verts, vec=(p0 + p1) / 2)
    return obj_from_bm(name, bm)
def boxo(name, lo, hi, M=None):
    lo, hi = Vector(lo), Vector(hi); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=hi - lo, verts=bm.verts); bmesh.ops.translate(bm, verts=bm.verts, vec=(lo + hi) / 2)
    if M is not None: bm.transform(M)
    return obj_from_bm(name, bm)
def torus(name, R, r, origin, ax, nM=160, nm=10):
    ax, u, v = frame(ax); bm = bmesh.new(); V = []
    for i in range(nM):
        t = 2 * math.pi * i / nM; e = math.cos(t) * u + math.sin(t) * v
        V.append([bm.verts.new(Vector(origin) + e * (R + r * math.cos(2 * math.pi * k / nm)) + ax * (r * math.sin(2 * math.pi * k / nm))) for k in range(nm)])
    for i in range(nM):
        for k in range(nm): bm.faces.new((V[i][k], V[(i + 1) % nM][k], V[(i + 1) % nM][(k + 1) % nm], V[i][(k + 1) % nm]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return obj_from_bm(name, bm)
def hull(name, objs, scale=1.0, sweep=None):
    pts = []
    for o in objs: pts += [o.matrix_world @ vv.co for vv in o.data.vertices]
    if scale != 1.0:
        lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)]); c0 = (lo + hi) / 2
        pts = [c0 + (p - c0) * scale for p in pts]
    if sweep: pts = pts + [p + Vector(sweep) for p in pts]
    bm = bmesh.new(); vs = [bm.verts.new(p) for p in pts]; bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm)
def boolean(t, tools, op):
    tools = tools if isinstance(tools, (list, tuple)) else [tools]
    for tl in tools:
        md = t.modifiers.new("b", "BOOLEAN"); md.operation = op; md.solver = SOLVER; md.object = tl
        bpy.context.view_layer.objects.active = t; bpy.ops.object.modifier_apply(modifier=md.name)
    return t
def vol(o):
    bm = bmesh.new(); bm.from_mesh(o.data); v = bm.calc_volume(signed=False); bm.free(); return v
DROPPED = {}
def keep_largest(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); seen = set(); parts = []
    for f in bm.faces:
        if f.index in seen: continue
        stack = [f]; comp = []; seen.add(f.index)
        while stack:
            g = stack.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); stack.append(h)
        parts.append(comp)
    if len(parts) > 1:
        parts.sort(key=len); dead = [f for p in parts[:-1] for f in p]; DROPPED[o.name] = DROPPED.get(o.name, 0) + len(dead)
        bmesh.ops.delete(bm, geom=dead, context="FACES"); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data); bm.free(); return len(parts)
def half(k, g=0.0):
    return boxo("half_" + k, (C.x - 300, C.y - 300, ZS + g), (C.x + 300, C.y + 300, ZS + 600)) if k == "head_upper" else boxo("half_" + k, (C.x - 300, C.y - 300, ZS - 600), (C.x + 300, C.y + 300, ZS - g))
info = dict(DZ=DZ, R_OUT=R_OUT, R_WIN=R_WIN, RF=RF, RB=RB, solver=f"Blender {bpy.app.version_string} {SOLVER} boolean")
src = {k: imp(k) for k in ("head_upper", "head_lower", "eye_bezel_L", "eye_bezel_R", "display_carrier_L", "display_carrier_R", "snout")}
pods = {sd: [imp(f"pod_{sd}{i}") for i in range(4)] for sd in "LR"}
for sd in "LR":
    for p in pods[sd]: link(p, CT)
log("imported")
shift = Vector((0, 0, -DZ)); C2 = C + shift
A_F = math.sqrt(Rb ** 2 - R_PL ** 2); A_B = math.sqrt(Rb ** 2 - RB ** 2) - 0.2
ax_old, ax_new, e_new = {}, {}, {}
for sd in "LR":
    e0 = Vector(P["eye_centre_v329"][sd]); ax_old[sd] = (e0 - C).normalized(); e_new[sd] = e0 + shift; ax_new[sd] = (e_new[sd] - C2).normalized()
# ---- 1. bezels + carriers
out = {}
for sd in "LR":
    a_front = A_F + RING_H
    prof = [(R_WIN, A_F - 4.6), (R_SPIG, A_F - 4.6), (R_SPIG, A_F + 0.15), (R_OUT, A_F + 0.15), (R_OUT, a_front - 0.5), (R_OUT - 0.5, a_front), (R_WIN + 1.2, a_front), (R_WIN, a_front - 1.2)]
    out[f"eye_bezel_{sd}"] = link(revolve(f"eye_bezel_{sd}", C2, ax_new[sd], prof, n=192), CO)
    out[f"display_carrier_{sd}"] = dup(src[f"display_carrier_{sd}"], f"display_carrier_{sd}", CO, shift)
    info[sd] = dict(axis=[round(x, 4) for x in ax_new[sd]], centre=[round(x, 2) for x in e_new[sd]], eye_disc_d_mm=2 * R_OUT, window_d_mm=2 * R_WIN,
                    ring_width_mm=round(R_OUT - R_WIN, 1), wood_flat_rim_mm=round(RF - R_OUT, 1), facet_plane_a=round(A_F, 2), ring_front_a=round(a_front, 2))
log("bezels")
# ---- 2. snout
S_ = P["snout"]; P0 = Vector(S_["P0"]); w2 = Vector(S_["w"]); L, ed = S_["L"], S_["EDGE"]
r_out = lambda s: S_["OD0"] / 2 + (S_["OD1"] - S_["OD0"]) / 2 * s / L
prof = [(0, -45.0), (r_out(-45.0), -45.0)] + [(r_out(s), s) for s in [-40.0 + 2 * i for i in range(int((L - ed + 40) / 2) + 1) if -40.0 + 2 * i < L - ed]]
prof += [(r_out(L - ed) - ed + ed * math.cos(a), L - ed + ed * math.sin(a)) for a in [math.pi / 2 * i / 8 for i in range(1, 9)]] + [(0, L)]
tube = revolve("snout", P0, w2, prof, 180)
u2, v2 = Vector(S_["u"]), Vector(S_["v"])
def fillet_cone(f=S_["FIL"], N=180, K=8):
    """3 mm concave blend between the cone wall and the ball (per azimuth: circle tangent to the cone generatrix and the ball's tangent line)"""
    k = (S_["OD1"] - S_["OD0"]) / 2 / L; rings = [[] for _ in range(K + 4)]
    for i in range(N):
        ph = 2 * math.pi * i / N; e = math.cos(ph) * u2 + math.sin(ph) * v2
        g = lambda s: (P0 + r_out(s) * e + s * w2 - C).length - Rb
        a, b = -40.0, 40.0
        for _ in range(60):
            mid = 0.5 * (a + b)
            if g(mid) > 0: b = mid
            else: a = mid
        s0 = 0.5 * (a + b); X = P0 + r_out(s0) * e + s0 * w2; n = (X - C) / Rb
        m = n.dot(e) * e + n.dot(w2) * w2; m.normalize()
        dw = (w2 + k * e) / math.hypot(1, k); db = e - e.dot(m) * m; db.normalize()
        phi = math.acos(max(-1, min(1, dw.dot(db)))); t = f / math.tan(phi / 2)
        bis = (dw + db).normalized(); O = X + bis * f / math.sin(phi / 2); Tb, Tw = X + db * t, X + dw * t
        nw = e - e.dot(dw) * dw; nw.normalize()
        pts = [X - 3.0 * e - 6.0 * w2, Tb - 1.0 * m]; vs, vw = (Tb - O) / f, (Tw - O) / f; ang = math.acos(max(-1, min(1, vs.dot(vw))))
        for j in range(K + 1):
            q = j / K * ang; pts.append(O + f * (math.sin(ang - q) * vs + math.sin(q) * vw) / math.sin(ang))
        pts.append(Tw - 2.0 * nw)
        for j, p in enumerate(pts): rings[j].append(p)
    bm = bmesh.new(); V = [[bm.verts.new(p) for p in r] for r in rings]
    for r in range(len(V) - 1):
        for i in range(N): bm.faces.new((V[r][i], V[r][(i + 1) % N], V[r + 1][(i + 1) % N], V[r + 1][i]))
    for r in (0, len(V) - 1):
        c0 = bm.verts.new(sum((vv.co for vv in V[r]), Vector()) / N)
        for i in range(N): bm.faces.new((c0, V[r][(i + 1) % N], V[r][i]) if r == 0 else (c0, V[r][i], V[r][(i + 1) % N]))
    return obj_from_bm("snout_root_fillet", bm)
boolean(tube, fillet_cone(), "UNION")
ball15 = ico("ball_p015", C, Rb + 0.15, 7); boolean(tube, ball15, "DIFFERENCE")
rb = lambda s: S_["BORE_K"] * r_out(s); sb0 = L - S_["BORE_D"]
bprof = [(0, sb0 - 1.0), (rb(sb0) - 3.0, sb0)] + [(rb(s), s) for s in [sb0 + 4.0 + 2 * i for i in range(40) if sb0 + 4.0 + 2 * i < L - 1.6]]
bprof += [(rb(L - 1.6) + 1.6 - 1.6 * math.cos(a), L - 1.55 + 1.6 * math.sin(a)) for a in [math.pi / 2 * i / 6 for i in range(1, 7)]] + [(rb(L) + 1.6, L + 3.0), (0, L + 3.0)]
bore = revolve("snout_bore", P0, w2, bprof, 180)
M = Matrix(P["sock_M"]); RBs = P["SN_RB"]
def sock_cyl(name, z0, z1, r):
    o = cyl(name, (0, 0, z0), (0, 0, z1), r, 160); o.data.transform(M)
    if M.to_3x3().determinant() < 0: o.data.flip_normals()
    return o
spig = sock_cyl("spigot_plug", -11, 14, RBs + 2.1); boolean(spig, boxo("key", (RBs + 1.6, -1.8, -11), (RBs + 4.8, 1.8, 14), M), "UNION")   # keyed spigot + flush plug in one solid
boolean(spig, sock_cyl("spigot_bore", -20, -3.0, RBs), "DIFFERENCE")                                              # = v3.12 (spigot - bore) U plug(-3..14)
ballk = ico("ball_k", C, Rb + 0.17, 7); boolean(spig, ballk, "INTERSECT")
boolean(tube, spig, "UNION"); boolean(tube, bore, "DIFFERENCE")
import random; rnd = random.Random(7); gr = None; ng = 0                       # wood grain: 0.9 mm wide x 0.45 mm deep grooves along the cone (irregular spacing, broken lengths)
ph = 0.0
while ph < 2 * math.pi - 0.05:
    s_a = 6.0 + rnd.uniform(0, 10); s_b = L - 6.0 - rnd.uniform(0, 14)
    e = math.cos(ph) * u2 + math.sin(ph) * v2
    pa = P0 + w2 * s_a + e * (r_out(s_a) + 0.0); pb = P0 + w2 * s_b + e * (r_out(s_b) + 0.0)
    gcy = cyl(f"grain_{ng}", pa, pb, 0.45, 8)
    if gr is None: gr = gcy; gr.name = "snout_grain"
    else: boolean(gr, gcy, "UNION")
    ng += 1; ph += rnd.uniform(0.11, 0.21)
v_g0 = vol(tube); boolean(tube, gr, "DIFFERENCE"); grain_mm3 = v_g0 - vol(tube); v0 = vol(tube)
for sd in "LR": boolean(tube, hull(f"bezel_hull104_{sd}", [out[f"eye_bezel_{sd}"]], 1.04), "DIFFERENCE")
v1 = vol(tube)
for sd in "LR":
    for i, p in enumerate(pods[sd]): boolean(tube, hull(f"podsweep_{sd}{i}", [p], 1.0, (0, 0, 90.0)), "DIFFERENCE")      # pods (v3.29 position) lift out vertically
v2 = vol(tube)
rho_s = math.sqrt(Rb ** 2 - (ZS - C.z) ** 2) + 2.0
boolean(tube, cyl("lift_cyl", (C.x, C.y, ZS), (C.x, C.y, ZS + 150), rho_s, 256), "DIFFERENCE"); v3 = vol(tube)
nparts = keep_largest(tube); out["snout"] = link(tube, CO)
info["snout"] = dict(fillet_mm=S_["FIL"], grain_grooves=ng, grain_removed_mm3=round(grain_mm3, 1), axis_yaw_pitch=(S_["YAW"], S_["PITCH"]), L=L, OD_root=S_["OD0"], OD_mouth=S_["OD1"], T2=[round(x, 4) for x in w2], root=[round(x, 2) for x in P0],
                     bezel_cut_mm3=round(v0 - v1, 1), pod_sweep_cut_mm3=round(v1 - v2, 1), lift_clash_cut_mm3=round(v2 - v3, 1), volume_cm3=round(v3 / 1000, 1), parts_before_keep=nparts)
log("snout", info["snout"])
# ---- 3. shells
sn12 = hull("snout_hull112", [out["snout"]], 1.12); sn30 = hull("snout_hull130", [out["snout"]], 1.30)
shells = {k: dup(src[k], k, CO) for k in ("head_upper", "head_lower")}
for k in shells:
    for sd in "LR":
        n_ = 40; cap = [(0, Rb - 0.02)] + [(49.5 * i / n_, math.sqrt((Rb - 0.02) ** 2 - (49.5 * i / n_) ** 2)) for i in range(1, n_ + 1)]
        cap += [(49.5 * i / n_, math.sqrt((Rb - 3.2) ** 2 - (49.5 * i / n_) ** 2)) for i in range(n_, 0, -1)] + [(0, Rb - 3.2)]
        F = revolve(f"fill_{k}_{sd}", C, ax_old[sd], cap, 192)
        boolean(F, sn12, "DIFFERENCE"); boolean(F, half(k, 0.01), "INTERSECT")
        if k == "head_upper":
            for t in ((0, 0, 0.25), (0.25, 0, 0), (-0.25, 0, 0), (0, 0.25, 0), (0, -0.25, 0)): boolean(F, dup(shells["head_lower"], "hl_off", CT, t), "DIFFERENCE")
        info[f"fill_{k}_{sd}_cm3"] = round(vol(F) / 1000, 2)
        boolean(shells[k], F, "UNION")
    log("filled", k)
for sd in "LR":
    ax = ax_new[sd]
    cutter = revolve(f"facet_cutter_{sd}", C2, ax, [(0, A_F), (RF, A_F), (RB, A_B), (RB + 25, A_B + 30), (0, A_B + 30)], 192)
    def a_surf(r): return A_F if r <= RF else min(A_F + (A_B - A_F) * (r - RF) / (RB - RF), math.sqrt(Rb ** 2 - r ** 2))
    for i, r0 in enumerate((R_OUT + 1.6, R_OUT + 4.2, RF + 1.6, RB - 1.2)): boolean(cutter, torus(f"grain_ring_{sd}{i}", r0, 0.45, C2 + ax * a_surf(r0), ax), "UNION")
    boolean(cutter, sn30, "DIFFERENCE")
    bp = revolve(f"bore_{sd}", C2, ax, [(0, 80.0), (R_BORE, 80.0), (R_BORE, A_F + 5), (0, A_F + 5)], 192)
    boolean(bp, revolve(f"ring_pocket_{sd}", C2, ax, [(0, A_F), (R_OUT + 1.3, A_F), (R_OUT + 1.3, A_F + 30), (0, A_F + 30)], 192), "UNION")
    boolean(bp, sn12, "DIFFERENCE"); boolean(cutter, bp, "UNION"); cut_all = cutter; cut_all.name = f"eye_cut_all_{sd}"
    back = revolve(f"backing_{sd}", C2, ax, [(R_BORE - 0.5, A_F - BACK_T), (RB + 5.0, A_F - BACK_T - 2.0), (RB + 5.0, A_F + 3), (R_BORE - 0.5, A_F + 3)], 192)
    boolean(back, ico("ball_in", C, Rb - 0.4, 7), "INTERSECT"); boolean(back, sn12, "DIFFERENCE")
    for k in ("head_lower", "head_upper"):
        b_k = dup(back, f"backing_{sd}_{k}"); boolean(b_k, half(k, 0.01), "INTERSECT"); boolean(b_k, cut_all, "DIFFERENCE")
        if k == "head_upper":
            for t in ((0, 0, 0.25), (0, 0, -0.25)): boolean(b_k, dup(shells["head_lower"], "hl_off", CT, t), "DIFFERENCE")
        if len(b_k.data.polygons): boolean(shells[k], b_k, "UNION")
        boolean(shells[k], cut_all, "DIFFERENCE")
    log("eye recut", sd)
# ---- 4. carrier posts + lift sweeps (head_lower)
HL = shells["head_lower"]
for i, (x, y, zt) in enumerate(P["posts"]):
    boolean(HL, cyl(f"post_trim_{i}", (x, y, zt - DZ), (x, y, zt + 2.0), P["POST_R"] + 0.6, 48), "DIFFERENCE")
    boolean(HL, cyl(f"insert_{i}", (x, y, zt - DZ - P["POST_INS_D"]), (x, y, zt - DZ + 1.0), P["POST_INS_R"], 32), "DIFFERENCE")
for sd in "LR":
    for i, p in enumerate(pods[sd]):
        q = dup(p, f"pod_v330_{sd}{i}", CT, shift); boolean(HL, hull(f"pod_lift_{sd}{i}", [q], 1.0, (0, 0, DZ + 0.5)), "DIFFERENCE")
    bz = hull(f"bezel_lift_{sd}", [out[f"eye_bezel_{sd}"]], 1.006, (0, 0, 90.0)); boolean(bz, half("head_lower"), "INTERSECT"); boolean(HL, bz, "DIFFERENCE")
log("posts + sweeps")
for k in shells: info[k] = dict(parts_before_keep=keep_largest(shells[k]), vol_cm3=round(vol(shells[k]) / 1000, 1), v329_cm3=round(vol(src[k]) / 1000, 1)); out[k] = shells[k]
from mathutils import kdtree
def f32_separate(o, sep=3e-4, it=4):
    """STL is float32 and topology-free: vertices that coincide geometrically (touching sheets the solver keeps topologically apart) would be
    re-merged by any slicer -> 'kissing' non-manifold edges. Push each such vertex 'sep' mm inward along its own normal (sub-micron change)."""
    me = o.data; moved = 0
    for _ in range(it):
        me.update(); n = len(me.vertices); kd = kdtree.KDTree(n)
        for i, v in enumerate(me.vertices): kd.insert(v.co, i)
        kd.balance(); hit = set()
        for i, v in enumerate(me.vertices):
            for (co, j, d) in kd.find_range(v.co, sep * 0.5):
                if j != i: hit.add(i); hit.add(j)
        if not hit: break
        for i in hit: me.vertices[i].co -= me.vertices[i].normal * sep
        moved += len(hit)
    return moved
def nonman(o):
    bm = bmesh.new(); bm.from_mesh(o.data); n = sum(1 for e in bm.edges if not e.is_manifold); bm.free(); return n
info["f32_separated_verts"] = {k: f32_separate(o) for k, o in out.items()}; info["dropped_faces"] = DROPPED
info["nonmanifold_edges"] = {k: nonman(o) for k, o in out.items()}; log("nonmanifold", info["nonmanifold_edges"])
for k, o in out.items():
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT, k + ".stl"), export_selected_objects=True, ascii_format=False, apply_modifiers=True, global_scale=1.0, forward_axis="Y", up_axis="Z")
    o.select_set(False)
json.dump(info, open(os.path.join(OUT, "face_info.json"), "w"), indent=1)
CT.hide_viewport = True; CT.hide_render = True; CIN.hide_viewport = True
if "--no-save" not in A: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BL, "head_v330.blend"), compress=True)
log("FACE_OK", json.dumps(info))
