# Twiglet v3.10: curved horn snout (only the snout changed vs v3.9)

Replaces v39_head_snout.stl (everything else on the head is unchanged and reused: head_upper, head_lower, fringe, chin collars, bezels, carriers).

- Shape: gently curved horn. The first 10 mm are straight (clean 3 mm blend fillet onto the ball, no ring), then it bends 15.5 deg up/outward. OD flares smoothly from 66 mm at the root to 74 mm at the mouth, with a 3 mm rounded mouth edge and no separate lip step. The bore widens with the flare from 41 mm (0.62 x OD) to 51 mm at the mouth (0.69 x OD, 1.6 mm inner round) and is 46 mm deep, which keeps the head-pitch load at the v3.9 level. Wood-grain rings follow the curved tube.
- Size [82.4, 74.2, 93.9] mm, 203.8 cm3. Fits the P1S. Watertight: True, bodies: 1.
- Print: wood brown PLA (wood-fill optional), mouth face DOWN (flat annulus on the bed, as exported), spigot up, no supports, 0.2 mm (0.16 mm makes the grain pop), 2 walls (0.8 mm), 8 % gyroid. Use these LIGHT settings: the STS3215 head-pitch 2x margin assumes them. That gives about 53 g (53.1 g in the sim; v3.9 snout 52.6 g). At 3 walls / 15 % it would be ~88 g and ~5.6 h, and the margin would drop below 2x.
- Fit: the same keyed spigot + tab as v3.9 into the unchanged head_lower socket. Dry-fit so the tab sits in the key slot and the root lies flush on the ball, then glue (CA or epoxy). The root is 2.5 mm off the socket centre by design (it covers the socket rim fully and clears the right eye bezel).

## Sims v3.9 vs v3.10

| Metric | v3.9 | v3.10 |
|---|---|---|
| Total mass (kg) | 2.423 | 2.424 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 241.1 | 241.1 |
| Support margin front / back / side (mm) | 54 / 48 / 70 | 54 / 48 / 70 |
| Tipping angle side / front (deg) | 16.2 / 12.6 | 16.2 / 12.6 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.25 (0.51x) / 0.39 (0.80x) / 0.11 | 0.25 (0.51x) / 0.39 (0.80x) / 0.11 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.244 (0.50x) | 0.000 (0.00x) / 0.245 (0.50x) |
| Standing bus current (A) | 4.57 | 4.57 |
| Push survived, no controller F/B/L/R (N·s) | 1.17 / 1.08 / 1.52 / 1.55 | 1.17 / 1.08 / 1.52 / 1.55 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.34 / 0.91 / 1.59 / 1.59 | 1.31 / 0.91 / 1.59 / 1.59 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.05 / 0.00 | 0.05 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.167 m/s / 11.61 A | 100% / 0.169 m/s / 11.82 A |
| Walk energy-aware: success / speed / current | 100% / 0.132 m/s / 10.63 A | 100% / 0.143 m/s / 10.37 A |
| Head+arm test: fell / min margin / neck peak | no / 33.0 mm / n/a (no joint) N·m | no / 33.1 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.724 / 0.771 / 0.363 | 0.725 / 0.771 / 0.361 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).

Head nod (collide_head_v310.json): pitch -36..9 deg (11-12 deg at yaw +-45..90), roll +-9, yaw +-160, same as v3.9; no snout contacts. Gaits: both re-refined (walk_refine.py), 100 % on 20 randomized trials.

Renders: renders/snout_closeup_photo_v39_v310.png, renders/snout_profile_v39_v310.png
