# Twiglet v3.9 (from v3.8): clean snout root + head proportions

User request: "Make the nose not have a ring nearest the head, just have it connect as in the photo, and make sure the head is similar proportions to the photos head, in size, maybe it should be larger or more spherical? idk".

## Measured proportions (photos vs v3.8 / v3.9)

| Ratio | Photos | v3.8 | v3.9 |
|---|---|---|---|
| Head top to black collar / total height | 0.374 (0.342-0.393; original photo, perspective-corrected) | 0.327 (black chin collar starts 0.53 R below centre) | 0.354 (collar now wood: ball reads to the neck opening) |
| Visible ball height / width | 0.82 (original, corrected) | 0.765 | 0.83 |
| Head width / torso width (mid chest) | 2.2-2.4 (front + 3/4 photos) | 2.25 | 2.25 |
| Head width / torso width just under the neck | 2.4 (front) | 2.78 | 2.78 |
| Eye centre spacing / head width | 0.455 (front) | 0.46 | 0.46 |
| Snout OD / head width | 0.31-0.34 (front) | 0.32 | 0.32 |
| Head width / shoulder width | 1.09 (original; arms posed differently) | 1.28 | 1.28 |

Conclusion: at 210 mm the head width already matches the torso, eye and snout ratios. What made it look small and squashed was the 13.6 mm BLACK chin collar band (it read as neck, so the visible ball was only 0.765 x width tall). The photo head matches a 225-240 mm ball on head/total height, but that is ruled out by the STS3215 load: v3.8 was already at 0.279 N·m (1.76x rated 0.49). v3.9 keeps 210 mm and makes the chin collars wood-grained brown, so the ball reads 0.83 x width tall (photo 0.82) and head/total is 0.354, inside the photo range. A lighter snout brings static head pitch to 0.244 N·m (2.01x rated; 8x the 1.96 N·m stall).

## What changed
- **Snout root:** the 78 mm root flare/ring is gone. The straight tube (OD 68, lip 72, bore 45) now emerges from the ball with a 3 mm concave blend fillet, trimmed to the ball (R + 0.15) so it's flush all round. Axis 12 deg right / 6 deg down (v3.8: 16 / 11), so it sits a little higher and more forward. Length from the face is 72 mm (v3.8: 74). No internal void. It keeps the same keyed spigot + tab into the unchanged head_lower socket. The eye-bezel clearance cut shrank to a 43 mm3 sliver at the fillet edge (v3.8's flare notch was much bigger).
- **Chin collars:** same geometry, now with the head grain and printed wood brown instead of black.
- **Size, eyes, fringe, mounts, neck interface, display carriers:** unchanged (210 mm ball), so the P1S bed fit is unchanged (largest part head_lower 209 x 210 x 95 mm).

## Sims (v3.8 vs v3.9)

| Metric | v3.8 | v3.9 |
|---|---|---|
| Total mass (kg) | 2.442 | 2.423 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 241.6 | 241.1 |
| Support margin front / back / side (mm) | 51 / 50 / 70 | 54 / 48 / 70 |
| Tipping angle side / front (deg) | 16.2 / 12.0 | 16.2 / 12.6 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.28 (0.57x) / 0.42 (0.87x) / 0.14 | 0.25 (0.51x) / 0.39 (0.80x) / 0.11 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.279 (0.57x) | 0.000 (0.00x) / 0.244 (0.50x) |
| Standing bus current (A) | 4.86 | 4.57 |
| Push survived, no controller F/B/L/R (N·s) | 1.12 / 1.15 / 1.52 / 1.55 | 1.17 / 1.08 / 1.52 / 1.55 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.34 / 0.91 / 1.59 / 1.62 | 1.34 / 0.91 / 1.59 / 1.59 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.07 / 0.00 | 0.05 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.162 m/s / 11.79 A | 100% / 0.167 m/s / 11.61 A |
| Walk energy-aware: success / speed / current | 100% / 0.132 m/s / 10.89 A | 100% / 0.132 m/s / 10.63 A |
| Head+arm test: fell / min margin / neck peak | no / 31.5 mm / n/a (no joint) N·m | no / 33.0 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.744 / 0.774 / 0.362 | 0.724 / 0.771 / 0.363 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged in v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).


STS3215 check (rated 0.49 N·m continuous, ~1.96 N·m stall): static head pitch 0.244 N·m = 2.01x rated margin; head+arm test peaks 0.724 / 0.771 / 0.363 N·m (pitch / yaw / roll) = 0.37-0.39x stall.

Body parts changed vs v3.8: none (body STLs identical or grain-noise only) -> no body zip for v3.9; use twiglet-body-v3.8-stl.zip.
