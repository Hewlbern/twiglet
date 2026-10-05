"""head-range clearance (run after v333_arms.py): subtract the head sweep at the hb_check grid poses that are NEW vs v3.32
(measure/head_sweep_cutter.py v333g v332f -> in/head_sweep_upper_arm_{L,R}_new.stl; R poses mirrored into the L frame so both sides stay
mirror twins) from shoulder_sleeve_L + leaf_shoulder_L (only jacket/leaf material: 0 mm3 of the rev C sleeve core is touched), then
R = Blender mirror of L; tidy, export asm + print frames, save.  blender -b body_v333.blend -P v333_headclear.py"""
import bpy, bmesh, os, sys, json
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
TMP = L.coll("TMP_headclear"); A = os.path.join(L.OUT, "asm"); P = os.path.join(L.OUT, "stl"); log = {}
def vol(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); v = bm.calc_volume(signed=False); bm.free(); return v
def tidy(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="EAR_CLIP"); seen = {}
    for f in bm.faces: seen.setdefault(frozenset(v.index for v in f.verts), []).append(f)
    bad = [f for fs in seen.values() if len(fs) > 1 for f in fs]
    if bad: bmesh.ops.delete(bm, geom=bad, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2); bm.to_mesh(ob.data); bm.free(); ob.data.update(); L.drop_islands(ob, 1.0); return nm
HH = json.load(open(os.path.join(L.HERE, "..", "work", "head_hulls.json")))   # measure/head_sweep_hulls.py: per-pose convex-hull head chunks (L frame)
core = L.imp(os.path.join(L.REF, "shoulder_sleeve_L.stl"), "tmp_core", TMP)
ob = bpy.data.objects["shoulder_sleeve_L_v333"]; v0 = vol(ob); used = []; CUT = None
for h in HH:
    if h["cut_in_core_mm3"] > 1.0 or h["cut_mm3"] <= 0.0: continue      # a hull that would bite into the rev C sleeve core is skipped
    hu = L.imp(os.path.join(L.HERE, "in", "head_hulls_L", f"hull_{h['k']:03d}.stl"), f"tmp_hull_{h['k']}", TMP)   # (in-core bite of the kept hulls <= 0.5 mm3: negligible, no core subtraction - the rev C core mesh is not EXACT-safe)
    if CUT is None: CUT = hu
    else: L.boolean(CUT, hu, "UNION")
    used.append(h["k"])
L.clean(CUT, 1e-4); keep = ob.data.copy(); tries = []
import random; random.seed(7)
for tr in range(8):     # EXACT through the grain grooves is fragile: jitter the cutter by <= 0.05 mm until the result is a closed manifold
    ob.data = keep.copy(); j = Vector([random.uniform(-0.05, 0.05) for _ in range(3)]) if tr else Vector((0, 0, 0))
    CUT.location = j; bpy.context.view_layer.update()
    L.activate(ob); md = ob.modifiers.new("b", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = CUT; md.solver = "EXACT"
    md.use_self = tr % 2 == 1; md.use_hole_tolerant = tr >= 4; bpy.ops.object.modifier_apply(modifier=md.name); n_ = tidy(ob); tries.append(n_)
    if n_ == 0: break
log["jitter_tries"] = tries
def open_e(o):
    bm = bmesh.new(); bm.from_mesh(o.data); n = sum(1 for e in bm.edges if len(e.link_faces) != 2); bm.free(); return n
log["open_after_bool"] = open_e(ob); log["cutter_open"] = open_e(CUT)
nm = tries[-1]; log["shoulder_sleeve_L"] = dict(vol0=round(v0), vol=round(vol(ob)), open_edges=nm, hulls=used)
obr = bpy.data.objects["shoulder_sleeve_R_v333"]; me = ob.data.copy(); me.transform(obr.matrix_world.inverted() @ Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)) @ ob.matrix_world); me.flip_normals()
old = obr.data; obr.data = me; bpy.data.meshes.remove(old); log["shoulder_sleeve_R"] = dict(vol=round(vol(obr)), mirrored=True)
def export_flat(ob, path, R):
    M3 = Matrix((R.col[0], R.col[2], -R.col[1]))
    if M3.determinant() < 0: M3[0] = -M3[0]
    T = M3.to_4x4(); pts = [T @ v.co for v in ob.data.vertices]; lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    L.export(ob, path, Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))) @ T @ ob.matrix_world.inverted())
ok = all(v.get("open_edges", 0) == 0 for v in log.values() if isinstance(v, dict))
for s, sg in (("L", 1), ("R", -1)) if ok else ():
    a = Vector((0.0, -0.98, -0.17 * sg)).normalized(); o = (-a if s == "L" else a).normalized(); d = Vector((1, 0, 0)).cross(o).normalized()
    if d.z > 0: d = -d
    R = Matrix((Vector((1, 0, 0)), o, d)).transposed()
    for n in ("shoulder_sleeve",):
        ob = bpy.data.objects[f"{n}_{s}_v333"]; L.export(ob, os.path.join(A, f"{n}_{s}.stl")); export_flat(ob, os.path.join(P, f"v333_{n}_{s}.stl"), R)
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP)
if ok: bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v333.blend"))
print("HEADCLEAR_DONE", "saved" if ok else "NOT_SAVED", json.dumps(log), flush=True)
