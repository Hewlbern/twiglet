"""Renders the assembly-guide step images (docs/images/assembly/*.png) from the v3.34 + wig v3.44 rest scene and the repo print STLs.
Exploded views: each part of a step is pushed away from the step centre along a fixed direction; the parts of the step are in colour,
everything already assembled is a faint grey ghost. The scene is a simulation/measurement scene: servos, bearings and boards are simple
proxies (dark grey), and items called "sim_*" are lumped masses, not printed parts.  usage: python render_assembly.py [step ...]"""
import os, sys, glob, numpy as np, pyvista as pv, trimesh
import geomlib as G
pv.OFF_SCREEN = True
REPO = os.path.dirname(os.path.dirname(G.HERE)); OUTD = os.path.join(REPO, "docs", "images", "assembly"); os.makedirs(OUTD, exist_ok=True)
PRINT = os.path.join(REPO, "print")
items, joints = G.load_scene()
COL = {"wood": "#a8743f", "black": "#2b2b2b", "green": "#3f9a3a", "yellow": "#e7c24a", "servo": "#4a5563", "pla": "#d8d8d8", "proxy": "#8a8f98", "frame": "#8fa8c4"}
def colour(ln, n, k):
    n = n.lower()
    if n == "head3_fringe": return COL["yellow"]
    if n.startswith("head3_"): return COL["black"] if ("bezel" in n or "carrier" in n) else COL["wood"]
    if k.startswith("repl_"): return COL[k[5:]] if k[5:] in COL else COL["pla"]
    if "kilt" in n or "leaf" in n or "vine" in n: return COL["green"]
    if k in ("servo", "sim_servo", "sim_s32") or n.startswith(("wj-", "s32")): return COL["servo"]
    if k.startswith("sim"): return COL["proxy"]
    if n in ("torso_frame", "hip_cradle"): return COL["frame"]
    if n in ("hip_bracket_l", "hip_bracket_r", "boot_cuff_l", "boot_cuff_r"): return COL["black"]
    if n in ("hip_cradle", "hip_ring"): return COL["pla"]
    return COL["pla"]
def pvmesh(V, F): return pv.PolyData(np.asarray(V, float), np.c_[np.full(len(F), 3), F].ravel())
def pick(pred): return [it for it in items if pred(*it[:3])]
def render(name, focus, ghost=(), explode=None, view=(1, -1, 0.6), labels=True, title=None, size=(1100, 820), zoom=1.0, label_map=None):
    p = pv.Plotter(off_screen=True, window_size=size); p.set_background("white")
    for ln, n, k, V, F in ghost: p.add_mesh(pvmesh(V, F), color="#c8c8c8", opacity=0.12, smooth_shading=False)
    pts, labs = [], []
    allV = np.vstack([np.asarray(V, float) for *_, V, F in focus]); c0 = (allV.min(0) + allV.max(0)) / 2
    for ln, n, k, V, F in focus:
        V = np.asarray(V, float); off = explode(ln, n, V, c0) if explode else np.zeros(3)
        p.add_mesh(pvmesh(V + off, F), color=colour(ln, n, k), smooth_shading=True, specular=0.2)
        if labels and not k.startswith("sim") and not n.startswith(("wj-", "s32", "drive_pal", "passive_pal")):
            lab = (label_map or {}).get(n, n.replace("head3_", ""))
            if lab and lab not in labs: pts.append((V.min(0) + V.max(0)) / 2 + off); labs.append(lab)
    if pts: p.add_point_labels(np.array(pts), labs, font_size=13, point_size=1, shape_opacity=0.55, always_visible=True, text_color="black", shape_color="white")
    if title: p.add_text(title, font_size=11, color="black", position="upper_left")
    p.camera_position = "iso"; d = np.array(view, float); d /= np.linalg.norm(d)
    p.camera.focal_point = c0; p.camera.position = c0 + d * 900; p.camera.up = (0, 0, 1); p.reset_camera(); p.camera.zoom(zoom)
    fn = os.path.join(OUTD, name + ".png"); p.screenshot(fn); p.close(); print("wrote", os.path.relpath(fn, REPO), flush=True)
def radial(f, axis=(1, 1, 0)):
    a = np.array(axis, float)
    def e(ln, n, V, c0):
        c = (V.min(0) + V.max(0)) / 2; v = (c - c0) * a; L = np.linalg.norm(v); return v / L * f if L > 1e-6 else np.zeros(3)
    return e
def along(table):
    def e(ln, n, V, c0):
        for key, off in table:
            if key in n or key == ln: return np.array(off, float)
        return np.zeros(3)
    return e
def parts_sheet(name, files, title, cols=4):
    """thumbnails of the print STLs (print orientation), labelled with file name and qty"""
    rows = (len(files) + cols - 1) // cols; p = pv.Plotter(off_screen=True, shape=(rows, cols), window_size=(300 * cols, 260 * rows), border=False); p.set_background("white")
    for i, (f, qty, col) in enumerate(files):
        p.subplot(i // cols, i % cols); m = trimesh.load(os.path.join(PRINT, f), force="mesh")
        p.add_mesh(pvmesh(m.vertices, m.faces), color=COL.get(col, col), smooth_shading=True)
        p.add_text(f"{os.path.basename(f)[:-4]}  x{qty}", font_size=8, color="black", position="upper_left"); p.camera_position = "iso"; p.reset_camera(); p.camera.zoom(1.25)
    fn = os.path.join(OUTD, name + ".png"); p.screenshot(fn); p.close(); print("wrote", os.path.relpath(fn, REPO), flush=True)
LEGL = ("hip_roll_assembly", "left_roll_to_pitch_assembly", "knee_and_ankle_assembly", "knee_and_ankle_assembly_2", "foot_assembly")
LEGR = ("hip_roll_assembly_2", "right_roll_to_pitch_assembly", "knee_and_ankle_assembly_3", "knee_and_ankle_assembly_4", "foot_assembly_2")
ARML = ("upper_arm_L", "fore_arm_L", "finger_L"); ARMR = ("upper_arm_R", "fore_arm_R", "finger_R")
HEADL = ("head_assembly",); NECK = ("neck_yaw_assembly", "head_pitch_to_yaw")
def link_in(*L): return lambda ln, n, k: ln in L
FR = "frame"
def trunk_core(ln, n, k): return ln == "trunk_assembly" and not n.startswith(("torso_shell", "kilt", "leaf_chest", "chest_vine", "hip_ring"))
STEPS = {}
def step(f): STEPS[f.__name__] = f; return f
@step
def s01_feet():
    parts_sheet("s01_feet_parts", [("foot_top.stl", 2, "pla"), ("foot_side.stl", 2, "pla"), ("foot_bottom_pla.stl", 2, "pla"), ("foot_bottom_tpu.stl", 2, "#555555"),
        ("mods/Twiglet/body_v3.34/v332_boot_L.stl", 1, "black"), ("mods/Twiglet/body_v3.34/v332_boot_R.stl", 1, "black"), ("mods/Twiglet/body_v3.34/v39_boot_cuff.stl", 2, "black")], "Step 1 - feet: stock ODM foot parts + Twiglet boot and cuff")
    render("s01_feet", pick(link_in("foot_assembly")), explode=along([("boot_cuff", (0, 0, 125)), ("boot_L", (0, 0, 70)), ("foot_top", (0, 0, 0)), ("foot_side", (0, -45, 0)), ("foot_bottom_tpu", (0, 0, -40)), ("foot_bottom_pla", (0, 0, -20))]),
           view=(1, -1.3, 0.5), title="Step 1 - left foot (exploded). Right foot = mirror.")
@step
def s02_shins():
    parts_sheet("s02_shins_parts", [("knee_to_ankle_left_sheet.stl", "2?", "pla"), ("knee_to_ankle_right_sheet.stl", "2?", "pla"), ("leg_spacer.stl", "2?", "pla"),
        ("mods/Twiglet/body_v3.34/v332_shin_cover_front_L.stl", 1, "wood"), ("mods/Twiglet/body_v3.34/v332_shin_cover_back_L.stl", 1, "wood"),
        ("mods/Twiglet/body_v3.34/v332_shin_cover_front_R.stl", 1, "wood"), ("mods/Twiglet/body_v3.34/v332_shin_cover_back_R.stl", 1, "wood")], "Step 2 - shins: stock sheets/spacer + wood shin-cover clamshell")
    render("s02_shins", pick(link_in("knee_and_ankle_assembly_2")), ghost=pick(link_in("foot_assembly")),
           explode=along([("shin_cover_front", (60, 0, 0)), ("shin_cover_back", (-60, 0, 0)), ("right_sheet", (0, -30, 0)), ("left_sheet", (0, 30, 0))]), title="Step 2 - left shin on the foot (covers exploded front/back)")
@step
def s03_thighs():
    parts_sheet("s03_thighs_parts", [("mods/Twiglet/body_v3.34/v39_thigh_sheet_a.stl", 2, "black"), ("mods/Twiglet/body_v3.34/v331_thigh_sheet_b.stl", 2, "black"),
        ("mods/Twiglet/body_v3.34/v39_thigh_spacer.stl", 2, "black")], "Step 3 - thighs: black thigh sheets a/b + thigh spacer", cols=3)
    render("s03_thighs", pick(link_in("knee_and_ankle_assembly")), ghost=pick(link_in("knee_and_ankle_assembly_2", "foot_assembly")),
           explode=along([("right_sheet", (0, -35, 0)), ("left_sheet", (0, 35, 0))]), title="Step 3 - left thigh (sheets exploded sideways); shin + foot ghosted",
           label_map={"v3_left_knee_to_ankle_left_sheet": "thigh sheet", "v3_left_knee_to_ankle_right_sheet": "thigh sheet", "v3_leg_spacer": "thigh spacer"})
@step
def s04_hips():
    parts_sheet("s04_hips_parts", [("roll_motor_top.stl", 2, "pla"), ("roll_motor_bottom.stl", 2, "pla"), ("mods/Twiglet/body_v3.34/v39_hip_bracket_L.stl", 1, "black"),
        ("mods/Twiglet/body_v3.34/v39_hip_bracket_R.stl", 1, "black")], "Step 4 - hips: stock roll_motor_top/bottom + black hip brackets", cols=4)
    render("s04_hips", pick(link_in("hip_roll_assembly", "left_roll_to_pitch_assembly")), ghost=pick(link_in("knee_and_ankle_assembly", "knee_and_ankle_assembly_2", "foot_assembly")),
           explode=along([("hip_bracket", (0, 40, 30))]), title="Step 4 - left hip (hip_roll + roll_to_pitch links); leg ghosted")
@step
def s05_trunk():
    parts_sheet("s05_trunk_parts", [("mods/Twiglet/body_v3.34/v331_torso_frame.stl", 1, "frame"), ("mods/Twiglet/body_v3.34/v39_hip_cradle.stl", 1, "frame")],
                "Step 5 - trunk: torso frame (battery tray, back rail, hip deck, neck cradle, shoulder bosses) + hip cradle", cols=2)
    render("s05_trunk", pick(trunk_core), explode=along([("hip_cradle", (0, 0, -60))]), view=(-0.6, -1, 0.7), title="Step 5 - torso frame + hip cradle (cradle dropped 60 mm); grey = sim proxies (servos, boards, battery)")
@step
def s06_legs_on_trunk():
    render("s06_legs_on_trunk", pick(lambda ln, n, k: ln in LEGL + LEGR or trunk_core(ln, n, k)), explode=lambda ln, n, V, c0: np.array([0, 0, -40.0]) if ln in LEGL + LEGR else np.zeros(3),
           view=(1, -1, 0.35), title="Step 6 - both legs on the hip cradle / torso frame (legs lowered 40 mm)", labels=False)
@step
def s07_electronics():
    render("s07_electronics", pick(lambda ln, n, k: ln == "trunk_assembly" and k.startswith("sim")), ghost=pick(trunk_core), view=(-1, -0.8, 0.6),
           title="Step 7 - trunk electronics as modelled (lumped sim proxies): servo bus board, IMU, battery pod in the tray (TODO exact layout)", labels=True,
           label_map={"sim_metal_trunk_assembly": "metal (sim)", "sim_servo_trunk_assembly": "servo (sim)", "sim_pcb_trunk_assembly": "boards (sim)", "sim_grey_trunk_assembly": "grey parts (sim)", "sim_s32_trunk_assembly": "STS3032 (sim)"})
@step
def s09_arms():
    A = "mods/Twiglet/body_v3.34/"
    parts_sheet("s09_arms_parts", [(A + "v333_shoulder_sleeve_L.stl", 1, "wood"), (A + "v39_upper_arm_L.stl", 1, "black"), (A + "v333_elbow_sleeve_L.stl", 1, "wood"), (A + "v39_forearm_L.stl", 1, "black"),
        (A + "v334_gripper_housing_L.stl", 1, "black"), (A + "v333_finger_moving_L.stl", 1, "black"), (A + "v333_leaf_shoulder_L.stl", 1, "green"), (A + "v333_leaf_elbow_L.stl", 1, "green"),
        (A + "v333_vine_upper_L.stl", 1, "green"), (A + "v333_vine_fore_L.stl", 1, "green")], "Step 9 - left arm parts (right arm = _R files)", cols=5)
    render("s09_arms", pick(link_in(*ARML)), ghost=pick(lambda ln, n, k: n.startswith("torso_shell")),
           explode=along([("leaf", (0, 30, 15)), ("vine", (25, 10, 0)), ("shoulder_sleeve", (0, 25, 10)), ("elbow_sleeve", (0, 25, 0)), ("gripper_housing", (0, 30, -45)), ("finger_moving", (0, 25, -85)), ("upper_arm_L", (0, 0, 0)), ("forearm_L", (0, 10, -20))]),
           view=(1, 1.4, 0.4), title="Step 9 - left arm (exploded outward): shoulder / elbow / gripper STS3032")
@step
def s08_torso_shells():
    render("s08_torso_shells", pick(lambda ln, n, k: ln == "trunk_assembly" and n.startswith(("torso_shell", "leaf_chest", "chest_vine"))),
           ghost=pick(lambda ln, n, k: trunk_core(ln, n, k) or ln in ARML + ARMR),
           explode=along([("torso_shell_front", (70, 0, 0)), ("leaf_chest", (110, 0, 0)), ("chest_vine", (110, 0, 0)), ("torso_shell_back", (-70, 0, 0))]), view=(0.2, -1, 0.35),
           title="Step 8 - torso shells (front / back split) + chest leaves, exploded along x")
@step
def s10_kilt():
    parts_sheet("s10_kilt_parts", [("mods/Twiglet/body_v3.34/v331_kilt_band.stl", 1, "green")] + [(f"mods/Twiglet/body_v3.34/v334_kilt_petal_{i:02d}.stl", 1, "green") for i in range(10)], "Step 10 - kilt band + 10 petals", cols=6)
    render("s10_kilt", pick(lambda ln, n, k: ln == "trunk_assembly" and (n.startswith("kilt") or n == "hip_ring")), ghost=pick(lambda ln, n, k: ln in LEGL + LEGR or trunk_core(ln, n, k) or n.startswith("torso_shell")),
           explode=radial(45), view=(1, -1, 0.9), title="Step 10 - kilt petals hooked on the band rim (exploded radially); 'hip_ring' = scene stand-in for the kilt band",
           label_map={"hip_ring": "kilt band (scene stand-in)"})
@step
def s11_neck():
    parts_sheet("s11_neck_parts", [("head_pitch_to_yaw.stl", 1, "pla"), ("mods/Twiglet/head_v3.30/v330_head_head_yaw_to_roll.stl", 1, "#777777"), ("head_roll_mount.stl", 1, "pla")],
                "Step 11 - neck / head mechanism: stock head_pitch_to_yaw + head_roll_mount, Twiglet head_yaw_to_roll", cols=3)
    render("s11_neck", pick(link_in(*NECK)), ghost=pick(lambda ln, n, k: trunk_core(ln, n, k) or n.startswith("torso_shell")), view=(1, -1, 0.5),
           title="Step 11 - head pitch / yaw stack on the fixed neck post (sim proxies; printed neck parts in the parts sheet)",
           label_map={"sim_grey_neck_yaw_assembly": "neck yaw stack (sim)", "sim_servo_neck_yaw_assembly": "head servos (sim)", "sim_wood_l_head_pitch_to_yaw": "head_pitch_to_yaw (sim)"})
@step
def s12_head_inside():
    H = "mods/Twiglet/head_v3.30/"
    parts_sheet("s12_head_parts", [(H + "v330_head_head_lower.stl", 1, "wood"), (H + "v330_head_head_upper.stl", 1, "wood"), (H + "v330_head_snout.stl", 1, "wood"),
        (H + "v330_head_chin_collar_L.stl", 1, "wood"), (H + "v330_head_chin_collar_R.stl", 1, "wood"), (H + "v330_head_display_carrier_L.stl", 1, "black"),
        (H + "v330_head_display_carrier_R.stl", 1, "black"), (H + "v330_head_eye_bezel_L.stl", 1, "black"), (H + "v330_head_eye_bezel_R.stl", 1, "black")], "Step 12-14 - head v3.30 parts", cols=5)
    render("s12_head_inside", pick(lambda ln, n, k: ln == "head_assembly" and n in ("head3_head_lower", "head3_display_carrier_L", "head3_display_carrier_R", "head3_chin_collar_L", "head3_chin_collar_R")),
           ghost=pick(link_in(*NECK)), explode=along([("display_carrier", (0, 0, 70)), ("chin_collar", (0, 0, -55))]), view=(1, -0.6, 1.1),
           title="Step 12 - head_lower: display carriers (lifted 70 mm), chin collars (dropped 55 mm)")
@step
def s13_head_close():
    render("s13_head_close", pick(lambda ln, n, k: ln == "head_assembly" and n.startswith("head3_") and n != "head3_fringe"),
           explode=along([("head_upper", (0, 0, 90)), ("eye_bezel", (55, 0, 40)), ("snout", (80, 0, 0))]), view=(1, -0.9, 0.5),
           title="Step 13 - close the head: head_upper (lifted 90 mm), bezels, snout (pulled forward 80 mm)")
@step
def s14_wig():
    parts_sheet("s14_wig_parts", [("mods/Twiglet/wig_v3.44/FINAL_WIG.stl", 1, "yellow")], "Step 14 - wig v3.44 (one piece, as printed)", cols=1)
    render("s14_wig", pick(lambda ln, n, k: ln == "head_assembly" and n.startswith("head3_")), explode=along([("fringe", (0, 0, 80))]), view=(1, -0.8, 0.45),
           title="Step 14 - wig v3.44 lifted 80 mm above head_upper (pins + keyed tongue; felt hat not modelled)", label_map={"head3_fringe": "wig v3.44"})
@step
def s15_complete():
    allp = pick(lambda ln, n, k: not n.startswith("sim_metal"))
    render("s15_complete_front", allp, view=(1, -0.55, 0.25), labels=False, title="Complete: body v3.34 + head v3.30 + wig v3.44 (rest pose; felt hat not modelled)")
    render("s15_complete_back", allp, view=(-1, 0.7, 0.35), labels=False, title="Complete, back view")
if __name__ == "__main__":
    for s in (sys.argv[1:] or list(STEPS)): STEPS[s]()
