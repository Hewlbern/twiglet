"""Labelled uneven-terrain fixtures. The flat model is never edited on disk.

Contact remains the existing MuJoCo boxes (soles, trunk, head) against these new
primitive geoms. Visual meshes do not collide. This is not mesh-to-ground contact.
"""
import math
import os
import mujoco

def _xml_path():
    from simlib import model_path
    return model_path("v3")

def grade_placement(angle_deg=2.0, length=0.85, thick=0.012, x_front=0.26):
    """Rotate a thin box about y so the top of the front edge is on z=0 and the far end rises.

    The first version put the bottom corner on z=0, which left a curb about one thickness
    high. That run is discarded. This placement is the one reported as grade_2deg.
    The underside of the box goes below the floor. Contact is still sole-box against this box.
    """
    a = math.radians(angle_deg)
    corners = [(sx * length / 2, sz * thick / 2) for sx in (-1.0, 1.0) for sz in (-1.0, 1.0)]
    def world_xz(x, z):
        c, s = math.cos(a), math.sin(a)
        return c * x + s * z, s * x + c * z
    front_top = world_xz(-length / 2, thick / 2)
    back_top = world_xz(length / 2, thick / 2)
    z_shift = -front_top[1]
    xs = [world_xz(x, z)[0] for x, z in corners]
    center_x = x_front - min(xs)
    qw, qy = math.cos(a / 2), math.sin(a / 2)
    lowest = min(world_xz(x, z)[1] for x, z in corners) + z_shift
    return dict(angle_deg=angle_deg, length_m=length, thick_m=thick, x_front_m=x_front,
                pos=[center_x, 0.0, z_shift], quat=[qw, 0.0, qy, 0.0],
                surface_front_m=round(front_top[1] + z_shift, 5),
                surface_back_m=round(back_top[1] + z_shift, 5),
                lowest_point_m=round(lowest, 5))

def catalogue():
    """Named fixtures. flat is the untouched AC model."""
    bumps = []
    for i, x in enumerate((0.32, 0.58, 0.84, 1.10, 1.36)):
        bumps.append(dict(name=f"bump_{i}", size=[0.045, 0.07, 0.002], pos=[x, 0.0, 0.002]))
    ridge = [dict(name="ridge", size=[0.012, 0.16, 0.003], pos=[0.42, 0.0, 0.003])]
    grade = grade_placement()
    return {
        "flat": dict(label="flat", note="unchanged AC floor plane", geoms=[]),
        "gentle_bumps_h4mm": dict(label="gentle_bumps_h4mm",
                                  note="five boxes, 4 mm tall, 90 mm by 140 mm, on the +x walk line. Felt only by sole/trunk/head boxes.",
                                  geoms=bumps, height_m=0.004),
        "gentle_ridge_h6mm": dict(label="gentle_ridge_h6mm",
                                  note="one transverse box, 6 mm tall, 24 mm along x, 320 mm across y.",
                                  geoms=ridge, height_m=0.006),
        "grade_2deg": dict(label="grade_2deg",
                           note="one box rotated 2 deg about y. Leading-edge height is in placement; not a smooth heightfield.",
                           placement=grade, geoms=[dict(name="grade", size=[grade["length_m"] / 2, 0.18, grade["thick_m"] / 2],
                                                         pos=grade["pos"], quat=grade["quat"])]),
    }

def compile_model(label):
    spec = mujoco.MjSpec.from_file(os.path.abspath(_xml_path()))
    meta = catalogue()[label]
    for gspec in meta["geoms"]:
        g = spec.worldbody.add_geom()
        g.name = "terrain_" + gspec["name"]
        g.type = mujoco.mjtGeom.mjGEOM_BOX
        g.size = list(gspec["size"])
        g.pos = list(gspec["pos"])
        if "quat" in gspec:
            g.quat = list(gspec["quat"])
        g.contype = 1
        g.conaffinity = 1
        g.rgba = [0.45, 0.38, 0.28, 1]
        g.friction = [0.8, 0.02, 0.001]
    model = spec.compile()
    return model, meta
