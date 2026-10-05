"""v3.32 boots (Blender 4.2: blender -b body_v332.blend -P v332_boots.py), asm frame. boot_L/R = rev C/v3.9 boot (model-cache asm mesh) +
 (a) sole rand: rounded 3 mm lip on the outer side, toe and heel (inner side unchanged), 7.5 mm tall from the boot bottom, 17 mm plan radius;
 (b) hollow rounded toe cap (half-ellipsoid shell 25 x 30.5 x 13 mm, 2.2 mm wall, cut at z -199) over the toe.
 Clearance to the ODM foot: both additions minus the convex hull of foot_top+foot_side+foot bottoms, grown 1.2 % about its centroid (~0.8 mm)."""
import bpy, bmesh, os, sys, math, json
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
C = L.coll("LEGS_v332"); TMP = L.coll("TMP_v332_boots"); A = os.path.join(L.OUT, "asm"); P = os.path.join(L.OUT, "stl")
mp_fn = os.path.join(A, "map.json"); mp = json.load(open(mp_fn)); log = {}
def vol(o):
    bm = bmesh.new(); bm.from_mesh(o.data); v = bm.calc_volume(signed=True); bm.free(); return round(v / 1000, 2)
def ell(name, c, r):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
    for v in bm.verts: v.co = Vector((c[0] + v.co.x * r[0], c[1] + v.co.y * r[1], c[2] + v.co.z * r[2]))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); TMP.objects.link(o); return o
for s, sg in (("L", 1), ("R", -1)):
    b = L.imp(os.path.join(L.REF, f"boot_{s}.stl"), f"boot_{s}_v332", C); v0 = vol(b)
    xs = [v.co.x for v in b.data.vertices]; ys = [v.co.y for v in b.data.vertices]; x0, x1 = min(xs), max(xs)
    yin = min(ys) if s == "L" else max(ys); yout = max(ys) if s == "L" else min(ys); zb = min(v.co.z for v in b.data.vertices)
    lo = (x0 - 3.0, min(yin, yout + 3.0 * sg), zb); hi = (x1 + 3.0, max(yin, yout + 3.0 * sg), zb + 7.5)
    rand = L.box(f"tmp_rand_{s}", lo, hi, TMP)
    bm = bmesh.new(); bm.from_mesh(rand.data)
    ve = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1.0]
    bmesh.ops.bevel(bm, geom=ve, offset=17.0, segments=8, affect="EDGES", profile=0.5)
    te = [e for e in bm.edges if abs(e.verts[0].co.z - hi[2]) < 1e-3 and abs(e.verts[1].co.z - hi[2]) < 1e-3]
    bmesh.ops.bevel(bm, geom=te, offset=2.0, segments=3, affect="EDGES", profile=0.5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(rand.data); bm.free()
    # ring only: minus the boot outline inset 1.5 mm (rounded the same way), so the rand is a lip around the boot wall, not a slab
    ilo = (x0 + 1.5, min(ys) + 1.5, zb - 1.0); ihi = (x1 - 1.5, max(ys) - 1.5, zb + 9.0)
    inn = L.box(f"tmp_inn_{s}", ilo, ihi, TMP); bm = bmesh.new(); bm.from_mesh(inn.data)
    ve = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1.0]
    bmesh.ops.bevel(bm, geom=ve, offset=15.5, segments=8, affect="EDGES", profile=0.5); bm.to_mesh(inn.data); bm.free()
    L.boolean(rand, inn, "DIFFERENCE")
    yc = (min(ys) + max(ys)) / 2
    cap = ell(f"tmp_cap_{s}", (x1 - 24.0, yc, -192.0), (25.0, 30.5, 13.0)); capi = ell(f"tmp_capi_{s}", (x1 - 24.0, yc, -192.0), (22.8, 28.3, 10.8))
    L.boolean(cap, capi, "DIFFERENCE")
    cut = L.box(f"tmp_cut_{s}", (x0 - 10, yc - 60, -260), (x1 + 10, yc + 60, -199.0), TMP); L.boolean(cap, cut, "DIFFERENCE")
    # foot proxy: convex hull of the foot parts, grown 1.2 %
    bm = bmesh.new()
    for fp in ("foot_top", "foot_side", "foot_bottom_pla", "foot_bottom_tpu"):
        f = L.imp(os.path.join(L.REF, f"foot_assembly{'' if s == 'L' else '_2'}__{fp}.stl"), f"tmp_{fp}_{s}", TMP)
        for v in f.data.vertices: bm.verts.new(v.co)
    bm.verts.ensure_lookup_table(); res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    dv = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if dv: bmesh.ops.delete(bm, geom=dv, context="VERTS")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    ctr = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    for v in bm.verts: v.co = ctr + (v.co - ctr) * 1.012
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); me = bpy.data.meshes.new(f"tmp_hull_{s}"); bm.to_mesh(me); bm.free()
    hull = bpy.data.objects.new(me.name, me); TMP.objects.link(hull)
    L.boolean(cap, hull, "DIFFERENCE"); L.boolean(rand, hull, "DIFFERENCE")
    vr, vc = vol(rand), vol(cap)
    L.boolean(b, rand, "UNION"); L.boolean(b, cap, "UNION"); L.clean(b, 1e-3); dr = L.drop_islands(b)
    log[s] = dict(dropped=dr, boot0=v0, rand=vr, cap=vc, boot=vol(b))
    L.export(b, os.path.join(A, f"boot_{s}.stl")); L.export_print(b, os.path.join(P, f"v332_boot_{s}.stl"), f"boot_{s}")
    mp[f"boot_{s}"] = [f"foot_assembly{'' if s == 'L' else '_2'}", "black"]
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP); json.dump(mp, open(mp_fn, "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v332.blend")); print("BOOTS_DONE", json.dumps(log))
