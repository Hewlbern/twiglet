# Twiglet v3.11: straight conical snout (only the snout changed vs v3.9/v3.10)

Replaces v39_head_snout.stl / v310_head_snout.stl (everything else on the head is unchanged and reused: head_upper, head_lower, fringe, chin collars, bezels, carriers).

- Shape: STRAIGHT conical snout (funnel) on the v3.9 axis (12 deg to the robot's right, 6 deg down), 72 mm from the face. The outer surface is a straight cone from 56 mm OD at the root to 74 mm at the mouth (7.1 deg half-angle), with a 3 mm rounded mouth rim and no lip step. The bore is a cone too, 0.66 x OD (37 mm to 49 mm at the mouth, 1.6 mm inner round), 64 mm deep. There is a clean 3 mm concave blend onto the ball (no ring), flush-trimmed. Wood-grain rings run around the cone.
- Socket cover: the narrow root cannot cover the whole head_lower socket hole, so the snout carries a flush PLUG (the spigot footprint filled up to the ball surface, head grain continued). Around the hole edge there is a hairline seam (0.3 mm fit clearance) partly outside the cone root. Fill it with the glue squeeze-out or a dab of wood filler and sand flush.
- Size [73.0, 73.1, 93.4] mm, 162.3 cm3. Fits the P1S. Watertight: True, bodies: 1.
- Print: wood brown PLA (wood-fill optional), mouth face DOWN (flat annulus on the bed, as exported), spigot up, no supports, 0.2 mm (0.16 mm makes the grain pop), 2 walls (0.8 mm), 8 % gyroid: about 49 g (48.5 g in the sim; v3.9 52.6 g), static head pitch 0.238 N·m = 2.06x the STS3215 rating. 10 % infill is the ceiling: it gives about 0.245 N·m = 2.0x with no margin (0.246 N·m = 1.99x measured before the spigot trim). The part is mostly skin (2 walls plus grain), so extra infill adds weight quickly. At 3 walls / 15 % it would be ~70 g (~4.4 h), which is too heavy.
- Fit: the same keyed spigot + tab as v3.9 into the unchanged head_lower socket. Dry-fit so the tab sits in the key slot and the root lies flush on the ball, then glue (CA or epoxy). The cone axis is 2 mm off the socket centre on purpose; this keeps the seam mostly under the cone root and clears the right eye bezel.

## Sims v3.9 vs v3.11

| Metric | v3.9 | v3.11 |
|---|---|---|
| Total mass (kg) | 2.423 | 2.419 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 241.1 | 240.9 |
| Support margin front / back / side (mm) | 54 / 48 / 70 | 54 / 48 / 70 |
| Tipping angle side / front (deg) | 16.2 / 12.6 | 16.2 / 12.7 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.25 (0.51x) / 0.39 (0.80x) / 0.11 | 0.24 (0.50x) / 0.39 (0.79x) / 0.10 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.244 (0.50x) | 0.000 (0.00x) / 0.238 (0.49x) |
| Standing bus current (A) | 4.57 | 4.51 |
| Push survived, no controller F/B/L/R (N·s) | 1.17 / 1.08 / 1.52 / 1.55 | 1.17 / 1.05 / 1.52 / 1.55 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.34 / 0.91 / 1.59 / 1.59 | 1.31 / 0.94 / 1.55 / 1.57 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.05 / 0.00 | 0.05 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.167 m/s / 11.61 A | 100% / 0.170 m/s / 11.81 A |
| Walk energy-aware: success / speed / current | 100% / 0.132 m/s / 10.63 A | 100% / 0.144 m/s / 10.34 A |
| Head+arm test: fell / min margin / neck peak | no / 33.0 mm / n/a (no joint) N·m | no / 33.4 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.724 / 0.771 / 0.363 | 0.722 / 0.77 / 0.366 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).

Head nod (collide_head_v311.json): pitch -36..9 deg (11-12 at yaw +-45..90), roll +-9, yaw +-160, same as v3.9. Gaits: the v3.10-refined params, 100 % on both, no retune.
