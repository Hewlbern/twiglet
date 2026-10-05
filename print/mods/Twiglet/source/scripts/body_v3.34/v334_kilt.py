"""v3.34 kilt = v3.33 kilt script with a wider flare: RHF 98 -> 118, RHB 102 -> 122, ZT -66 -> -72, YMAX 63 -> 65.5.  blender -b body_v334.blend -P v334_kilt.py
(v3.33 doc follows)"""
"""v3.33 kilt (Blender 4.2: blender -b body_v333.blend -P v333_kilt.py). Photo: broad felt leaves with straight sides down to ~57 % of the
length, then straight converging edges to a SHARP tip, a folded centre crease per leaf, layered (centre leaf over its neighbours), strong flare.
Per petal (10, same positions - their tops hang in the hip-ring rails): the v3.32 petal above z = ZC is kept unchanged (rails/attachment), the
lower part is rebuilt as a faceted leaf panel: two flat facets meeting in a raised centre crease (CREASE mm), TH thick, half-angle constant down to
the shoulder (z = ZS) then straight to the tip (z = ZT), radius flaring from the kept top to R_HEM (photo flare ~27 deg); alternate petals on an
outer layer (+LAYER mm, +EXT deg wider, overlapping the neighbours with a >= 0.5 mm air gap); in the arm corridor (x > XCOR, the arms swing there)
the panel is pulled in radially so |y| <= YMAX.  Writes collection KILT_v333, out/asm/kilt_petal_XX.stl, map.json (+ hip_ring re-specified green)."""
import bpy, bmesh, os, sys, math, json
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
E = lambda k, v: float(os.environ.get(k, v))
ZC, ZS, ZT, TH, CREASE, LAYER, EXT = E("ZC", 18.0), E("ZS", -27.0), E("ZT", -72.0), E("TH", 1.7), E("CREASE", 3.0), E("LAYER", 3.8), E("EXT", 0.0)
RHF, RHB, YMAX, XCOR, FLP = E("RHF", 118.0), E("RHB", 122.0), E("YMAX", 65.5), E("XCOR", -32.0), E("FLP", 1.15); ZTF = E("ZTF", -66.0)   # v334b: front petals keep the v3.33 hem height (foot swing), sides/back -72   # v3.34: wider flare front/back, corridor 65.5 (arm inner faces >= 67.7)
R0 = E("R0", 0.0)      # common base radius (0 = auto: outermost kept-top radius + 0.3, so no leaf moves inward of its top)
TB = E("TB", 0.22); NC = int(E("NC", 13)); CRW = E("CRW", 0.6); TIPW = E("TIPW", 1.4); EXI = E("EXI", 0.6); CLR = E("CLR", 0.3)   # columns across a leaf; crease half-width (fraction of the span)     # top -> common-base blend length (fraction of the leaf length; long = gentle tilt, walls stay >= 1.2 mm)
AX = Vector((-20.9, 0.0)); OUTER = {1, 4, 6, 8}      # layer assignment (01 = centre front over 00/02; back 03..09 alternate)
K = L.coll("KILT_v333")
for _o in list(K.objects): bpy.data.objects.remove(_o, do_unlink=True)
TMP = L.coll("TMP_v333_kilt"); log = {}
IN = os.path.join(L.HERE, "in", "asm_v332")
FRAME = L.imp(os.path.join(L.HERE, "in", "asm_torso_frame_v331.stl"), "tmp_torso_frame", TMP)
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
sm = lambda x: 0.0 if x <= 0 else (1.0 if x >= 1 else x * x * (3 - 2 * x))
def tidy(ob):   # export-safe: ear-clip triangulation (the exporter's ngon fill folds concave EXACT ngons into 2-face fins), drop
    # duplicate faces, then fuse any kissing (4-face) edge with a 0.6 mm cube so every body is a closed 2-manifold
    out = dict(dups=0, fused=0)
    for it in range(3):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="EAR_CLIP")
        seen = {}
        for f in bm.faces: seen.setdefault(frozenset(v.index for v in f.verts), []).append(f)
        bad = [f for fs in seen.values() if len(fs) > 1 for f in fs]; out["dups"] += len(bad)
        if bad: bmesh.ops.delete(bm, geom=bad, context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        nm = [(ob.matrix_world @ ((e.verts[0].co + e.verts[1].co) / 2)) for e in bm.edges if len(e.link_faces) != 2]
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
        if not nm or it == 2 or len(nm) > 8: out['open_edges'] = len(nm); break
        for q, c in enumerate(nm):
            bx = L.box(f"tmp_fuse_{ob.name}_{it}_{q}", tuple(c - Vector((0.3, 0.3, 0.3))), tuple(c + Vector((0.3, 0.3, 0.3))), bpy.data.collections.get("TMP_fuse") or L.coll("TMP_fuse"))
            L.boolean(ob, bx, "UNION"); bpy.data.objects.remove(bx, do_unlink=True); out["fused"] += 1; print("FUSE", ob.name, q, len(nm), flush=True)
    return out
DATA = {}
for i in range(10):
    src = L.imp(os.path.join(IN, f"kilt_petal_{i:02d}.stl"), f"tmp_scan_{i:02d}", TMP)
    band = [v.co.copy() for v in src.data.vertices if ZC - 1.5 < v.co.z < ZC + 1.5]
    DATA[i] = [(math.atan2(p.y - AX.y, p.x - AX.x), math.hypot(p.x - AX.x, p.y - AX.y)) for p in band]
def amid(xs): return math.atan2(sum(math.sin(a) for a in xs), sum(math.cos(a) for a in xs))
CEN = {i: amid([a for a, r in DATA[i]]) for i in DATA}; order = sorted(DATA, key=lambda i: CEN[i])
LEVEL = {}; pairs_log = {}
def rel(a, c): return ((a - c + math.pi) % (2 * math.pi)) - math.pi
for k in range(len(order)):
    i, j = order[k], order[(k + 1) % len(order)]
    ci = CEN[i]; ri = [(rel(a, ci), r) for a, r in DATA[i]]; rj = [(rel(a, ci), r) for a, r in DATA[j]]
    hi_i = max(a for a, r in ri); lo_j = min(a for a, r in rj)
    if lo_j > hi_i + math.radians(4): pairs_log[f"{i:02d}-{j:02d}"] = "gap"; continue
    zi = [r for a, r in ri if a >= lo_j]; zj = [r for a, r in rj if a <= hi_i]
    if not zi or not zj: pairs_log[f"{i:02d}-{j:02d}"] = "touch"; continue
    out_i = sorted(zi)[len(zi) // 2] > sorted(zj)[len(zj) // 2]; pairs_log[f"{i:02d}-{j:02d}"] = f"{i:02d} outer" if out_i else f"{j:02d} outer"
    LEVEL.setdefault(i, 0); LEVEL[j] = LEVEL[i] + (-1 if out_i else 1)
for i in DATA: LEVEL.setdefault(i, 0)
chains, cur = [], []
st = next(k for k in range(len(order)) if pairs_log.get(f"{order[k - 1]:02d}-{order[k]:02d}") == "gap")
for k in range(len(order)):
    i = order[(st + k) % len(order)]
    if cur and pairs_log.get(f"{cur[-1]:02d}-{i:02d}") == "gap": chains.append(cur); cur = []
    cur.append(i)
chains.append(cur)
for ch in chains:
    mn = min(LEVEL[i] for i in ch)
    for i in ch: LEVEL[i] -= mn
R0A = R0 or (max(r for i in DATA for a, r in DATA[i]) + 0.3)
ST = {}
log["_layers"] = dict(pairs=pairs_log, level={f"{i:02d}": v for i, v in LEVEL.items()}, R0=round(R0A, 1))
for i in range(10):
    src = L.imp(os.path.join(IN, f"kilt_petal_{i:02d}.stl"), f"kilt_petal_{i:02d}_v333", K)
    band = [v.co for v in src.data.vertices if ZC - 1.5 < v.co.z < ZC + 1.5]
    ang = [math.atan2(p.y - AX.y, p.x - AX.x) for p in band]; mid = math.atan2(sum(math.sin(a) for a in ang), sum(math.cos(a) for a in ang))
    rel = [((a - mid + math.pi) % (2 * math.pi)) - math.pi for a in ang]; rr = sorted(math.hypot(p.x - AX.x, p.y - AX.y) for p in band)
    a0, a1 = min(rel), max(rel); r_out = rr[int(0.97 * (len(rr) - 1))]; r_in = rr[int(0.03 * (len(rr) - 1))]
    phc = mid + (a0 + a1) / 2; al0 = (a1 - a0) / 2
    RS = [math.hypot(p.x - AX.x, p.y - AX.y) for p in band]; RL = [x - (a0 + a1) / 2 for x in rel]
    def rprof(sc):     # kept-top sheet radius (outer/inner) at relative angle sc*al0, from the band vertices near that angle
        tgt = sc * al0 * (0.96 if abs(sc) == 1 else 1.0); w = al0 / (NC - 1)
        sel = [r for r, a in zip(RS, RL) if abs(a - tgt) < w] or [r for r, a in sorted(zip(RS, RL), key=lambda q: abs(q[1] - tgt))[:6]]
        return max(sel), min(sel)
    front = math.cos(phc) > 0.3; RH = RHF if front else RHB; lev = LEVEL[i]; ZTi = ZTF if front else ZT
    # 1. keep the top
    cut = L.box(f"tmp_keep_{i}", (-300, -300, ZC), (300, 300, 100), TMP); L.boolean(src, cut, "INTERSECT")
    # 2. leaf panel: NC columns, crease tent within |s| < CRW, layer level lev (outer petals +LAYER per level), radial thickness grown by the
    #    meridian slope so the NORMAL wall stays TH on the flare ramp
    NT = 30; Z0 = ZC + 0.5; cols = [-1.0 + 2.0 * j / (NC - 1) for j in range(NC)]; RP = {sc: rprof(sc) for sc in cols}
    ts = (Z0 - ZS) / (Z0 - ZTi); clamp_n = 0
    def RO(t, sc):
        r_o, r_i = RP[sc]; bt = sm(t / TB)
        rb = (r_o + 0.3) * (1 - bt) + (R0A + (RH - R0A) * (t ** FLP) + LAYER * lev) * bt
        return rb + CREASE * max(0.0, 1.0 - abs(sc) / CRW) * sm(t / 0.15)
    def bad(ph, r): return AX.x + r * math.cos(ph) > XCOR and abs(r * math.sin(ph)) > YMAX
    def lim(side, r):  # corridor-limited edge angle on one side (absolute angle magnitude) for radius r
        return math.asin(min(1.0, YMAX / r)) if math.cos(phc) > 0 else math.acos(max(-1.0, (XCOR - AX.x) / r))
    def mk(name, infl):   # leaf solid; infl > 0 -> clearance body (outer +infl, inner -infl) used to carve the inner neighbour
        nonlocal_clamp = [0]; bm = bmesh.new(); grid = []
        for k in range(NT + 1):
            t = k / NT; z = Z0 - t * (Z0 - ZTi); al = al0
            if t > ts: al = max(al * (1.0 - (t - ts) / (1.0 - ts)), TIPW / max(RO(t, 0.0), 1.0))   # straight edges to the tip; TIPW half-width (printable tip)
            scl = {}
            for sd in (-1.0, 1.0):    # arm corridor: compress that side's angular span (columns keep their order, sheet stays radial-thick)
                r_e = RO(t, sd); ph_e = phc + sd * al; f = 1.0
                if bad(ph_e, r_e):
                    pl = math.copysign(lim(sd, r_e), math.sin(ph_e)); f = max(0.05, min(1.0, (pl - phc) / (sd * al))); nonlocal_clamp[0] += 1
                scl[sd] = f
            row = []
            for sc in cols:
                r_o, r_i = RP[sc]; ro = RO(t, sc)
                dz = (Z0 - ZTi) / NT; slope = (RO(min(1.0, t + 0.5 / NT), sc) - RO(max(0.0, t - 0.5 / NT), sc)) / dz
                thn = TH * math.sqrt(1.0 + slope * slope)
                thk = thn + (ro - (r_i + 0.1) - thn) * (1 - sm(t / 0.06))     # first rows span the kept-top sheet (inner +0.1 .. outer +0.3): fuse
                ph = phc + sc * al * (scl[1.0] if sc > 0 else scl[-1.0])
                if lev == 0: thk += EXI * sm(t / 0.03) * (1.0 - sm((t - 0.15) / 0.15))   # inner petal: +EXI inward under the outer neighbour's carve
                c, s_ = math.cos(ph), math.sin(ph); ri = ro - thk
                zz = z + (infl if k == 0 else (-infl if k == NT else 0.0)); ro2, ri2 = ro + infl, ri - infl
                row.append((bm.verts.new((AX.x + ro2 * c, AX.y + ro2 * s_, zz)), bm.verts.new((AX.x + ri2 * c, AX.y + ri2 * s_, zz))))
            grid.append(row)
        for k in range(NT):
            for j in range(len(cols) - 1):
                bm.faces.new((grid[k][j][0], grid[k][j + 1][0], grid[k + 1][j + 1][0], grid[k + 1][j][0]))
                bm.faces.new((grid[k][j][1], grid[k + 1][j][1], grid[k + 1][j + 1][1], grid[k][j + 1][1]))
            for j in (0, len(cols) - 1):
                a, b = grid[k][j], grid[k + 1][j]; bm.faces.new((a[0], b[0], b[1], a[1]))
        for k in (0, NT):
            r = grid[k]; bm.faces.new([r[j][0] for j in range(len(cols))] + [r[j][1] for j in range(len(cols) - 1, -1, -1)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        lf = bpy.data.objects.new(me.name, me); TMP.objects.link(lf); L.clean(lf, 1e-4); return lf, nonlocal_clamp[0]
    lf, clamp_n = mk(f"tmp_leaf_{i}", 0.0); cl, _ = mk(f"tmp_clr_{i}", CLR); print("LEAF", i, flush=True)
    L.boolean(lf, FRAME, "DIFFERENCE")      # the torso frame tabs the v3.32 petal tops are slotted around
    ST[i] = dict(src=src, lf=lf, cl=cl, top=L.dup(src, f"tmp_top_{i}", TMP), lev=lev)
    log[f"{i:02d}"] = dict(phc_deg=round(math.degrees(phc), 1), half_deg=round(math.degrees(al0), 1), r_prof={str(k): [round(x, 1) for x in v] for k, v in RP.items()}, front=front, level=lev, ncols=NC, clamped_verts=clamp_n)
NB = {i: set() for i in range(10)}
for pk, pv in pairs_log.items():
    if pv in ("gap",): continue
    a_, b_ = int(pk[:2]), int(pk[3:]); NB[a_].add(b_); NB[b_].add(a_)
for i in range(10):     # each leaf yields to its neighbours' kept tops; the inner (lower level) one also yields to the outer leaf + 0.4 clearance
    S = ST[i]; carved = []
    for j in sorted(NB[i]):
        L.boolean(S["lf"], ST[j]["top"], "DIFFERENCE"); carved.append(f"top{j:02d}"); print("CARVE", i, j, flush=True)
        if ST[j]["lev"] > S["lev"]: L.boolean(S["lf"], ST[j]["cl"], "DIFFERENCE"); carved.append(f"leaf{j:02d}")
    src = S["src"]; v_top = vol(src); L.boolean(src, S["lf"], "UNION"); L.clean(src, 1e-3); drp = L.drop_islands(src); nd = tidy(src); print("TIDY", i, nd, flush=True)
    log[f"{i:02d}"].update(carved=carved, tidy=nd, vol_top=round(v_top), vol=round(vol(src)), islands=islands(src), dropped=drp)
def manifold_ok(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); ok = all(len(e.link_faces) == 2 for e in bm.edges); bm.free(); return ok
TWIN = {0: 2, 2: 0, 3: 9, 9: 3, 4: 8, 8: 4, 5: 7, 7: 5}; MIRR = []
for i in range(10):    # a petal the cleanup could not close -> Blender mirror (y -> -y) of its clean mirror twin (the kilt is L/R symmetric)
    ob = bpy.data.objects[f"kilt_petal_{i:02d}_v333"]
    if manifold_ok(ob) or i not in TWIN: continue
    tw = bpy.data.objects[f"kilt_petal_{TWIN[i]:02d}_v333"]
    if not manifold_ok(tw): continue
    me = tw.data.copy(); me.transform(ob.matrix_world.inverted() @ Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ tw.matrix_world); me.flip_normals()
    old_me = ob.data; ob.data = me; bpy.data.meshes.remove(old_me); MIRR.append(i); log[f"{i:02d}"]["mirrored_from"] = TWIN[i]
log["_mirrored"] = MIRR; print("MIRRORED", MIRR, flush=True)
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP)
if bpy.data.collections.get("TMP_fuse"): bpy.data.collections.remove(bpy.data.collections["TMP_fuse"])
A = os.path.join(L.OUT, "asm"); mp_fn = os.path.join(A, "map.json"); mp = json.load(open(mp_fn))
for i in range(10):
    n = f"kilt_petal_{i:02d}"; L.export(bpy.data.objects[n + "_v333"], os.path.join(A, n + ".stl")); mp[n] = ["trunk_assembly", "green"]
json.dump(mp, open(mp_fn, "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v334.blend"))
print("KILT_DONE", json.dumps(log))
