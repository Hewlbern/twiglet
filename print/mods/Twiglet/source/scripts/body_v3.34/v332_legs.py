"""v3.32 legs / boots / kilt (Blender 4.2: blender -b body_v332.blend -P v332_legs.py). All in the asm (rest) frame.
 - leg blocks (photo: brown wooden block below the kilt, ~60 x 55 mm): rev C shin covers (front+back, print frame v3.9) placed in asm via the
   v3.9->asm registration and extended DOWN by COVER_DZ (bottom vertices z < -139 moved), i.e. taller block over the ankle-servo top (same shin link).
 - boot_L/R: rev C/v3.9 boot + (a) sole rand: rounded 3 mm lip on the outer side, toe and heel (not the inner side), z -216.7..-209.2;
   (b) hollow rounded toe cap (half-ellipsoid shell, 2.2 mm wall) over the toe, minus the foot parts (+0.8 mm) so it only adds material outside the foot.
 - kilt petals: lower part stretched by KILT_DZ (z' = z - KILT_DZ * clamp((Z0 - z)/(Z0 - zmin))) -> hem lower, top/band/rails untouched.
Writes collections LEGS_v332 / KILT_v332, out/asm/*.stl, out/stl/v332_*.stl, out/asm/map.json."""
import bpy, bmesh, os, sys, math, json
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
CDZ = float(os.environ.get("COVER_DZ", 6.0)); KDZ = float(os.environ.get("KILT_DZ", 12.0)); KZ0 = float(os.environ.get("KILT_Z0", -8.0))
C = L.coll("LEGS_v332"); K = L.coll("KILT_v332"); TMP = L.coll("TMP_v332_legs"); A = os.path.join(L.OUT, "asm"); P = os.path.join(L.OUT, "stl"); log = {}
mp_fn = os.path.join(A, "map.json"); mp = json.load(open(mp_fn)) if os.path.exists(mp_fn) else {}
# ---- leg blocks
for s in "LR":
    for fb in ("front", "back"):
        n = f"shin_cover_{fb}_{s}"; src = bpy.data.objects[f"{n}_v331c"]
        o = L.dup(src, f"{n}_v332", C); o.matrix_world = Matrix.Identity(4); o.data.transform(L.load_T(n) @ src.matrix_world)
        zmin = min(v.co.z for v in o.data.vertices)
        for v in o.data.vertices:
            if v.co.z < zmin + 7.0: v.co.z -= CDZ
        o.data.update(); L.export(o, os.path.join(A, f"{n}.stl")); L.export_print(o, os.path.join(P, f"v332_{n}.stl"), n)
        mp[n] = [f"knee_and_ankle_assembly_{2 if s == 'L' else 4}", "wood"]
# ---- boots
for s, sg in (("L", 1), ("R", -1)):
    b = L.imp(os.path.join(L.REF, f"boot_{s}.stl"), f"boot_{s}_v332", C)
    xs = [v.co.x for v in b.data.vertices]; ys = [v.co.y for v in b.data.vertices]; x0, x1 = min(xs), max(xs)
    yin = min(ys) if s == "L" else max(ys); yout = max(ys) if s == "L" else min(ys)
    zb = min(v.co.z for v in b.data.vertices)
    lo = (x0 - 3.0, min(yin, yout + 3.0 * sg), zb); hi = (x1 + 3.0, max(yin, yout + 3.0 * sg), zb + 7.5)
    rand = L.box(f"tmp_rand_{s}", lo, hi, TMP)
    bm = bmesh.new(); bm.from_mesh(rand.data)
    ve = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1.0]
    bmesh.ops.bevel(bm, geom=ve, offset=17.0, segments=8, affect="EDGES", profile=0.5)
    te = [e for e in bm.edges if abs(e.verts[0].co.z - hi[2]) < 1e-3 and abs(e.verts[1].co.z - hi[2]) < 1e-3]
    bmesh.ops.bevel(bm, geom=te, offset=2.0, segments=3, affect="EDGES", profile=0.5)
    bm.to_mesh(rand.data); bm.free()
    # toe cap: half-ellipsoid shell over the toe
    def ell(name, c, r):
        me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
        for v in bm.verts: v.co = Vector((c[0] + v.co.x * r[0], c[1] + v.co.y * r[1], c[2] + v.co.z * r[2]))
        bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); TMP.objects.link(o); return o
    yc = (min(ys) + max(ys)) / 2
    cap = ell(f"tmp_cap_{s}", (x1 - 24.0, yc, -192.0), (25.0, 30.5, 13.0)); capi = ell(f"tmp_capi_{s}", (x1 - 24.0, yc, -192.0), (22.8, 28.3, 10.8))
    L.boolean(cap, capi, "DIFFERENCE")
    cut = L.box(f"tmp_cut_{s}", (x0 - 10, yc - 60, -260), (x1 + 10, yc + 60, -199.0), TMP); L.boolean(cap, cut, "DIFFERENCE")
    for fp in ("foot_top", "foot_side", "foot_bottom_pla", "foot_bottom_tpu"):
        f = L.imp(os.path.join(L.REF, f"foot_assembly{'' if s == 'L' else '_2'}__{fp}.stl"), f"tmp_{fp}_{s}", TMP)
        ctr = sum((v.co for v in f.data.vertices), Vector()) / len(f.data.vertices)
        for v in f.data.vertices:
            r = v.co - ctr; v.co = ctr + Vector((r.x * (1 + 0.8 / max(abs(r.x), 1)), r.y * (1 + 0.8 / max(abs(r.y), 1)), r.z * (1 + 0.8 / max(abs(r.z), 1)))) if r.length > 0 else v.co
        f.data.update(); L.boolean(cap, f, "DIFFERENCE"); L.boolean(rand, f, "DIFFERENCE")
    L.boolean(b, rand, "UNION"); L.boolean(b, cap, "UNION"); L.clean(b, 1e-3)
    L.export(b, os.path.join(A, f"boot_{s}.stl")); L.export_print(b, os.path.join(P, f"v332_boot_{s}.stl"), f"boot_{s}")
    mp[f"boot_{s}"] = [f"foot_assembly{'' if s == 'L' else '_2'}", "black"]
# ---- kilt petals
for i in range(10):
    src = bpy.data.objects[f"KiltPetal_{i:02d}"]; o = L.dup(src, f"KiltPetal_{i:02d}_v332", K)
    zmin = min((src.matrix_world @ v.co).z for v in src.data.vertices)
    o.matrix_world = Matrix.Identity(4); o.data.transform(src.matrix_world)
    for v in o.data.vertices:
        if v.co.z < KZ0: v.co.z -= KDZ * min(1.0, (KZ0 - v.co.z) / (KZ0 - zmin))
    o.data.update(); L.export(o, os.path.join(A, f"kilt_petal_{i:02d}.stl")); mp[f"kilt_petal_{i:02d}"] = ["trunk_assembly", "green"]
log["kilt"] = dict(KDZ=KDZ, KZ0=KZ0); log["covers"] = dict(CDZ=CDZ)
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP)
json.dump(mp, open(mp_fn, "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v332.blend")); print("LEGS_DONE", json.dumps(log))
