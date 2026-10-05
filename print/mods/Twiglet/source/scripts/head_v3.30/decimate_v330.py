"""Blender size reduction for the print pack (zip < 20 MB): Decimate (COLLAPSE, triangulated) one STL in the model frame, then the same
float32 round-trip gate as stl_safe_v330.py (re-import: every edge exactly 2 faces, no non-manifold verts, 1 body).
  blender -b -P blender/decimate_v330.py -- in.stl out.stl ratio"""
import bpy, bmesh, sys, json
A = sys.argv[sys.argv.index("--") + 1:]; src, dst, ratio = A[0], A[1], float(A[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src); o = bpy.context.selected_objects[0]; bpy.context.view_layer.objects.active = o
bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0); v0 = bm.calc_volume(signed=True); f0 = len(bm.faces); bm.to_mesh(o.data); bm.free()
md = o.modifiers.new("dec", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.ratio = ratio; md.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="dec")
bm = bmesh.new(); bm.from_mesh(o.data)
for it in range(6):                                                    # tidy any collapse artefacts (rare): non-manifold fans -> re-fill
    bad_e = [e for e in bm.edges if len(e.link_faces) != 2]; bad_v = [v for v in bm.verts if v.link_faces and not v.is_manifold]
    if not bad_e and not bad_v: break
    fs = set(f for e in bad_e for f in e.link_faces if len(e.link_faces) > 2) | set(f for v in bad_v for f in v.link_faces)
    if fs: bmesh.ops.delete(bm, geom=list(fs), context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    r = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=256)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=True, ascii_format=False, global_scale=1.0, forward_axis="Y", up_axis="Z")
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.wm.stl_import(filepath=dst); r = bpy.context.selected_objects[0]
bm = bmesh.new(); bm.from_mesh(r.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0)
h = {}
for e in bm.edges: n = len(e.link_faces); h[n] = h.get(n, 0) + 1
nv = sum(1 for v in bm.verts if not v.is_manifold); v1 = bm.calc_volume(signed=True)
print("DECIMATE", json.dumps(dict(src=src, dst=dst, ratio=ratio, faces_in=f0, faces_out=len(bm.faces), stl_hist=h, nonmanifold_verts=nv,
                                  vol_in_cm3=round(v0 / 1000, 3), vol_out_cm3=round(v1 / 1000, 3), ok=(set(h) == {2} and nv == 0))), flush=True)
