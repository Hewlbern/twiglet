| Metric | v3.23 | v3.24 |
|---|---|---|
| Total mass (kg) | 2.568 | 2.556 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 246.5 | 245.4 |
| Support margin front / back / side (mm) | 57 / 45 / 70 | 58 / 44 / 70 |
| Tipping angle side / front (deg) | 15.9 / 13.0 | 16.0 / 13.2 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.23 (0.47x) / 0.38 (0.77x) / 0.07 | 0.22 (0.45x) / 0.37 (0.75x) / 0.06 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.202 (0.41x) | 0.000 (0.00x) / 0.196 (0.40x) |
| Standing bus current (A) | 4.29 | 4.22 |
| Push survived, no controller F/B/L/R (N·s) | 1.36 / 1.08 / 1.66 / 1.69 | 1.36 / 1.03 / 1.66 / 1.66 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.50 / 0.94 / 1.71 / 1.73 | 1.52 / 0.89 / 1.69 / 1.73 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.07 / 0.00 | 0.07 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.195 m/s / 11.54 A | 100% / 0.197 m/s / 11.53 A |
| Walk energy-aware: success / speed / current | 100% / 0.162 m/s / 10.84 A | 100% / 0.161 m/s / 10.82 A |
| Head+arm test: fell / min margin / neck peak | no / 33.2 mm / n/a (no joint) N·m | no / 32.1 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.797 / 0.777 / 0.38 | 0.764 / 0.777 / 0.373 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
