"""v3.32 finalize body_v332.blend (no geometry change): rejected/duplicate objects moved to collection REJECTED_v332 (excluded from the
view layer, nothing deleted), viewport colours by print colour, thigh_sheet_b re-specified black (photo: no brown thigh), notes text block."""
import bpy, os, sys, json, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
import struct
def stl_vol(p):
    d = open(p, "rb").read(); n = struct.unpack("<I", d[80:84])[0]; v = 0.0
    for i in range(n):
        f = struct.unpack("<12f", d[84 + 50 * i: 84 + 50 * i + 48]); a, b, c = f[3:6], f[6:9], f[9:12]
        v += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return v
def ob_vol(o):
    bm = bmesh.new(); bm.from_mesh(o.data); v = bm.calc_volume(signed=True); bm.free(); return v
R = L.coll("REJECTED_v332"); rep = {"moved": []}
vt = stl_vol(os.path.join(L.OUT, "asm", "chest_vine.stl"))
vines = sorted([o for o in bpy.data.objects if o.name.startswith("chest_vine_v332")], key=lambda o: abs(ob_vol(o) - vt))
keep = vines[0] if vines else None
for o in list(bpy.data.objects):
    if o.name.startswith(("torso_shell_front_v332", "torso_shell_back_v332", "leaf_chest_0_v332")) or (o.name.startswith("chest_vine_v332") and o is not keep):
        L.link_to(o, R); rep["moved"].append(o.name)
if keep: keep.name = "chest_vine_v332"; rep["chest_vine_kept_vol_mm3"] = round(ob_vol(keep), 1); rep["chest_vine_stl_vol_mm3"] = round(vt, 1)
for lc in bpy.context.view_layer.layer_collection.children:
    if lc.name == "REJECTED_v332": lc.exclude = True
COL = {"black": (0.12, 0.12, 0.13, 1), "wood": (0.6, 0.42, 0.27, 1), "green": (0.31, 0.54, 0.24, 1)}
for o in bpy.data.objects:
    n = o.name.lower()
    if o.users_collection and o.users_collection[0].name in ("ARMS_v332", "LEGS_v332", "KILT_v332", "TORSO_v332"):
        o.color = COL["black"] if ("gripper" in n or "finger" in n or "sleeve" in n or "boot" in n) else COL["green"] if ("kilt" in n or "vine" in n) else COL["wood"]
    if n.startswith("thigh_sheet_b"): o.color = COL["black"]; o["print_colour"] = "black (v3.32 restyle: photo shows no brown thigh)"
t = bpy.data.texts.get("V332_NOTES") or bpy.data.texts.new("V332_NOTES"); t.clear()
t.write(open(os.path.join(L.HERE, "..", "CHANGED_PARTS_v332.md")).read() if os.path.exists(os.path.join(L.HERE, "..", "CHANGED_PARTS_v332.md")) else "see STATUS.md")
bpy.ops.wm.save_mainfile(filepath=os.path.join(L.HERE, "body_v332.blend")); print("FINAL", json.dumps(rep))
