# Twiglet body v3.31 - print sheet (non-head parts)

Printer: Bambu P1S, 0.4 mm nozzle. Grams/hours are rough formula estimates (no slicer run) - slice to confirm.

Kilt petals: print v331_kilt_petal_00..09 (one each). Shins/boots/arms: print L and R files (qty column = total).

| Part | File | Qty | Material | Orientation / supports | Walls / infill | Layer mm | est g each | est h each | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| torso_shell_front | v331_torso_shell_front.stl | 1 | PLA wood-brown (or wood-fill PLA) | split face down (as exported); tree supports only inside the two shoulder-boss holes; brim 5 mm | 3 walls, 15% gyroid | 0.2 | 23.7 | 1.84 | READY |
| torso_shell_back | v331_torso_shell_back.stl | 1 | PLA wood-brown | split face down; no supports | 3 walls, 15% gyroid | 0.2 | 24.2 | 1.88 | READY |
| leaf_cluster_shoulder | v331_leaf_cluster_shoulder.stl | 2 | PLA green | veined face down, peg up; no supports | 100% (thin) | 0.12 | 0.7 | 0.26 | READY |
| torso_frame | v39_torso_frame.stl | 1 | PLA/PETG any colour (hidden) | battery-tray face down; tree supports under the deck and neck cradle | 4 walls, 30% gyroid (load path) | 0.2 | 85.6 | 6.27 | NEEDS CHANGE - not in pack (2 loose bodies: battery-pod tray/back rail island 26.6 mm from the frame; also degenerate faces) |
| hip_cradle | v39_hip_cradle.stl | 1 | PLA/PETG any (hidden) | flipped, seats up; supports under the T-arms | 4 walls, 30% | 0.2 | 10.9 | 0.93 | READY |
| kilt_band | v316_kilt_band.stl | 1 | PLA wood-brown | upside down, no supports | 3 walls, 20% | 0.2 | 8.4 | 0.75 | READY |
| kilt_petals_00-09 | v331_kilt_petal_00.stl | 10 | PLA green (or TPU 95A) | upside down on the lip; no supports (flare <= 36 deg) | solid (1.2 mm) | 0.16 | 6.6 | 1.1 | READY |
| hip_bracket_L/R | v39_hip_bracket_L.stl | 2 | PETG or PLA+ black | as exported (sleeve axis vertical); supports under the webs | 5 walls, 40% (load path) | 0.2 | 28.0 | 2.15 | READY |
| thigh_sheet_a | v39_thigh_sheet_a.stl | 2 | PLA wood-brown | flat | 4 walls, 40% | 0.2 | 4.7 | 0.48 | READY |
| thigh_sheet_b | v39_thigh_sheet_b.stl | 2 | PLA wood-brown | flat | 4 walls, 40% | 0.2 | 4.1 | 0.44 | READY |
| thigh_spacer | v39_thigh_spacer.stl | 2 | PLA black | flat | 4 walls, 40% | 0.2 | 5.0 | 0.51 | READY |
| shin_cover_front_L/R | v39_shin_cover_front_L.stl | 2 | PLA wood-brown | split face down; no supports | 3 walls, 15% | 0.2 | 5.2 | 0.52 | READY |
| shin_cover_back_L/R | v39_shin_cover_back_L.stl | 2 | PLA wood-brown | split face down; no supports | 3 walls, 15% | 0.2 | 5.6 | 0.55 | READY |
| boot_cuff | v39_boot_cuff.stl | 2 | PLA black | upright ring, no supports | 3 walls, 15% | 0.2 | 6.1 | 0.59 | READY |
| boot_L/R (wood grain) | v39_boot_L.stl | 2 | PETG or TPU 95A black (PLA ok) | sole down (open cavity under), no supports | 2-3 walls, 8-10% | 0.2 | 36.7 | 2.77 | READY |
| upper_arm_L/R | v39_upper_arm_L.stl | 2 | PLA wood-brown | outer plate face down, no supports | 4 walls, 30% | 0.2 | 3.0 | 0.36 | READY |
| shoulder_sleeve_L/R | v39_shoulder_sleeve_L.stl | 2 | PLA black | as exported, no supports | 4 walls, 30% | 0.2 | 5.0 | 0.51 | READY |
| forearm_L/R | v39_forearm_L.stl | 2 | PLA wood-brown | inner face down | 4 walls, 30% | 0.2 | 6.8 | 0.64 | READY |
| elbow_sleeve_L/R | v39_elbow_sleeve_L.stl | 2 | PLA black | as exported | 4 walls, 30% | 0.2 | 4.6 | 0.48 | READY |
| gripper_housing_L/R | v39_gripper_housing_L.stl | 2 | PLA/PETG black | inner (servo sleeve) face down; supports under the finger tip only | 4 walls, 30% | 0.2 | 16.5 | 1.33 | READY |
| finger_moving_L/R | v39_finger_moving_L.stl | 2 | PLA/PETG black | outer (hub) face down | 100% | 0.16 | 5.5 | 0.94 | READY |
| leaf_M (elbow + chest) | v39_leaf_M.stl | 3 | PLA green | veined face down, peg up | 100% | 0.12 | 0.3 | 0.2 | READY |
| leaf_S (vine) | v39_leaf_S.stl | 2 | PLA green | veined face down, peg up | 100% | 0.12 | 0.2 | 0.18 | READY |
| head_yaw_to_roll (neck mechanics) | v39_head_yaw_to_roll.stl | 1 | PLA+/PETG | as exported; supports per ODM guide | 4 walls, 40% | 0.2 | 20.7 | 1.63 | BLOCKED BY HEAD - not in pack (neck mechanics; confirm with the head owner) |

Ready total (all parts except frame + head_yaw_to_roll): 49 prints, about 410 g, about 42 h printer time (rough).
Not in this pack: torso_frame (needs change), head_yaw_to_roll + chin collars (head owner), head/wig/snout/bezels (head owner).
Superseded, do not print: v39_leaf_L (replaced by v331_leaf_cluster_shoulder), v39_hip_ring (replaced by v316_kilt_band).
Shin sheets are stock Open Duck Mini v2 parts (print from the ODM repo).
