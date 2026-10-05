"""Loads the Blender-made face parts (blender/out_v330/*.stl, made by blender/face_v330_bpy.py) into the head chain caches
(.cache/snout_v330.pkl, .cache/eyes_v330.pkl) - no geometry editing here, only load + merge vertices + watertight / body checks."""
import os, json, pickle, trimesh
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(HERE, "blender", "out_v330")
info = json.load(open(os.path.join(OUT, "face_info.json"))); parts = {}; chk = {}
for k in ("head_upper", "head_lower", "eye_bezel_L", "eye_bezel_R", "display_carrier_L", "display_carrier_R", "snout"):
    m = trimesh.load(os.path.join(OUT, k + ".stl"), process=True); m.merge_vertices()
    parts[k] = m; chk[k] = dict(watertight=bool(m.is_watertight), bodies=len(m.split(only_watertight=False)), vol_cm3=round(m.volume / 1000, 2), faces=len(m.faces))
sn = dict(info["snout"]); sn.update(watertight=chk["snout"]["watertight"], bodies=chk["snout"]["bodies"], volume_cm3=chk["snout"]["vol_cm3"], made_in="Blender 4.2 (blender/face_v330_bpy.py)")
pickle.dump(dict(snout=parts.pop("snout"), info=sn), open(os.path.join(HERE, ".cache", "snout_v330.pkl"), "wb"))
ei = {k: v for k, v in info.items() if k != "snout"}; ei["checks"] = chk; ei["made_in"] = "Blender 4.2 (blender/face_v330_bpy.py)"
pickle.dump(dict(parts=parts, info=ei), open(os.path.join(HERE, ".cache", "eyes_v330.pkl"), "wb"))
print("LOAD_OK", json.dumps(chk))
