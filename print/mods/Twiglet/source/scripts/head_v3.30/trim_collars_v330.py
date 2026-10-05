"""v3.30 chin-collar side-hem relief in Blender 4.5 (head_v330.blend): imports the v3.29/v3.30 chin collars (model frame) into the collection
"v330_collar_trim", the hem cutters (trim_v330/collar_cutter_L/R.stl, made by trim_v330/mk_collar_cutters.py) into "tools", applies a MANIFOLD
Boolean DIFFERENCE (+ a clearance notch under the snout root: snout convex hull x1.02, trim_v330/snout_clear_cutter.stl; the v3.30 re-aimed snout
lower rim overlapped the collar top-front edge by 0.6 mm3), then the same float32-safe export + re-import gate as stl_safe_v330.py -> out_v330/chin_collar_L/R.stl + out_v330/collar_trim.json,
and saves the scene (the untrimmed scene is kept as trim_v330/head_v330_pretrim.blend).
  blender -b blender/head_v330.blend -P blender/trim_collars_v330.py"""

import bpy, bmesh, os, sys, json
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
def safe_export(name, OUT, rep):
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

T = os.path.join(HERE, "trim_v330")
def coll(n):
    c = bpy.data.collections.get(n)
    if c is None: c = bpy.data.collections.new(n); bpy.context.scene.collection.children.link(c)
    return c
def imp(fp, name, col):
    old = bpy.data.objects.get(name)
    if old is not None: bpy.data.objects.remove(old)
    bpy.ops.wm.stl_import(filepath=fp); o = bpy.context.selected_objects[0]; o.name = name; o.data.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); return o
rep = {}
SNC = imp(os.path.join(T, "snout_clear_cutter.stl"), "collar_snout_clearance", coll("tools")); SNC.hide_render = True
for sd in "LR":
    o = imp(os.path.join(T, f"chin_collar_{sd}_v329.stl"), f"chin_collar_{sd}", coll("v330_collar_trim"))
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); v_before = bm.calc_volume(signed=True); bm.to_mesh(o.data); bm.free()
    k = imp(os.path.join(T, f"collar_cutter_{sd}.stl"), f"collar_hem_cutter_{sd}", coll("tools")); k.hide_render = True
    md = o.modifiers.new("hem", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = k; md.solver = "MANIFOLD"
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="hem")
    md = o.modifiers.new("snout_clear", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = SNC; md.solver = "MANIFOLD"   # v3.30 snout (re-aimed) dipped 0.8 mm into the collar top-front edge
    bpy.ops.object.modifier_apply(modifier="snout_clear")
    safe_export(f"chin_collar_{sd}", OUT, rep); rep[f"chin_collar_{sd}"]["vol_before_cm3"] = round(v_before / 1000, 3)
json.dump(rep, open(os.path.join(OUT, "collar_trim.json"), "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(HERE, "head_v330.blend"))
print("TRIM_DONE", json.dumps({k: (v["ok"], v["vol_before_cm3"], v["vol_cm3"], v["stl_bodies"]) for k, v in rep.items()}))
