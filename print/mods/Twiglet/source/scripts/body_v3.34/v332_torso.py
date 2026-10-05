"""v3.32 torso  [FINAL: TOP_Z=95 -> shells NOT cut: trimming the dome detaches the inner neck collar that hugs the frame top at 0.15 mm (fit feature); only the chest vine is added]
 (Blender 4.2: blender -b body_v332.blend -P v332_torso.py), asm frame.
Photo: flat-topped wooden barrel with a black neck band visible between chin and torso, green vine running down the chest with leaves.
The photo torso also sits ~40 mm lower/taller, which needs the head/neck stack or ODM hip height to move (fixed) -> not attempted.
 - torso_shell_front/back: rev C shells with the narrow dome top removed above TOP_Z (95 -> 90): flatter barrel top, the black frame/neck
   (head_pitch_to_yaw) shows as a band under the chin like the photo; slots (top 88.3) stay closed (1.7 mm lip). Also more head-range room.
 - chest_vine (new, green, glued): 2.6 mm round vine following the front shell surface from the rim down to z 46 in a gentle S, its back
   conformed to the shell (shell subtracted) -> half-round strip.
 - leaf_chest_0 moved down 7 mm (and out to the surface) so it no longer sticks above the new rim (placement only)."""
import bpy, bmesh, os, sys, math, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
TOP = float(os.environ.get("TOP_Z", 95.0)); CUT = TOP < 94.9; VTOP = min(TOP - 1.5, 93.0); C = L.coll("TORSO_v332"); TMP = L.coll("TMP_v332_torso"); A = os.path.join(L.OUT, "asm"); P = os.path.join(L.OUT, "stl")
mp_fn = os.path.join(A, "map.json"); mp = json.load(open(mp_fn)); log = {}
sh = {}
for fb in ("front", "back"):     # rev C exported asm shells (watertight; the blend objects carry modifiers)
    o = L.imp(os.path.join(L.HERE, "in", f"asm_torso_shell_{fb}_v331.stl"), f"torso_shell_{fb}_v332", C)
    # bisect at TOP (drop everything above), then scanfill the cut boundary (handles C-shaped / annular sections with holes)
    bm = bmesh.new(); bm.from_mesh(o.data)
    if not CUT: bm.free(); sh[fb] = o; continue
    r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=Vector((0, 0, TOP)), plane_no=Vector((0, 0, 1)), clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(o.data); bm.free(); o.data.update(); L.clean(o, 1e-3); log[fb] = dict(boundary_edges=len(bnd), drop=L.drop_islands(o))
    sh[fb] = o
    if CUT: L.export(o, os.path.join(A, f"torso_shell_{fb}.stl")); mp[f"torso_shell_{fb}"] = ["trunk_assembly", "wood"]
    else: mp.pop(f"torso_shell_{fb}", None)
# vine path on the front surface
fr = sh["front"]; bm = bmesh.new(); bm.from_mesh(fr.data); tree = BVHTree.FromBMesh(bm)
def surf(y, z):
    h = tree.ray_cast(Vector((150, y, z)), Vector((-1, 0, 0)), 400)
    return h[0]
pts = []
for i in range(46):
    z = VTOP - i * (VTOP - 46.0) / 45.0; y = 3.0 + 7.0 * math.sin((TOP - z) / 44.0 * 1.5 * math.pi)
    p = surf(y, z)
    if p is not None: pts.append(p + Vector((0.5, 0, 0)))
cu = bpy.data.curves.new("vine_curve", "CURVE"); cu.dimensions = "3D"; sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
for q, p in zip(sp.points, pts): q.co = (p.x, p.y, p.z, 1.0)
cu.bevel_depth = 1.3; cu.bevel_resolution = 3; cu.use_fill_caps = True
co = bpy.data.objects.new("tmp_vine_curve", cu); TMP.objects.link(co); L.activate(co); bpy.ops.object.convert(target="MESH")
vine = bpy.context.view_layer.objects.active; vine.name = vine.data.name = "chest_vine_v332"; L.link_to(vine, C); L.clean(vine, 1e-3)
L.boolean(vine, fr, "DIFFERENCE"); L.clean(vine, 1e-3); log["vine_drop"] = L.drop_islands(vine, 20.0)
L.export(vine, os.path.join(A, "chest_vine.stl")); mp["chest_vine"] = ["trunk_assembly", "green"]
# print frame for the vine: lay its back (-x) on the bed -> rotate +90 deg about y (x->-z... ) and drop
Rp = Matrix.Rotation(math.radians(-90), 4, "Y"); vs = [Rp @ v.co for v in vine.data.vertices]
lo = Vector([min(p[i] for p in vs) for i in range(3)]); hi = Vector([max(p[i] for p in vs) for i in range(3)])
L.export(vine, os.path.join(P, "v332_chest_vine.stl"), Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))) @ Rp)
if CUT:
  # leaf_chest_0: down 7 mm, then out/in to keep the same standoff from the surface
  lf = bpy.data.objects["LeafChest0_v331"]; ln = L.dup(lf, "leaf_chest_0_v332", C); ln.data.transform(ln.matrix_world); ln.matrix_world = Matrix.Identity(4)
  c0 = sum((v.co for v in ln.data.vertices), Vector()) / len(ln.data.vertices); s0 = surf(c0.y, c0.z); s1 = surf(c0.y, c0.z - 7.0)
  dx = (s1.x - s0.x) if (s0 is not None and s1 is not None) else 0.0
  ln.data.transform(Matrix.Translation(Vector((dx, 0, -7.0)))); L.export(ln, os.path.join(A, "leaf_chest_0.stl")); mp["leaf_chest_0"] = ["trunk_assembly", "green"]
  log["leaf0_dx"] = round(dx, 2)
else: mp.pop("leaf_chest_0", None)
log["vine_pts"] = len(pts); log["cut"] = CUT
for ob in list(TMP.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(TMP); json.dump(mp, open(mp_fn, "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v332.blend")); print("TORSO_DONE", json.dumps(log))
