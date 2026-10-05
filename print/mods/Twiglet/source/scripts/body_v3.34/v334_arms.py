"""v3.34 arms = v3.33 arms (v333h recipe) with a BIGGER hollow FEETECH box: BOX_H 44 -> 58 (along the forearm, photo ~62), +BXD per side in x
(depth 29 -> ~36), walls W 1.6, open bottom.  blender -b body_v334.blend -P v334_arms.py.  (v3.33 doc follows)
 Photo look: WOOD upper-arm / forearm blocks, small black joints,
black FEETECH-style gripper box, two long parallel prongs, black cable loop, vines + leaves.
 - shoulder_sleeve / elbow_sleeve: rev C sleeve + fused wood jacket (+TJ on the front/back faces, +TO on the outer face, 1.2 mm rounded) with
   0.5 mm wood-grain grooves; printed wood (were black).  upper_arm / forearm brackets: unchanged geometry, printed black (photo joints/collar).
 - leaf_shoulder: rev C leaf scaled about the sleeve axis so it sits on the jacket (0.25 mm gap).  vine_upper / vine_fore: flat wavy vine strip
   (2.6 x 1.4 mm) + 2 leaves on the front face of each block (green, glued).
 - gripper_housing: rev C housing, fixed finger stretched DF along the finger axis, + HOLLOW box shell (W wall, GAP air gap to the housing hull,
   2.0 mm top wall fused onto the housing top, open bottom) minus the finger+horn sweep; both fingers get a SW slot -> two prongs each.
 - vis_cable: render-only black tube (the real gripper-servo lead routed outside in a loop), not printed, not in collision checks."""
import bpy, bmesh, os, sys, math, json, random
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
E = lambda k, v: float(os.environ.get(k, v))
TJ, TOU, TOF, GRV, WC = E("TJ", 2.4), E("TOU", 9.0), E("TOF", 7.0), E("GRV", 0.5), E("WC", 1.8)
SKIRT, BOXO = E("SKIRT", 12.0), E("BOXO", 6.0)
DF, DTH, W, GAP, WT, BOX_H, TOP_IN = E("DF", 30.0), E("DTH", 22.5), E("W", 1.6), E("GAP", 0.6), E("WT", 2.0), E("BOX_H", 58.0), E("TOP_IN", 1.0)
SW, SLF, SLM = E("SW", 5.0), E("SLF", 28.0), E("SLM", 20.0)
BXD = E("BXD", 3.5)      # v3.34: box grows BXD per side in x (front/back depth)
C = L.coll("ARMS_v333")
for _o in list(C.objects): bpy.data.objects.remove(_o, do_unlink=True)      # regenerated build products of a previous run of this script
TMP = L.coll("TMP_v333_arms"); log = {}
DIRS = [Vector((i, j, k)).normalized() for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)]
def hull(name, obs, k=1.0, pts=None):
    bm = bmesh.new()
    for p in (pts or [v.co for ob in obs for v in ob.data.vertices]): bm.verts.new(p)
    bm.verts.ensure_lookup_table(); res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    dv = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if dv: bmesh.ops.delete(bm, geom=dv, context="VERTS")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    ctr = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    for v in bm.verts: v.co = ctr + (v.co - ctr) * k
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    h = bpy.data.objects.new(me.name, me); TMP.objects.link(h); return h
def multibox(name, boxes, R, J=Vector()):
    """one mesh of many (disjoint) boxes given in frame coords (x, o, d); p = J + R @ q"""
    bm = bmesh.new()
    for lo, hi in boxes:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]: v.co = J + R @ Vector([lo[i] + (v.co[i] + 0.5) * (hi[i] - lo[i]) for i in range(3)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); TMP.objects.link(o); return o
def fbox(name, lo, hi, R, J=Vector(), bev=0.0, c=None):
    b = L.box(name, lo, hi, c or TMP, bevel=bev)
    for v in b.data.vertices: v.co = J + R @ v.co
    b.data.update(); L.clean(b); return b
def tb(ob, R, J=Vector()):
    P = [R.transposed() @ (v.co - J) for v in ob.data.vertices]
    return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])
def vol(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); v = bm.calc_volume(signed=False); bm.free(); return v
def islands(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table(); seen = set(); n = 0
    for f in bm.faces:
        if f.index in seen: continue
        n += 1; st = [f]; seen.add(f.index)
        while st:
            g = st.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); st.append(h)
    bm.free(); return n
def grooves(lo, hi, rng):
    """wood-grain grooves (GRV deep, 0.6 wide) along d on the two x faces and the outer o face of the jacket box lo..hi"""
    bx = []
    for face in ("x0", "x1", "o1"):
        a0, a1 = (lo.y, hi.y) if face != "o1" else (lo.x, hi.x)
        t = a0 + 1.8
        while t < a1 - 1.8:
            dl = lo.z + 1.6 + rng.uniform(0, 3.0); dh = hi.z - 1.6 - rng.uniform(0, 3.0)
            if face == "x0": bx.append(((lo.x - 1, t - 0.3, dl), (lo.x + GRV, t + 0.3, dh)))
            elif face == "x1": bx.append(((hi.x - GRV, t - 0.3, dl), (hi.x + 1, t + 0.3, dh)))
            else: bx.append(((t - 0.3, hi.y - GRV, dl), (t + 0.3, hi.y + 1, dh)))
            t += rng.uniform(2.2, 3.4)
    return bx
def vine(name, R, face_x, o0, o1, d0, d1, rng, J=Vector()):
    """flat wavy vine strip on the plane x = face_x (frame coords), 2.6 wide, 1.4 thick, + 2 leaves; one body"""
    bm = bmesh.new(); N = 40; oc = (o0 + o1) / 2; amp = 0.18 * (o1 - o0); ph = rng.uniform(0, 6.28)
    cen = [Vector((0, oc + amp * math.sin(ph + 2 * math.pi * 1.0 * i / N), d0 + (d1 - d0) * i / N)) for i in range(N + 1)]
    def slab(poly2d, x0, x1):     # extrude a closed (o,d) polygon between x0..x1
        vs0 = [bm.verts.new(J + R @ Vector((x0, p[0], p[1]))) for p in poly2d]; vs1 = [bm.verts.new(J + R @ Vector((x1, p[0], p[1]))) for p in poly2d]
        bm.faces.new(vs0[::-1]); bm.faces.new(vs1)
        for i in range(len(poly2d)): j = (i + 1) % len(poly2d); bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))
    # strip outline
    lft, rgt = [], []
    for i, c in enumerate(cen):
        t = (cen[min(i + 1, N)] - cen[max(i - 1, 0)]); t = Vector((t.y, t.z)).normalized(); nrm = Vector((-t.y, t.x)) * 1.5
        lft.append((c.y + nrm.x, c.z + nrm.y)); rgt.append((c.y - nrm.x, c.z - nrm.y))
    slab(lft + rgt[::-1], face_x, face_x + 1.6)
    obs = []
    me = bpy.data.meshes.new(name); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); C.objects.link(ob)
    for k, tf in enumerate((0.33, 0.72)):
        i = int(tf * N); c = cen[i]; side = 1 if k == 0 else -1; ang = math.radians(side * 55); Lf, Wf = 9.0, 4.6
        base = Vector((c.y, c.z)); dirv = Vector((math.sin(ang) * side, -math.cos(ang))).normalized() if False else Vector((side * math.sin(math.radians(55)), -math.cos(math.radians(55))))
        perp = Vector((-dirv.y, dirv.x)); poly = []
        for j in range(17):
            u = j / 16.0; w = Wf / 2 * math.sin(math.pi * u) ** 0.8; p = base + dirv * (Lf * u - 0.8); poly.append(tuple(p + perp * w))
        for j in range(15, 0, -1):
            u = j / 16.0; w = Wf / 2 * math.sin(math.pi * u) ** 0.8; p = base + dirv * (Lf * u - 0.8); poly.append(tuple(p - perp * w))
        bm2 = bmesh.new(); bm = bm2; slab(poly, face_x, face_x + 1.5)
        me2 = bpy.data.meshes.new(name + f"_lf{k}"); bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces[:]); bm2.to_mesh(me2); bm2.free()
        lf = bpy.data.objects.new(me2.name, me2); TMP.objects.link(lf); L.clean(lf); L.boolean(ob, lf, "UNION")
    L.clean(ob, 1e-3); return ob
def leaf3d(name, R, o_face, base, ang_deg, Lf, Wf, lift, c=None):
    """pointed leaf lying on the plane o = o_face (frame coords): base (x, d), direction ang_deg from +d toward +x, length Lf, width Wf,
    1.3 mm blade + 0.8 mm midrib ridge, blade flat on the face for u < 0.35 then curls out to 'lift' mm at the tip. one closed body."""
    e = Vector((math.sin(math.radians(ang_deg)), math.cos(math.radians(ang_deg)))); f = Vector((-e.y, e.x)); NU, NV = 26, 9
    def P(u, v, h):
        lft = lift * max(0.0, (u - 0.35) / 0.65) ** 2; q2 = base + e * (u * Lf) + f * v
        return R @ Vector((q2.x, o_face + h + lft, q2.y))
    bm = bmesh.new(); grid = []
    for i in range(NU + 1):
        u = i / NU; w = max(Wf / 2 * math.sin(math.pi * min(u, 0.999)) ** 0.75 * (1 - 0.35 * u), 0.05) if 0 < i < NU else 0.05
        row = []
        for j in range(NV):
            v = -w + 2 * w * j / (NV - 1); hb = 1.5 + 0.8 * max(0.0, 1 - abs(v) / 0.9) * (1 if 0.03 < u < 0.93 else 0)
            row.append((bm.verts.new(P(u, v, 0.0)), bm.verts.new(P(u, v, hb))))
        grid.append(row)
    for i in range(NU):
        for j in range(NV - 1):
            bm.faces.new((grid[i][j][0], grid[i][j + 1][0], grid[i + 1][j + 1][0], grid[i + 1][j][0]))
            bm.faces.new((grid[i][j][1], grid[i + 1][j][1], grid[i + 1][j + 1][1], grid[i][j + 1][1]))
        for j, k in ((0, 0), (NV - 1, 1)):
            a0, a1 = grid[i][j], grid[i + 1][j]; bm.faces.new((a0[0], a1[0], a1[1], a0[1]))
    for i in (0, NU):
        r = grid[i]; bm.faces.new([r[j][0] for j in range(NV)] + [r[j][1] for j in range(NV - 1, -1, -1)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); (c or C).objects.link(ob); L.clean(ob, 1e-4); return ob
def head_cutter(s):
    """v333h (final): union of the per-pose head convex hulls k < 100 (measure/head_sweep_hulls.py; L frame, 0.8 mm inflated; hulls that
    would bite the rev C core are skipped); R = y-mirror.  The k >= 100 exact-overlap hulls (measure/head_exact_hulls.py) are NOT used:
    the v333i rebuild with them crashed / stalled (see STATUS.md)."""
    import json
    HH = json.load(open(os.path.join(L.HERE, "..", "work", "head_hulls.json"))); cut = None
    for h in HH:
        if h["k"] >= 100 or h["cut_in_core_mm3"] > 1.0 or h["cut_mm3"] <= 0.0: continue
        hu = L.imp(os.path.join(L.HERE, "in", "head_hulls_L", f"hull_{h['k']:03d}.stl"), f"tmp_hull_{s}_{h['k']}", TMP)
        if cut is None: cut = hu
        else: L.boolean(cut, hu, "UNION")
    L.clean(cut, 1e-4)
    if s == "R": cut.data.transform(Matrix.Diagonal((1.0, -1.0, 1.0, 1.0))); cut.data.flip_normals(); cut.data.update()
    return cut
rng = random.Random(333)
for s, sg in (("L", 1), ("R", -1)):
    a = Vector((0.0, -0.98, -0.17 * sg)).normalized(); o = (-a if s == "L" else a).normalized(); d = Vector((1, 0, 0)).cross(o).normalized()
    if d.z > 0: d = -d
    R = Matrix((Vector((1, 0, 0)), o, d)).transposed()          # columns x, o, d ; world p = R @ (x, o, d)
    lg = log.setdefault(s, {})
    # ---------- 1. wood jackets on the sleeves ----------
    for sl, sv_n, d_rec, nm, TO, mates in (("shoulder_sleeve", "s32_shoulder", (1.5, 1.5), "upper", TOU, ("upper_arm",)), ("elbow_sleeve", "s32_elbow", (1.5, 1.5), "fore", TOF, ("forearm",))):
        sleeve = L.imp(os.path.join(L.REF, f"{sl}_{s}.stl"), f"{sl}_{s}_v333", C); servo = L.imp(os.path.join(L.REF, f"{sv_n}_{s}.stl"), f"tmp_{sv_n}_{s}", TMP)
        v0 = vol(sleeve); lo, hi = tb(sleeve, R)
        jlo = Vector((lo.x - TJ, lo.y + 1.3, lo.z + d_rec[0])); jhi = Vector((hi.x + TJ, hi.y + TO, hi.z - d_rec[1]))
        if nm == "fore" and SKIRT > 0: jhi = Vector((jhi.x, jhi.y, SKIRT))     # block continues down over the forearm plate (short black wrist collar, photo)
        jb = fbox(f"tmp_jacket_{nm}_{s}", jlo, jhi, R, bev=1.2); steps = [round(vol(jb))]
        L.boolean(jb, hull(f"tmp_jh_{nm}_{s}", (sleeve, servo), 0.97), "DIFFERENCE"); steps.append(round(vol(jb)))
        # hollow outer cap (WC walls), open at the bottom (+d end); for the forearm it also clears the plate (0.3 mm) inside the skirt
        d_end = (SKIRT if (nm == "fore" and SKIRT > 0) else jhi.z) + 1.0
        if TO > 2 * WC + 1.0:
            L.boolean(jb, fbox(f"tmp_cap_{nm}_{s}", Vector((jlo.x + WC, hi.y + 1.4, jlo.z + WC)), Vector((jhi.x - WC, jhi.y - WC, d_end)), R, bev=0.8), "DIFFERENCE"); steps.append(round(vol(jb)))
        if nm == "upper" and os.environ.get("HEADCLEAR", "1") == "1":     # head range: carve the head sweep at the hb_check poses newly hit by the jacket
            L.boolean(jb, head_cutter(s), "DIFFERENCE"); steps.append(round(vol(jb)))   # (measure/head_sweep_hulls.py; on the plain box, before the grooves = EXACT-safe)
        jgh = Vector((jhi.x, jhi.y, SKIRT if (nm == "fore" and SKIRT > 0) else jhi.z))
        for tr in range(4):      # grooves; EXACT solver occasionally fails on the left forearm (coplanar faces) -> retry with a jittered set
            keep = jb.data.copy(); vb = vol(jb); jit = Vector((0.0, 0.07 * tr, 0.13 * tr))
            L.boolean(jb, multibox(f"tmp_grv_{nm}_{s}_{tr}", grooves(jlo + jit, jgh + jit, rng), R), "DIFFERENCE"); steps.append(round(vol(jb)))
            if vol(jb) > 0.85 * vb: break
            jb.data = keep; steps.append("grooves_retry")
        if nm == "fore" and SKIRT > 0:
            pl = L.imp(os.path.join(L.REF, f"forearm_{s}.stl"), f"tmp_plate_{s}", TMP); plo, phi = tb(pl, R)
            L.boolean(jb, fbox(f"tmp_platecut_{s}", Vector((plo.x - 0.3, plo.y - 0.3, 1.0)), Vector((phi.x + 0.3, jhi.y - WC, SKIRT + 1.0)), R), "DIFFERENCE")   # plate clearance + hollow skirt; steps.append(round(vol(jb)))
            jhi = Vector((jhi.x, jhi.y, SKIRT))
        for mt in mates:      # same-link printed mates: never overlap them (exact difference)
            mo = L.imp(os.path.join(L.REF, f"{mt}_{s}.stl"), f"tmp_mate_{mt}_{s}", TMP); keep = jb.data.copy(); vb = vol(jb)
            L.boolean(jb, mo, "DIFFERENCE"); steps.append(round(vol(jb)))
            if vol(jb) < 0.8 * vb:      # EXACT solver failure (seen once on the left forearm plate): keep the pre-cut mesh, overlap is re-checked below
                jb.data = keep; steps.append(f"mate_cut_{mt}_reverted")
            ovm = L.dup(mo, f"tmp_ovm_{mt}_{s}", TMP); L.boolean(ovm, jb, "INTERSECT"); steps.append(f"ovl_{mt}={vol(ovm):.1f}")
        L.boolean(sleeve, jb, "UNION"); L.clean(sleeve, 1e-3); drp = L.drop_islands(sleeve)
        lg[sl] = dict(sleeve_lo=[round(x, 1) for x in lo], sleeve_hi=[round(x, 1) for x in hi], jacket_lo=[round(x, 1) for x in jlo], jacket_hi=[round(x, 1) for x in jhi],
                      vol0=round(v0), vol=round(vol(sleeve)), islands=islands(sleeve), dropped=drp, steps=steps)
        vn = vine(f"vine_{nm}_{s}_v333", R, jhi.x + 0.05, jlo.y + 3.5, jhi.y - 3.5, jlo.z + 2.0, jhi.z - 2.0, rng)
        lg[f"vine_{nm}"] = dict(vol=round(vol(vn)), islands=islands(vn))
        lname = "leaf_shoulder" if nm == "upper" else "leaf_elbow"
        if s == "L":     # leaves: built on the left arm, mirrored (y -> -y) for the right arm
            if nm == "upper":
                lf = leaf3d(f"{lname}_{s}_v333", R, jhi.y + 0.05, Vector((4.5, jlo.z + 4.0)), 28.0, 25.0, 13.0, 4.5)
                lf2 = leaf3d(f"tmp_leaf2_{nm}_{s}", R, jhi.y + 0.05, Vector((1.5, jlo.z + 6.0)), -38.0, 17.0, 9.0, 3.0, c=TMP)
                stem = fbox(f"tmp_stem_{nm}_{s}", Vector((1.0, jhi.y + 0.05, jlo.z + 1.5)), Vector((7.0, jhi.y + 1.6, jlo.z + 8.5)), R, bev=0.5)
            else:
                lf = leaf3d(f"{lname}_{s}_v333", R, jhi.y + 0.05, Vector((4.5, jhi.z - 4.0)), 150.0, 21.0, 11.0, 3.5)
                lf2 = leaf3d(f"tmp_leaf2_{nm}_{s}", R, jhi.y + 0.05, Vector((2.5, jhi.z - 6.0)), -160.0, 15.0, 8.0, 2.5, c=TMP)
                stem = fbox(f"tmp_stem_{nm}_{s}", Vector((1.0, jhi.y + 0.05, jhi.z - 8.5)), Vector((7.0, jhi.y + 1.6, jhi.z - 1.5)), R, bev=0.5)
            L.boolean(lf, lf2, "UNION"); L.boolean(lf, stem, "UNION"); L.clean(lf, 1e-3)
        else:
            src = bpy.data.objects[f"{lname}_L_v333"]; lf = L.dup(src, f"{lname}_{s}_v333", C)
            for v in lf.data.vertices: v.co.y = -v.co.y
            lf.data.update(); L.clean(lf, 1e-4)
        t1 = L.dup(lf, f"tmp_ovl_{nm}_{s}", TMP); L.boolean(t1, sleeve, "INTERSECT")
        lg[lname] = dict(overlap_mm3=round(vol(t1), 2), vol=round(vol(lf)), islands=islands(lf))
    # ---------- 2. gripper: rev C housing + stretched two-prong fingers + hollow FEETECH box ----------
    J = Vector((4.0, sg * 65.5, -42.2))
    hs = L.imp(os.path.join(L.REF, f"gripper_housing_{s}.stl"), f"gripper_housing_{s}_v333", C)
    fm = L.imp(os.path.join(L.REF, f"finger_moving_{s}.stl"), f"finger_moving_{s}_v333", C)
    hn = L.imp(os.path.join(L.REF, f"s32horn_gripper_{s}.stl"), f"tmp_horn_{s}", TMP)
    sv = L.imp(os.path.join(L.REF, f"s32_gripper_{s}.stl"), f"tmp_servo_{s}", TMP); fa = L.imp(os.path.join(L.REF, f"forearm_{s}.stl"), f"tmp_fa_{s}", TMP)
    v_hs0, v_fm0 = vol(hs), vol(fm)
    loc = lambda p: R.transposed() @ (p - J)
    H = [loc(v.co) for v in hs.data.vertices]; top_d = min(h.z for h in H)
    hs0 = L.dup(hs, f"tmp_hs0_{s}", TMP)
    for ob in (hs, fm):
        for v in ob.data.vertices:
            if (v.co - J).dot(d) > DTH: v.co = v.co + d * DF
        ob.data.update()
    # two prongs: slot SW wide, SL long from the tip, centred on each finger's prong o-range
    for ob, nm, SL in ((hs, "fixed", SLF), (fm, "moving", SLM)):
        P = [loc(v.co) for v in ob.data.vertices]; tip = max(p.z for p in P); Pp = [p for p in P if p.z > tip - SL]
        o0, o1 = min(p.y for p in Pp), max(p.y for p in Pp); oc = (o0 + o1) / 2
        L.boolean(ob, fbox(f"tmp_slot_{nm}_{s}", Vector((-40, oc - SW / 2, tip - SL)), Vector((40, oc + SW / 2, tip + 3)), R, J), "DIFFERENCE")
        lg[f"prong_{nm}"] = dict(o=[round(o0, 1), round(o1, 1)], tip_d=round(tip, 1), prong_w=round((o1 - o0 - SW) / 2, 2))
    L.boolean(hs, fm, "DIFFERENCE"); L.clean(hs, 1e-3)      # stretched fixed finger must not overlap the stretched moving finger at rest
    Hl = [loc(v.co) for v in sv.data.vertices] + [h for h in H if h.z < top_d + 52]
    hx0, hx1 = min(h.x for h in Hl), max(h.x for h in Hl); ho0, ho1 = min(h.y for h in Hl), max(h.y for h in Hl)
    m = GAP + W
    BX = (hx0 - m - BXD, hx1 + m + BXD, ho0 - m, ho1 + m + BOXO, top_d + TOP_IN, top_d + BOX_H)
    outer = fbox(f"tmp_outer_{s}", Vector(BX[0::2]), Vector(BX[1::2]), R, J, bev=3.0)
    inner = fbox(f"tmp_inner_{s}", Vector((BX[0] + W, BX[2] + W, BX[4] + WT)), Vector((BX[1] - W, BX[3] - W, BX[5] + 6)), R, J, bev=1.4)
    L.boolean(outer, inner, "DIFFERENCE")
    L.boolean(outer, hull(f"tmp_hullA_{s}", (sv, hn, fa), 1.008), "DIFFERENCE")
    L.boolean(outer, hull(f"tmp_hullB_{s}", (hs0,), 0.97), "DIFFERENCE")
    pts = []
    for ang in range(-14, 65, 4):
        Mr = Matrix.Translation(J) @ Matrix.Rotation(math.radians(ang), 4, a) @ Matrix.Translation(-J)
        for src in (fm, hn): pts += [Mr @ v.co for v in src.data.vertices]
    L.boolean(outer, hull(f"tmp_sweep_{s}", (), 1.04, pts), "DIFFERENCE")
    L.clean(outer, 1e-3); dpo = L.drop_islands(outer, 30.0); v_box = vol(outer)
    L.boolean(hs, outer, "UNION"); L.clean(hs, 1e-3); drp = L.drop_islands(hs)
    lg["gripper"] = dict(BX=[round(x, 2) for x in BX], box_mm=[round(BX[1] - BX[0], 1), round(BX[3] - BX[2], 1), round(BX[5] - BX[4], 1)], top_d=round(top_d, 2),
                         box_vol=round(v_box), box_drop=dpo, housing_vol0=round(v_hs0), housing_vol=round(vol(hs)), finger_vol0=round(v_fm0), finger_vol=round(vol(fm)),
                         islands=islands(hs), finger_islands=islands(fm), dropped=drp)
    # ---------- 3. render-only cable loop (gripper servo lead) ----------
    cu = bpy.data.curves.new(f"vis_cable_{s}", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 1.7; cu.bevel_resolution = 3
    spl = cu.splines.new("BEZIER"); pp = [(4, 99.0, -66.0), (6.5, 110.0, -50.0), (9.0, 117.0, -22.0), (8.0, 116.0, 4.0), (5.0, 110.0, 21.0)]
    spl.bezier_points.add(len(pp) - 1)
    for bp, p in zip(spl.bezier_points, pp): bp.co = R @ Vector(p); bp.handle_left_type = bp.handle_right_type = "AUTO"
    cob = bpy.data.objects.new(f"tmp_cable_{s}", cu); TMP.objects.link(cob); bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(cob.evaluated_get(bpy.context.evaluated_depsgraph_get())); co = bpy.data.objects.new(f"vis_cable_{s}_v333", me); C.objects.link(co)
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP)
def tidy(ob):      # drop degenerate debris faces left by EXACT booleans, then the export-safe pass (see tidy2)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() < 1e-8], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS"); bm.to_mesh(ob.data); bm.free(); ob.data.update(); L.drop_islands(ob, 1.0)
    return tidy2(ob)
def tidy2(ob):   # export-safe: ear-clip triangulation (the exporter's ngon fill folds concave EXACT ngons into 2-face fins), drop
    # duplicate faces, then fuse any kissing (4-face) edge with a 0.6 mm cube so every body is a closed 2-manifold
    out = dict(dups=0, fused=0)
    for it in range(4):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="EAR_CLIP")
        seen = {}
        for f in bm.faces: seen.setdefault(frozenset(v.index for v in f.verts), []).append(f)
        bad = [f for fs in seen.values() if len(fs) > 1 for f in fs]; out["dups"] += len(bad)
        if bad: bmesh.ops.delete(bm, geom=bad, context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bad_e = [e for e in bm.edges if len(e.link_faces) != 2]
        short = [e for e in bad_e if e.calc_length() < 0.2]
        if bad_e and len(short) == len(bad_e):     # pinch slivers from the groove cuts: collapse the tiny kissing edges (moves < 0.1 mm)
            bmesh.ops.collapse(bm, edges=short, uvs=False); bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
            out["collapsed"] = out.get("collapsed", 0) + len(short); bm.to_mesh(ob.data); bm.free(); ob.data.update(); continue
        nm = [(ob.matrix_world @ ((e.verts[0].co + e.verts[1].co) / 2)) for e in bad_e]
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
        if not nm or it == 3: break
        for q, c in enumerate(nm):
            bx = L.box(f"tmp_fuse_{ob.name}_{it}_{q}", tuple(c - Vector((0.3, 0.3, 0.3))), tuple(c + Vector((0.3, 0.3, 0.3))), bpy.data.collections.get("TMP_fuse") or L.coll("TMP_fuse"))
            L.boolean(ob, bx, "UNION"); bpy.data.objects.remove(bx, do_unlink=True); out["fused"] += 1
    return out
TIDY = {}
for ob in list(C.objects):
    if ob.type == "MESH" and not ob.name.startswith("vis_"): TIDY[ob.name] = tidy(ob)
def manifold_ok(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); ok = all(len(e.link_faces) == 2 for e in bm.edges); bm.free(); return ok
MIRR = []
for ob in list(C.objects):     # a right part the cleanup could not close (EXACT pinch slivers on one side) -> mirror of its clean left twin
    if ob.type != "MESH" or ob.name.startswith("vis_") or "_R" not in ob.name or manifold_ok(ob): continue
    lt = bpy.data.objects.get(ob.name.replace("_R", "_L"))
    if lt is None or not manifold_ok(lt): continue
    me = lt.data.copy(); me.transform(ob.matrix_world.inverted() @ Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ lt.matrix_world); me.flip_normals()
    old_me = ob.data; ob.data = me; me.name = old_me.name + "_mirL"; bpy.data.meshes.remove(old_me); MIRR.append(ob.name)
print("TIDY", json.dumps({k: v for k, v in TIDY.items() if v["dups"] or v["fused"]}), "MIRRORED", MIRR)
A = os.path.join(L.OUT, "asm"); P = os.path.join(L.OUT, "stl"); mp_fn = os.path.join(A, "map.json"); mp = json.load(open(mp_fn))
def export_flat(ob, path, R):
    """print frame for the jackets/leaves/vines: frame (x, d, -o) -> the closed outer face down"""
    M3 = Matrix((Vector((1, 0, 0)), -R.col[2] * -1, -R.col[1])) if False else Matrix((R.col[0], R.col[2], -R.col[1]))   # rows = new axes
    if M3.determinant() < 0: M3[0] = -M3[0]      # keep it a rotation (a left-handed frame would print the MIRROR part)
    T = M3.to_4x4(); pts = [T @ v.co for v in ob.data.vertices]; lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    L.export(ob, path, Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))) @ T @ ob.matrix_world.inverted())
for s, sg in (("L", 1), ("R", -1)):
    a = Vector((0.0, -0.98, -0.17 * sg)).normalized(); o = (-a if s == "L" else a).normalized(); d = Vector((1, 0, 0)).cross(o).normalized()
    if d.z > 0: d = -d
    R = Matrix((Vector((1, 0, 0)), o, d)).transposed()
    for n, ln, cls, pr in ((f"shoulder_sleeve_{s}", f"upper_arm_{s}", "wood", "flat"), (f"elbow_sleeve_{s}", f"fore_arm_{s}", "wood", "flat"),
                           (f"leaf_shoulder_{s}", f"upper_arm_{s}", "green", "flat"), (f"leaf_elbow_{s}", f"fore_arm_{s}", "green", "flat"), (f"vine_upper_{s}", f"upper_arm_{s}", "green", "flat"),
                           (f"vine_fore_{s}", f"fore_arm_{s}", "green", "flat"), (f"gripper_housing_{s}", f"fore_arm_{s}", "black", "T"),
                           (f"finger_moving_{s}", f"finger_{s}", "black", "T"), (f"vis_cable_{s}", f"fore_arm_{s}", "black", None)):
        ob = bpy.data.objects[n + "_v333"]; L.export(ob, os.path.join(A, n + ".stl")); mp[n] = [ln, cls]
        if pr == "flat": export_flat(ob, os.path.join(P, f"v334_{n}.stl"), R)
        elif pr == "T": L.export_print(ob, os.path.join(P, f"v334_{n}.stl"), n)
    for n, ln in ((f"upper_arm_{s}", f"upper_arm_{s}"), (f"forearm_{s}", f"fore_arm_{s}")):      # recolour only (rev C geometry)
        ob = L.imp(os.path.join(L.REF, n + ".stl"), n + "_v333_black", C); L.export(ob, os.path.join(A, n + ".stl")); mp[n] = [ln, "black"]
json.dump(mp, open(mp_fn, "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v334.blend"))
print("ARMS_DONE", json.dumps(log))
