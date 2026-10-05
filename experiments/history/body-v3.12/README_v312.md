# Twiglet v3.12: gentler straight conical snout (only the snout changed)

Replaces v39/v310/v311_head_snout.stl (everything else on the head is unchanged and reused: head_upper, head_lower, fringe, chin collars, bezels, carriers).

- Shape: STRAIGHT gentle cone on the v3.9 axis (12 deg to the robot's right, 6 deg down), 72 mm from the face. The outer surface goes from 65 mm OD at the root to 72 mm at the mouth (2.8 deg half-angle, root/mouth 0.90; measured from the original photo as 0.88). The mouth has a 3 mm rounded rim and no lip step. The bore is a cone too, 0.66 x OD (43 mm to 47.5 mm at the mouth, 1.6 mm inner round), 64 mm deep. There is a clean 3 mm concave blend onto the ball (no ring), flush-trimmed. Wood-grain rings run around the cone.
- No plug and no seam (v3.11's plug is gone): the 65 mm root covers the head_lower socket the way v3.9 did (axis 2.5 mm off the socket centre; exposed socket-rim sliver 4.8 mm3, the same as v3.9). The spigot's top and key tab are trimmed flush with the ball.
- Size [71.6, 71.6, 93.4] mm, 174.3 cm3. Fits the P1S. Watertight: True, bodies: 1.
- Print: wood brown PLA (wood-fill optional), mouth face DOWN (flat annulus on the bed, as exported), spigot up, no supports, 0.2 mm (0.16 mm makes the grain pop), 2 walls (0.8 mm), 8 % gyroid: about 52 g (52.2 g in the sim; v3.9 52.6 g, v3.11 48.5 g). Static head pitch is 0.245 N·m = 2.00x the STS3215 rating (v3.9 0.244). There is no room for more infill: each extra 1 % adds ~1.9 g, ~0.004 N·m. At 3 walls / 15 % it would be ~76 g (~4.8 h), which is too heavy.
- Fit: the same keyed spigot + tab as v3.9 into the unchanged head_lower socket. Dry-fit so the tab sits in the key slot and the root lies flush on the ball, then glue (CA or epoxy). The cone axis is 2.5 mm off the socket centre on purpose; this covers the socket rim and clears the right eye bezel.

Photo taper measurement: measure/snout_taper_v312.json

## Sims v3.11 vs v3.12

| Metric | v3.11 | v3.12 |
|---|---|---|
| Total mass (kg) | 2.419 | 2.423 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 240.9 | 241.0 |
| Support margin front / back / side (mm) | 54 / 48 / 70 | 54 / 48 / 70 |
| Tipping angle side / front (deg) | 16.2 / 12.7 | 16.2 / 12.6 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.24 (0.50x) / 0.39 (0.79x) / 0.10 | 0.25 (0.51x) / 0.39 (0.80x) / 0.11 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.238 (0.49x) | 0.000 (0.00x) / 0.245 (0.50x) |
| Standing bus current (A) | 4.51 | 4.57 |
| Push survived, no controller F/B/L/R (N·s) | 1.17 / 1.05 / 1.52 / 1.55 | 1.17 / 1.08 / 1.52 / 1.55 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.31 / 0.94 / 1.55 / 1.57 | 1.31 / 0.91 / 1.59 / 1.59 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.05 / 0.00 | 0.05 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.170 m/s / 11.81 A | 100% / 0.172 m/s / 11.81 A |
| Walk energy-aware: success / speed / current | 100% / 0.144 m/s / 10.34 A | 100% / 0.143 m/s / 10.36 A |
| Head+arm test: fell / min margin / neck peak | no / 33.4 mm / n/a (no joint) N·m | no / 33.1 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.722 / 0.77 / 0.366 | 0.725 / 0.771 / 0.362 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).

Head nod (collide_head_v312.json): pitch -36..9 deg (11-12 at yaw +-45..90), roll +-9, yaw +-160, unchanged. Gaits: 100 % / 100 %, no retune.
