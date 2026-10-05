"""shared Blender helpers for the v3.32 body scripts (Blender 4.2, background)."""
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); REF = os.path.join(HERE, "in", "ref"); OUT = os.path.join(HERE, "out")
def coll(name):
    c = bpy.data.collections.get(name)
    if c is None: c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def link_to(o, c):
    for u in list(o.users_collection): u.objects.unlink(o)
    c.objects.link(o)
def imp(path, name, c=None):
    old = bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    bpy.ops.wm.stl_import(filepath=path); o = bpy.context.selected_objects[0]; o.name = o.data.name = name
    if c: link_to(o, c)
    clean(o); return o
def clean(o, dist=1e-4):
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(o.data); bm.free(); o.data.update()
def activate(o):
    for x in bpy.context.view_layer.objects: x.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
def boolean(o, other, op, solver="EXACT"):
    activate(o); m = o.modifiers.new("b", "BOOLEAN"); m.operation = op; m.object = other; m.solver = solver
    if solver == "EXACT": m.use_self = False; m.use_hole_tolerant = True
    bpy.ops.object.modifier_apply(modifier=m.name)
def apply_mods(o):
    activate(o)
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
def dup(o, name, c=None):
    n = o.copy(); n.data = o.data.copy(); n.name = n.data.name = name; (c or o.users_collection[0]).objects.link(n); return n
def box(name, lo, hi, c=None, bevel=0.0, seg=3):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector([lo[i] + (v.co[i] + 0.5) * (hi[i] - lo[i]) for i in range(3)])
    if bevel > 0: bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=bevel, segments=seg, affect="EDGES", profile=0.5)
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); (c or bpy.context.scene.collection).objects.link(o); return o
def export(o, path, M=None):
    os.makedirs(os.path.dirname(path), exist_ok=True); me = o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    import struct
    T = o.matrix_world if M is None else M @ o.matrix_world
    tris = []; me.calc_loop_triangles()
    for t in me.loop_triangles: tris.append([T @ me.vertices[i].co for i in t.vertices])
    with open(path, "wb") as f:
        f.write(b"\0" * 80); f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = (b - a).cross(c - a); n = n.normalized() if n.length > 0 else n
            f.write(struct.pack("<12fH", n.x, n.y, n.z, a.x, a.y, a.z, b.x, b.y, b.z, c.x, c.y, c.z, 0))
    o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
def load_T(key, fn="print_T.json"):
    J = json.load(open(os.path.join(HERE, "in", fn))); return Matrix(J[key])
def export_print(o, path, key):
    """print frame = inverse of the v3.9 print->asm registration (same bed orientation as the v3.9 part), then dropped to z=0 and centred in xy."""
    Ti = load_T(key).inverted(); me = o.data; T = Ti @ o.matrix_world
    zs = [(T @ v.co) for v in me.vertices]; lo = Vector([min(p[i] for p in zs) for i in range(3)]); hi = Vector([max(p[i] for p in zs) for i in range(3)])
    S = Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))) @ T
    export(o, path, S @ o.matrix_world.inverted())
def drop_islands(o, min_vol=50.0):
    """delete loose mesh islands with |volume| < min_vol mm3 (boolean slivers); returns list of dropped volumes."""
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table(); seen = set(); isl = []
    for f in bm.faces:
        if f.index in seen: continue
        stack = [f]; comp = []; seen.add(f.index)
        while stack:
            g = stack.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); stack.append(h)
        isl.append(comp)
    dropped = []
    for comp in isl:
        v = sum((f.calc_center_median().dot(f.normal) * f.calc_area()) for f in comp) / 3.0
        if abs(v) < min_vol: dropped.append(round(v, 3)); bmesh.ops.delete(bm, geom=comp, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data); bm.free(); o.data.update(); return dropped
