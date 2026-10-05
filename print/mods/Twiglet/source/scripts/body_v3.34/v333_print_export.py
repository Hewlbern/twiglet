"""re-export the v3.33 arm print frames from body_v333.blend (no re-modelling): same export_flat as v333_arms.py (fixed: proper rotation, the
left parts were written mirrored / inside-out) + export_print for gripper/finger.  blender -b body_v333.blend -P v333_print_export.py"""
import bpy, os, sys
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lib332 as L
P = os.path.join(L.OUT, "stl")
def export_flat(ob, path, R):
    M3 = Matrix((R.col[0], R.col[2], -R.col[1]))
    if M3.determinant() < 0: M3[0] = -M3[0]
    T = M3.to_4x4(); pts = [T @ v.co for v in ob.data.vertices]; lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    L.export(ob, path, Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))) @ T @ ob.matrix_world.inverted())
for s, sg in (("L", 1), ("R", -1)):
    a = Vector((0.0, -0.98, -0.17 * sg)).normalized(); o = (-a if s == "L" else a).normalized(); d = Vector((1, 0, 0)).cross(o).normalized()
    if d.z > 0: d = -d
    R = Matrix((Vector((1, 0, 0)), o, d)).transposed()
    for n in ("shoulder_sleeve", "elbow_sleeve", "leaf_shoulder", "leaf_elbow", "vine_upper", "vine_fore"):
        export_flat(bpy.data.objects[f"{n}_{s}_v333"], os.path.join(P, f"v333_{n}_{s}.stl"), R)
    for n in ("gripper_housing", "finger_moving"):
        L.export_print(bpy.data.objects[f"{n}_{s}_v333"], os.path.join(P, f"v333_{n}_{s}.stl"), f"{n}_{s}")
print("PRINT_EXPORT_DONE", flush=True)
