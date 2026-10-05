| Metric | v3.18 | v3.19 |
|---|---|---|
| Total mass (kg) | 2.537 | 2.54 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 244.5 | 244.5 |
| Support margin front / back / side (mm) | 57 / 45 / 70 | 58 / 44 / 70 |
| Tipping angle side / front (deg) | 16.0 / 13.1 | 16.0 / 13.3 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.23 (0.46x) / 0.37 (0.75x) / 0.06 | 0.22 (0.45x) / 0.36 (0.74x) / 0.05 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.205 (0.42x) | 0.000 (0.00x) / 0.197 (0.40x) |
| Standing bus current (A) | 4.27 | 4.2 |
| Push survived, no controller F/B/L/R (N·s) | 1.34 / 1.05 / 1.64 / 1.66 | 1.36 / 1.03 / 1.64 / 1.66 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.50 / 0.91 / 1.69 / 1.71 | 1.48 / 0.91 / 1.69 / 1.71 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.00 / 0.00 | 0.00 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.182 m/s / 11.03 A | 100% / 0.177 m/s / 11.08 A |
| Walk energy-aware: success / speed / current | 100% / 0.150 m/s / 10.43 A | 100% / 0.148 m/s / 10.55 A |
| Head+arm test: fell / min margin / neck peak | no / 32.7 mm / n/a (no joint) N·m | no / 33.3 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.761 / 0.774 / 0.374 | 0.755 / 0.774 / 0.378 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
