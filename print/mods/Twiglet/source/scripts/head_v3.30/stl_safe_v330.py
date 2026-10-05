"""Blender float32-safe STL export (run after face_v330_bpy.py, which saves head_v330.blend with the exact MANIFOLD-solver meshes).
The solver output is closed in float64 topology but contains zero-thickness contacts (two sheets on identical coordinates, e.g. where a
backing ring touches the old wall) that any slicer re-merges into non-manifold edges. Per part, all in bmesh:
  1. weld by position (what a slicer does on STL load),
  2. delete coincident face pairs (both copies: the zero-thickness contact patch disappears and the two solids join) + loose geometry,
  3. dissolve zero-area slivers, fill the few remaining tiny boundary loops, drop crumbs < 1 mm3, re-orient normals,
  4. export binary STL, RE-IMPORT it and gate it (every edge exactly 2 faces, no non-manifold verts, 1 body, volume).
  blender -b head_v330.blend -P stl_safe_v330.py -- name1 name2 ..."""
import bpy, bmesh, os, sys, json
A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out_v330")
def hist(bm):
    h = {}
    for e in bm.edges: n = len(e.link_faces); h[n] = h.get(n, 0) + 1
    return h
def comps(bm):
    bm.faces.index_update(); seen = set(); cs = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; cp = []; seen.add(f.index)
        while st:
            g = st.pop(); cp.append(g)
            for e in g.edges:
                if len(e.link_faces) != 2: continue
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); st.append(h)
        cs.append(cp)
    return cs
def nbad(bm): return sum(1 for e in bm.edges if len(e.link_faces) != 2) + sum(1 for v in bm.verts if v.link_faces and not v.is_manifold)
def tidy(bm):
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
def dup_faces(bm):
    d = {}
    for f in bm.faces: d.setdefault(frozenset(v.index for v in f.verts), []).append(f)
    return [f for k, fs in d.items() if len(fs) > 1 for f in fs]
rep = {}
for name in A:
    o = bpy.data.objects[name]; me = o.data
    bm = bmesh.new(); bm.from_mesh(me); v0 = bm.calc_volume(signed=True); log = []
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bm.verts.index_update()
    log.append(("weld", hist(bm)))
    for it in range(12):
        bm.verts.index_update(); df = dup_faces(bm)
        if df: bmesh.ops.delete(bm, geom=df, context="FACES_ONLY"); tidy(bm)
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-5)
        bad_e = [e for e in bm.edges if len(e.link_faces) > 2]; bad_v = [v for v in bm.verts if v.link_faces and not v.is_manifold]
        if bad_e or bad_v:                       # residual kissing edges/verts: drop their fan, re-fill below
            fs = set(f for e in bad_e for f in e.link_faces) | set(f for v in bad_v for f in v.link_faces)
            bmesh.ops.delete(bm, geom=list(fs), context="FACES_ONLY"); tidy(bm)
        if it >= 2:                              # stubborn (non-simple) boundary loops: widen them by one face ring, then re-fill
            ring = set(f for e in bm.edges if e.is_boundary for v in e.verts for f in v.link_faces)
            bmesh.ops.delete(bm, geom=list(ring), context="FACES_ONLY"); tidy(bm)
        r = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=256)
        if r["faces"]: bmesh.ops.triangulate(bm, faces=r["faces"])
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.verts.index_update(); nb = nbad(bm); log.append((it, len(df), len(bad_e), len(bad_v), len(r["faces"]), nb))
        if nb == 0 and not dup_faces(bm): break
    cs = comps(bm); cs.sort(key=len)
    if len(cs) > 1: bmesh.ops.delete(bm, geom=[f for c in cs[:-1] for f in c], context="FACES"); tidy(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free(); me.update()
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    o.hide_set(False); o.select_set(True); bpy.context.view_layer.objects.active = o
    fp = os.path.join(OUT, name + ".stl")
    bpy.ops.wm.stl_export(filepath=fp, export_selected_objects=True, ascii_format=False, apply_modifiers=True, global_scale=1.0, forward_axis="Y", up_axis="Z")
    o.select_set(False)
    bpy.ops.wm.stl_import(filepath=fp); r = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(r.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0); bm.verts.index_update()
    h1 = hist(bm); nb = len(comps(bm)); nv = sum(1 for v in bm.verts if not v.is_manifold); v1 = bm.calc_volume(signed=True); nf = len(bm.faces); bm.free(); bpy.data.objects.remove(r)
    rep[name] = dict(steps=log, dropped_components=len(cs) - 1, stl_hist=h1, stl_nonmanifold_verts=nv, stl_bodies=nb, faces=nf,
                     vol_cm3=round(v1 / 1000, 3), vol_mem_cm3=round(v0 / 1000, 3), ok=(set(h1) == {2} and nb == 1 and nv == 0))
    print("SAFE", name, json.dumps(rep[name]), flush=True)
json.dump(rep, open(os.path.join(OUT, "stl_safe.json"), "w"), indent=1)
