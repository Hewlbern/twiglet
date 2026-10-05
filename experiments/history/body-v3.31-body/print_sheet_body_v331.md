# Twiglet body v3.31 (rev C) - print sheet (non-head parts)

Printer: Bambu P1S, 0.4 mm nozzle. Grams/hours are rough formula estimates (no slicer run) - slice to confirm.

Kilt petals: print v331_kilt_petal_00..09 (one each). Shins/boots/arms: print the L and R files (qty column = total).

| Part | File | Qty | Material | Orientation / supports | Walls / infill | Layer mm | est g each | est h each | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| torso_shell_front | v331_torso_shell_front.stl | 1 | PLA wood-brown (or wood-fill PLA) | split face down (as exported); tree supports only inside the two shoulder-boss holes; brim 5 mm | 3 walls, 15% gyroid | 0.2 | 23.6 | 1.84 | READY |
| torso_shell_back | v331_torso_shell_back.stl | 1 | PLA wood-brown | split face down; no supports | 3 walls, 15% gyroid | 0.2 | 23.9 | 1.85 | READY |
| leaf_cluster_shoulder | v331_leaf_cluster_shoulder.stl | 2 | PLA green | veined face down, peg up; no supports | 100% (thin) | 0.12 | 0.7 | 0.26 | READY |
| torso_frame | v331_torso_frame.stl | 1 | PLA+/PETG any colour (hidden) | back rail face down (as exported); tree supports under the hip deck, neck cradle and the two strut columns/gussets | 4 walls, 30% gyroid (load path) | 0.2 | 88.6 | 6.48 | READY |
| hip_cradle | v39_hip_cradle.stl | 1 | PLA/PETG any (hidden) | flipped, seats up; supports under the T-arms | 4 walls, 30% | 0.2 | 10.9 | 0.93 | READY |
| kilt_band | v331_kilt_band.stl | 1 | PLA wood-brown | upside down, no supports | 3 walls, 20% | 0.2 | 8.5 | 0.75 | READY |
| kilt_petals_00-09 | v331_kilt_petal_00.stl | 10 | PLA green (or TPU 95A) | upside down on the lip; no supports (flare <= 36 deg) | solid (~1.4 mm) | 0.16 | 8.5 | 1.37 | READY |
| hip_bracket_L/R | v39_hip_bracket_L.stl | 2 | PETG or PLA+ black | as exported (sleeve axis vertical); supports under the webs | 5 walls, 40% (load path) | 0.2 | 28.0 | 2.15 | READY |
| thigh_sheet_a | v39_thigh_sheet_a.stl | 2 | PLA wood-brown | flat | 4 walls, 40% | 0.2 | 4.7 | 0.48 | READY |
| thigh_sheet_b | v331_thigh_sheet_b.stl | 2 | PLA wood-brown | flat | 4 walls, 40% | 0.2 | 4.1 | 0.45 | READY |
| thigh_spacer | v39_thigh_spacer.stl | 2 | PLA black | flat | 4 walls, 40% | 0.2 | 5.0 | 0.51 | READY |
| shin_cover_front_L/R | v331_shin_cover_front_L.stl | 2 | PLA wood-brown | split face down; no supports | 3 walls, 15% | 0.2 | 5.3 | 0.53 | READY |
| shin_cover_back_L/R | v331_shin_cover_back_L.stl | 2 | PLA wood-brown | split face down; no supports | 3 walls, 15% | 0.2 | 5.7 | 0.56 | READY |
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

Ready total: 50 prints, about 517 g, about 52 h printer time (rough).
torso_frame rev B: the battery-pod tray/back rail is now joined to the hip deck by two 6 mm struts (bar + column + gusset per side, |y| 25-31).
  Print back-rail face down as exported; tree supports under the hip deck, the neck cradle and the strut columns (they run horizontally at 18-24 mm print height).
Torso shells rev B: clean slots over the frame top rails (z 85-87) and shoulder-rail collars (z 60-64) where the 0.25 mm frame cut left paper-thin skin; outer shape otherwise unchanged.
Kilt petals rev B/C: thickened OUTWARD to ~1.4 mm (inside/leg side and hinge lip unchanged); petals 05 + 07 have a small notch where the frame back-rail corners sat inside them (the rail itself is unchanged); petals 01 + 06 side edges thickened; >= 0.1 mm kept to the neighbouring petals.
Rev C thin-wall fixes (>= 1.2 mm where it does not touch a fit face): kilt_band rim +0.07 mm on the inside; shin covers front/back thin corners and back wall grown OUTWARD up to 0.6 mm (inner servo/leg faces, length and bed face unchanged); thigh_sheet_b 0.88 mm recess floor raised to 1.23 mm.
Still under 1.2 mm in places (left on purpose, fit features or decorative): thigh_spacer (0.5-0.6 mm under its 4 pin bores), hip_bracket (ligaments between the servo-horn bolt holes), shoulder_sleeve (fillet corners round the square arm bore + cable-slot sliver), boot (tapered cuff tip), leaves (feathered tips), torso_shell_back (v3.9 shoulder area, 12.8 -> 10.8 % of surface), remaining shin-cover lips/tabs (4-6 % of surface). Use 0.42 mm line width; the slicer's thin-wall/gap-fill handles these.
Not in this pack: head_yaw_to_roll + chin collars and head/wig/snout/bezels (head owner).
Superseded, do not print: v39_leaf_L (replaced by v331_leaf_cluster_shoulder), v39_hip_ring + v316_kilt_band (replaced by v331_kilt_band), v39_torso_frame (v331_torso_frame), v39_shin_cover_* (v331_shin_cover_*), v39_thigh_sheet_b (v331_thigh_sheet_b), v316_kilt_petal_* (v331_kilt_petal_*).
Shin sheets are stock Open Duck Mini v2 parts (print from the ODM repo).
