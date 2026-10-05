| Metric | v3.24 | v3.25 |
|---|---|---|
| Total mass (kg) | 2.556 | 2.575 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 245.4 | 246.5 |
| Support margin front / back / side (mm) | 58 / 44 / 70 | 58 / 44 / 70 |
| Tipping angle side / front (deg) | 16.0 / 13.2 | 15.9 / 13.3 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.22 (0.45x) / 0.37 (0.75x) / 0.06 | 0.22 (0.44x) / 0.36 (0.74x) / 0.04 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.196 (0.40x) | 0.000 (0.00x) / 0.187 (0.38x) |
| Standing bus current (A) | 4.22 | 4.16 |
| Push survived, no controller F/B/L/R (N·s) | 1.36 / 1.03 / 1.66 / 1.66 | 1.41 / 1.03 / 1.66 / 1.69 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.52 / 0.89 / 1.69 / 1.73 | 1.50 / 0.94 / 1.69 / 1.71 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.07 / 0.00 | 0.07 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.197 m/s / 11.53 A | 100% / 0.200 m/s / 11.5 A |
| Walk energy-aware: success / speed / current | 100% / 0.161 m/s / 10.82 A | 100% / 0.163 m/s / 10.82 A |
| Head+arm test: fell / min margin / neck peak | no / 32.1 mm / n/a (no joint) N·m | no / 32.4 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.764 / 0.777 / 0.373 | 0.774 / 0.778 / 0.378 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
