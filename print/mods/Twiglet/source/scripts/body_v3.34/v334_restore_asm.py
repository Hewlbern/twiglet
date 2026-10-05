"""restore out/asm (+ map.json) of the v3.33 final (v333h) from body_v334.blend (copy of body_v333.blend) after the box restore lost out/:
base = frozen v3.32 asm (in/asm_v332), + v333 arm parts, kilt petals, black brackets (rev C geometry).  blender -b body_v334.blend -P v334_restore_asm.py"""
import bpy, os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
A = os.path.join(L.OUT, "asm"); os.makedirs(A, exist_ok=True); os.makedirs(os.path.join(L.OUT, "stl"), exist_ok=True)
I = os.path.join(L.HERE, "in", "asm_v332")
for f in os.listdir(I): shutil.copy(os.path.join(I, f), os.path.join(A, f))
mp = json.load(open(os.path.join(A, "map.json"))); C = L.coll("TMP_restore"); n_ = 0
for s in "LR":
    for n, ln, cls in ((f"shoulder_sleeve_{s}", f"upper_arm_{s}", "wood"), (f"elbow_sleeve_{s}", f"fore_arm_{s}", "wood"), (f"leaf_shoulder_{s}", f"upper_arm_{s}", "green"),
                       (f"leaf_elbow_{s}", f"fore_arm_{s}", "green"), (f"vine_upper_{s}", f"upper_arm_{s}", "green"), (f"vine_fore_{s}", f"fore_arm_{s}", "green"),
                       (f"gripper_housing_{s}", f"fore_arm_{s}", "black"), (f"finger_moving_{s}", f"finger_{s}", "black"), (f"vis_cable_{s}", f"fore_arm_{s}", "black")):
        L.export(bpy.data.objects[n + "_v333"], os.path.join(A, n + ".stl")); mp[n] = [ln, cls]; n_ += 1
    for n, ln in ((f"upper_arm_{s}", f"upper_arm_{s}"), (f"forearm_{s}", f"fore_arm_{s}")):
        ob = L.imp(os.path.join(L.REF, n + ".stl"), n + "_tmp_black", C); L.export(ob, os.path.join(A, n + ".stl")); mp[n] = [ln, "black"]; n_ += 1
for i in range(10):
    n = f"kilt_petal_{i:02d}"; L.export(bpy.data.objects[n + "_v333"], os.path.join(A, n + ".stl")); mp[n] = ["trunk_assembly", "green"]; n_ += 1
json.dump(mp, open(os.path.join(A, "map.json"), "w"), indent=1)
for ob in list(C.objects): bpy.data.objects.remove(ob, do_unlink=True)
bpy.data.collections.remove(C)
print("RESTORE_DONE", n_, len(mp), flush=True)
