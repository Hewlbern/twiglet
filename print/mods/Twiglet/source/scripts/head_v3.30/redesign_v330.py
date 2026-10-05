"""v3.30 head-range redesign in Blender 4.5 (head_v330.blend): roll-bearing holder moved 12.1 mm forward on the same roll axis (deck-hung
housing, no strut below the shell), 4 collar screw tabs replaced by internal bosses (vertical M3 heat-set inserts) + collar screw ledges,
collars cut to the front band (|phi| <= 64), back-bottom rim band relieved (|phi| > 100, z < 118 link, hidden from the front),
head_yaw_to_roll rear re-cut (tower + hub 12.1 mm forward, rear ring sector replaced by a cross-bar + side arms).
Cutter / adder solids: redesign_v330/mk_redesign_parts.py. Inputs (pre-redesign v3.30a): redesign_v330/in/*.stl.
MANIFOLD Booleans, then the float32-safe export + re-import gate of trim_collars_v330.py -> out_v330/{head_lower, chin_collar_L/R, head_yaw_to_roll}.stl
+ out_v330/redesign.json; saves the scene (pre-redesign scene: redesign_v330/head_v330_preredesign.blend).
  blender -b blender/head_v330.blend -P blender/redesign_v330.py"""
import bpy, bmesh, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out_v330"); RD = os.path.join(HERE, "redesign_v330")
src = open(os.path.join(HERE, "trim_collars_v330.py")).read(); exec(src[src.index("def hist(bm)"):src.index('T = os.path.join(HERE, "trim_v330")')])
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
def vol(o):
    bm = bmesh.new(); bm.from_mesh(o.data); v = bm.calc_volume(signed=True); bm.free(); return v
def boolean(o, tool, op):
    md = o.modifiers.new(tool.name, "BOOLEAN"); md.operation = op; md.object = tool; md.solver = "MANIFOLD"
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=md.name)
T = coll("tools_redesign"); W = coll("v330_redesign"); rep = {}
def tool(n):
    k = imp(os.path.join(RD, n + ".stl"), "rd_" + n, T); k.hide_render = True; k.hide_set(True); return k
for o in list(W.objects): bpy.data.objects.remove(o)
jobs = {"head_lower": ("in/head_lower_v330a.stl", [("DIFFERENCE", "cut_holder"), ("DIFFERENCE", "cut_tabs"), ("DIFFERENCE", "cut_backrim"),
                                                   ("UNION", "add_housing"), ("UNION", "add_bosses"), ("DIFFERENCE", "cut_insert_holes"), ("UNION", "add_ballast_ledge")]),
        "chin_collar_L": ("in/chin_collar_L_v330a.stl", [("DIFFERENCE", "cut_collar_L"), ("UNION", "add_ledges_L")]),
        "chin_collar_R": ("in/chin_collar_R_v330a.stl", [("DIFFERENCE", "cut_collar_R"), ("UNION", "add_ledges_R")]),
        "head_yaw_to_roll": ("in/head_yaw_to_roll_v39.stl", [("DIFFERENCE", "cut_neck_rear"), ("UNION", "add_neck_rear")])}
for name, (fp, ops) in jobs.items():
    o = imp(os.path.join(RD, fp), name, W)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(o.data); bm.free()
    v0 = vol(o); steps = []
    for op, tn in ops: boolean(o, tool(tn), op); steps.append((op, tn, round(vol(o) / 1000, 3)))
    safe_export(name, OUT, rep); rep[name]["vol_before_cm3"] = round(v0 / 1000, 3); rep[name]["bool_steps"] = steps
    for o2 in list(bpy.data.objects):
        if o2.name.startswith("rd_"): pass
json.dump(rep, open(os.path.join(OUT, "redesign.json"), "w"), indent=1)
bpy.ops.wm.save_mainfile(filepath=os.path.join(HERE, "head_v330.blend"))
print("REDESIGN_DONE", json.dumps({k: (v["ok"], v["vol_before_cm3"], v["vol_cm3"], v["stl_bodies"]) for k, v in rep.items()}))
