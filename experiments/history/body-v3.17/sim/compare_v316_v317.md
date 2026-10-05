| Metric | v3.16 | v3.17 |
|---|---|---|
| Total mass (kg) | 2.518 | 2.547 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 243.1 | 245.1 |
| Support margin front / back / side (mm) | 57 / 45 / 70 | 57 / 45 / 70 |
| Tipping angle side / front (deg) | 16.1 / 13.1 | 16.0 / 13.0 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.23 (0.47x) / 0.37 (0.76x) / 0.07 | 0.23 (0.47x) / 0.38 (0.77x) / 0.07 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.216 (0.44x) | 0.000 (0.00x) / 0.211 (0.43x) |
| Standing bus current (A) | 4.33 | 4.33 |
| Push survived, no controller F/B/L/R (N·s) | 1.31 / 1.05 / 1.62 / 1.64 | 1.34 / 1.08 / 1.64 / 1.66 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.50 / 0.89 / 1.69 / 1.71 | 1.48 / 0.94 / 1.69 / 1.71 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.07 / 0.00 | 0.06 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.182 m/s / 11.29 A | 100% / 0.181 m/s / 10.87 A |
| Walk energy-aware: success / speed / current | 100% / 0.152 m/s / 10.53 A | 100% / 0.150 m/s / 10.44 A |
| Head+arm test: fell / min margin / neck peak | no / 30.6 mm / n/a (no joint) N·m | no / 33.6 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.749 / 0.772 / 0.369 | 0.771 / 0.775 / 0.377 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
