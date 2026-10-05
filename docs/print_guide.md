# Print guide

> This is based on the [Open Duck Mini v2 print guide](https://github.com/apirrone/Open_Duck_Mini/blob/v2/docs/print_guide.md). A verbatim copy is in [upstream/print_guide.md](upstream/print_guide.md).

You can find the `.stl` files under the `print/` directory at the root of this repo:
- the upstream Open Duck Mini v2 stock parts are in `print/`, unchanged
- our Twiglet parts are in `print/mods/Twiglet/`

Upstream rule for the stock parts: standard PLA with 15% infill, except `foot_bottom_tpu.stl`, which is TPU at 40% infill.

Our parts have their own settings, listed below. The head and wig settings are **required**: the sims assume them, and heavier prints break the head-pitch and balance margins.

Printer used for the checks: Bambu P1S with a 0.4 mm nozzle. Every part fits 256 × 256 × 256 mm. Every Twiglet STL is exported in its print orientation, with z = 0 on the bed.

## Parts to print

### Stock Open Duck Mini v2 parts (`print/`)

Used, unchanged:
- foot_top.stl x2
- foot_side.stl x2
- foot_bottom_pla.stl x2
- foot_bottom_tpu.stl x2 (TPU)
- knee_to_ankle_left_sheet.stl (TODO: count. Upstream prints x4, but our thighs use our own sheets.)
- knee_to_ankle_right_sheet.stl (TODO: count, as above)
- leg_spacer.stl (TODO: count. Upstream prints x4.)
- roll_motor_bottom.stl x2
- roll_motor_top.stl x2
- head_pitch_to_yaw.stl x1
- head_roll_mount.stl x1

Unknown (TODO):
- left_roll_to_pitch.stl / right_roll_to_pitch.stl: `v39_hip_bracket_L/R` probably replace them.
- left_cache.stl / right_cache.stl

**Not used** (replaced by Twiglet parts, or the feature is dropped):
- trunk_bottom, trunk_top → `v331_torso_frame` + `v39_hip_cradle`
- neck_left_sheet, neck_right_sheet: there has been no neck-pitch servo since v3.5
- head_yaw_to_roll → `v330_head_head_yaw_to_roll`
- head, head_bot_sheet → the head v3.30 parts
- left/right_antenna_holder: no antennas
- body_front, body_middle_bottom, body_middle_top, body_back, battery_pack_lid → the torso shells and frame
- bulb, flash_light_module, flash_reflector_interface, left_eye, right_eye, speaker_interface, speaker_stand → the digital eyes (TODO: speaker?)

### Twiglet: body v3.34 (`print/mods/Twiglet/body_v3.34/`)

This table comes from [print_sheet_body_v334.md](../print/mods/Twiglet/body_v3.34/print_sheet_body_v334.md), which also has gram and hour estimates (rough, no slicer run). Layers are in mm. "Wood-brown" can be wood-fill PLA.

| File | Qty | Material / colour | Layer | Walls / infill | Orientation / supports |
|---|---|---|---|---|---|
| `v333_shoulder_sleeve_L.stl` | 1 | PLA wood-brown (wood-fill ok) | 0.2 | 4 walls, 30% | outer cap face down (as exported); tree supports inside the open bottom / servo pocket |
| `v333_shoulder_sleeve_R.stl` | 1 | PLA wood-brown (wood-fill ok) | 0.2 | 4 walls, 30% | outer cap face down (as exported); tree supports inside the open bottom / servo pocket |
| `v333_elbow_sleeve_L.stl` | 1 | PLA wood-brown (wood-fill ok) | 0.2 | 4 walls, 30% | outer cap face down (as exported); tree supports inside the skirt / servo pocket |
| `v333_elbow_sleeve_R.stl` | 1 | PLA wood-brown (wood-fill ok) | 0.2 | 4 walls, 30% | outer cap face down (as exported); tree supports inside the skirt / servo pocket |
| `v334_gripper_housing_L.stl` | 1 | PLA/PETG black | 0.2 | 4 walls, 30% | box inner (body-side) face down (as exported, lay-flat); supports under the prong slot + finger opening |
| `v334_gripper_housing_R.stl` | 1 | PLA/PETG black | 0.2 | 4 walls, 30% | box inner (body-side) face down (as exported, lay-flat); supports under the prong slot + finger opening |
| `v333_finger_moving_L.stl` | 1 | PLA/PETG black | 0.16 | 4 walls, 100% | flat side down (as exported, lay-flat); no supports |
| `v333_finger_moving_R.stl` | 1 | PLA/PETG black | 0.16 | 4 walls, 100% | flat side down (as exported, lay-flat); no supports |
| `v333_leaf_shoulder_L.stl` | 1 | PLA green (or TPU 95A) | 0.12 | 2 walls, 100% | back face down; tree supports under the curled tip |
| `v333_leaf_shoulder_R.stl` | 1 | PLA green (or TPU 95A) | 0.12 | 2 walls, 100% | back face down; tree supports under the curled tip |
| `v333_leaf_elbow_L.stl` | 1 | PLA green (or TPU 95A) | 0.12 | 2 walls, 100% | back face down; tree supports under the curled tip |
| `v333_leaf_elbow_R.stl` | 1 | PLA green (or TPU 95A) | 0.12 | 2 walls, 100% | back face down; tree supports under the curled tip |
| `v333_vine_upper_L.stl` | 1 | PLA green | 0.12 | 2 walls, 100% | flat (1.6 mm strip), no supports; glue on the upper-arm block front face |
| `v333_vine_upper_R.stl` | 1 | PLA green | 0.12 | 2 walls, 100% | flat (1.6 mm strip), no supports; glue on the upper-arm block front face |
| `v333_vine_fore_L.stl` | 1 | PLA green | 0.12 | 2 walls, 100% | flat (1.6 mm strip), no supports; glue on the forearm block front face |
| `v333_vine_fore_R.stl` | 1 | PLA green | 0.12 | 2 walls, 100% | flat (1.6 mm strip), no supports; glue on the forearm block front face |
| `v334_kilt_petal_00.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_01.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_02.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_03.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_04.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_05.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_06.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_07.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_08.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v334_kilt_petal_09.stl` | 1 | PLA green (or TPU 95A) | 0.16 | 3 walls, 100% | upside down on the lip (as exported); leaf flares <= ~30 deg from vertical - no supports (brim 3 mm helps the narrow lip) |
| `v332_boot_L/R.stl` | 2 | PETG or TPU 95A black (PLA ok) | 0.2 | 3 walls, 10% | sole down; tree supports (build plate only) under the toe-cap underside |
| `v332_shin_cover_*_L/R.stl` | 4 | PLA wood-brown | 0.2 | 3 walls, 15% | split face down; no supports |
| `v332_chest_vine.stl` | 1 | PLA green | 0.12 | 2 walls, 100% | as exported, tree supports under the curl |
| `v39_upper_arm_L/R.stl` | 2 | PLA **BLACK** (v3.33) | 0.2 | 4 walls, 30% | outer plate face down, no supports |
| `v39_forearm_L/R.stl` | 2 | PLA **BLACK** (v3.33) | 0.2 | 4 walls, 30% | inner face down |
| `v331_kilt_band.stl` | 1 | PLA **GREEN** (v3.33) | 0.2 | 3 walls, 20% | upside down, no supports |
| `v331_torso_shell_front.stl` | 1 | PLA wood-brown (or wood-fill PLA) | 0.2 | 3 walls, 15% gyroid | split face down (as exported); tree supports only inside the two shoulder-boss holes; brim 5 mm |
| `v331_torso_shell_back.stl` | 1 | PLA wood-brown | 0.2 | 3 walls, 15% gyroid | split face down; no supports |
| `v331_torso_frame.stl` | 1 | PLA+/PETG any colour (hidden) | 0.2 | 4 walls, 30% gyroid (load path) | back rail face down (as exported); tree supports under the hip deck, neck cradle and the two strut columns/gussets |
| `v39_hip_cradle.stl` | 1 | PLA/PETG any (hidden) | 0.2 | 4 walls, 30% | flipped, seats up; supports under the T-arms |
| `v39_hip_bracket_L/R.stl` | 2 | PETG or PLA+ black | 0.2 | 5 walls, 40% (load path) | as exported (sleeve axis vertical); supports under the webs |
| `v39_thigh_sheet_a.stl` | 2 | PLA **BLACK** (v3.32 recolour; was wood-brown) | 0.2 | 4 walls, 40% | flat |
| `v331_thigh_sheet_b.stl` | 2 | PLA **BLACK** (v3.32 recolour; was wood-brown) | 0.2 | 4 walls, 40% | flat |
| `v39_thigh_spacer.stl` | 2 | PLA black | 0.2 | 4 walls, 40% | flat |
| `v39_boot_cuff.stl` | 2 | PLA black | 0.2 | 3 walls, 15% | upright ring, no supports |
| `v39_leaf_M.stl` | 1 | PLA green | 0.12 | 100% | veined face down, peg up |
| `v39_leaf_S.stl` | 2 | PLA green | 0.12 | 100% | veined face down, peg up |
Colour summary:
- **BLACK:** gripper_housing, finger_moving, upper_arm, forearm, boots, boot_cuff, thigh_spacer, hip_bracket, thigh_sheet_a/b
- **WOOD-BROWN:** shoulder/elbow sleeves, torso shells, shin covers
- **GREEN:** kilt petals, kilt_band, leaves, vines, chest vine
- **Any colour (hidden):** torso_frame, hip_cradle

Totals (rough): section A (arms and kilt) is about 271 g and 30 h. Section B is about 400 g and 34 h.

### Twiglet: head v3.30 (`print/mods/Twiglet/head_v3.30/`)

This table comes from [print_note_head_v330.md](../print/mods/Twiglet/head_v3.30/print_note_head_v330.md). The PETG is wood-brown, printed at 240–250 °C on a 70–80 °C bed (textured PEI with glue stick, part fan 30–50 %).

| File | Qty | Material / colour | Layer | Walls / infill | Orientation / supports |
|---|---|---|---|---|---|
| `v330_head_head_upper.stl` | 1 | PETG wood-brown | 0.16 | 2 walls (0.8 mm) + 3 top/3 bottom, **8 % gyroid**; modifier 4 walls / 40 % on the M3 insert bosses only | split-plane rim down (dome up); tree supports INSIDE only (crown) + the eye bores' top edge |
| `v330_head_head_lower.stl` | 1 | PETG wood-brown | 0.16 | as head_upper | split-plane rim down; tree supports inside the eye bores' upper edges |
| `v330_head_snout.stl` | 1 | PETG wood-brown | 0.2 (0.16 makes the grain pop) | 2 walls, **8 % gyroid** | mouth face down; no supports |
| `v330_head_chin_collar_L/R.stl` | 1 + 1 | PETG wood-brown | 0.16 | as head_upper | as exported (flat top face on the bed); no supports |
| `v330_head_eye_bezel_L/R.stl` | 1 + 1 | matte BLACK PLA | 0.16 | 2 walls, 8 % | front ring face down (textured PEI for a matte front); no supports |
| `v330_head_display_carrier_L/R.stl` | 1 + 1 | black PLA | 0.2 | 2 walls, 8 %; modifier 4 walls on the M3 holes | ring back face on the bed; no supports |
| `v330_head_head_yaw_to_roll.stl` | 1 | PLA+ / PETG (structural, hidden) | 0.2 | 4 walls, 40 % | yaw ring face on the bed; supports from the build plate under the rear frame and the roll hub |

`head_upper` (15.6 MB) and `head_lower` (20.0 MB) are the largest STLs in the repo. Both are under 25 MB.

### Twiglet: wig v3.44 (`print/mods/Twiglet/wig_v3.44/`)

| File | Qty | Material / colour | Layer | Walls / infill | Orientation / supports |
|---|---|---|---|---|---|
| `FINAL_WIG.stl` | 1 | yellow / blond matte PLA | 0.2 | 2 walls (0.8 mm), 3 top/3 bottom, **4.5 % LIGHTNING (required, the sims assume it)** | as exported (crown axis tilted 38°, the least-support of 6120 orientations searched); tree supports (auto, build plate only, 40° threshold, 0.2 mm top Z gap) + 5 mm brim |

- 186.2 g; size 243.1 × 246.4 × 239.9 mm (fits the P1S); ~473 cm³ support, 212 cm² overhang. Closed crown; walls ≥ 2.39 mm.
- Print `FINAL_WIG.stl`, not `FINAL_WIG_model_frame.stl` (that one is the same mesh in the head model frame, for the sims).
- A "4 %" infill figure was mentioned, but the records only show 4.5 % LIGHTNING. Use 4.5 %.

### Not printed
- Felt hat: fabric.
- Ballast: 25 g of steel.
- Wig pins: 3 mm rods.
- See [BOM.md](BOM.md).
