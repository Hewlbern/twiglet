# Twiglet body v3.8 (from v3.7)

User request: "are the legs chonky enough, and can you make the back more cone like, and make the nose fit better and be more like in the image".

## What changed
1. **Legs:** in the photos the shin block is ~0.26-0.30 x head wide (55-63 mm) and about as tall as the gap between knee and boot. v3.7's C clip was 38 x 52 x 25 mm (width 0.25 x head). v3.8 uses a chunky rounded clamshell block, 56 (x) x 61 (y) x 30.5 (z) mm, outboard-biased, with an open bottom that swallows the top of the boot cuff, plus grain. The height is capped by the knee-servo sweep above and the cuff/ankle below. The thigh stays stock: in every photo the thigh is under the kilt and the visible 'knee' is the black servo. Inward hip roll is still 10 degrees (boot vs boot; the gait needs 9.1).
2. **Back:** clean cone (torso_env_v38.py). The back is a straight line from x -78 at the waist to -63 at the shoulder. The back-half sections are superellipses between the side width and that line, clamped to the internals + 4 mm. To make room: the two boards lean against the back at 13.4 degrees (was upright at x -75.8, z 15-48), the power switch moves under the kilt beside the battery pod, the back rail is cut to z 24 and the hip deck is trimmed at the yaw slings. The upright hip-yaw servos stay put (they set the top of the back: -63 at z 88).
3. **Snout:** new photo-matched snout (head_v38.py): OD 68 mm (0.32 x head), lip OD 72 mm with a slight bell and a rounded lip, bore 45 mm (0.66 x OD, thick rim as in the photos), 74 mm from the face. Barely tapered, with a root fillet (D 78) flaring onto the face. The axis points 16 degrees to the robot's right and 11 degrees down (v3.7: OD 65 thin-walled, bore 56, 28 degrees / 8 degrees). **Fit:** v3.7's root started only ~10 mm inside the ball along a 28-degree-yawed axis, so on one side it floated off the face (a crescent gap). v3.8 starts the root deep and trims it by the ball (R + 0.15 mm), so it sits flush all round. It keeps the keyed spigot + key tab into the **unchanged** head_lower socket (keyed seat; glue), so head_lower is not reprinted. A sealed internal void (2.6 mm skins) keeps it light. Wood grain rings run around the tube.

## Sim comparison (v3.7 vs v3.8)

| Metric | v3.7 | v3.8 |
|---|---|---|
| Total mass (kg) | 2.417 | 2.442 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 241.4 | 241.6 |
| Support margin front / back / side (mm) | 56 / 46 / 70 | 51 / 50 / 70 |
| Tipping angle side / front (deg) | 16.2 / 13.1 | 16.2 / 12.0 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.22 (0.46x) / 0.36 (0.73x) / 0.07 | 0.28 (0.57x) / 0.42 (0.87x) / 0.14 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.222 (0.45x) | 0.000 (0.00x) / 0.279 (0.57x) |
| Standing bus current (A) | 4.3 | 4.86 |
| Push survived, no controller F/B/L/R (N·s) | 1.22 / 1.01 / 1.52 / 1.55 | 1.12 / 1.15 / 1.52 / 1.55 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.38 / 0.84 / 1.59 / 1.59 | 1.34 / 0.91 / 1.59 / 1.62 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.00 / 0.05 | 0.07 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.166 m/s / 11.33 A | 100% / 0.162 m/s / 11.79 A |
| Walk energy-aware: success / speed / current | 100% / 0.135 m/s / 10.62 A | 100% / 0.132 m/s / 10.89 A |
| Head+arm test: fell / min margin / neck peak | no / 30.6 mm / n/a (no joint) N·m | no / 31.5 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.703 / 0.77 / 0.362 | 0.744 / 0.774 / 0.362 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged in v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).


Collisions (collide_v3.py, collide_log_v38.txt): see the report in the final summary.

## Files
- stl/v38_*.stl (body + copies of the head parts), stl_head_v38/ (head pack), print_sheet_body_v38.md, print_sheet_head_v38.md, changed_parts_v37_to_v38.json, build_report.json, collide_report.json
- renders/: compare_photo_v37_v38.png, v38_vs_new_photos.png, snout_closeup_photo_v37_v38.png, v38_snout_side.png, legs_photo_v37_v38.png, v38_back_three_quarter_nokilt.png, v38_three_quarter_*.png
