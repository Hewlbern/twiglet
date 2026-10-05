| Metric | v3.13 | v3.14 |
|---|---|---|
| Total mass (kg) | 2.439 | 2.486 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 242.0 | 245.9 |
| Support margin front / back / side (mm) | 54 / 48 / 70 | 55 / 47 / 70 |
| Tipping angle side / front (deg) | 16.2 / 12.6 | 15.9 / 12.6 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.25 (0.51x) / 0.39 (0.79x) / 0.10 | 0.24 (0.50x) / 0.39 (0.79x) / 0.09 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.237 (0.48x) | 0.000 (0.00x) / 0.219 (0.45x) |
| Standing bus current (A) | 4.53 | 4.45 |
| Push survived, no controller F/B/L/R (N·s) | 1.20 / 1.08 / 1.55 / 1.57 | 1.24 / 1.08 / 1.59 / 1.59 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.34 / 0.91 / 1.59 / 1.59 | 1.34 / 0.98 / 1.62 / 1.64 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.05 / 0.00 | 0.05 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.175 m/s / 11.36 A | 100% / 0.178 m/s / 11.36 A |
| Walk energy-aware: success / speed / current | 100% / 0.143 m/s / 10.35 A | 100% / 0.144 m/s / 10.32 A |
| Head+arm test: fell / min margin / neck peak | no / 34.9 mm / n/a (no joint) N·m | no / 26.6 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.731 / 0.774 / 0.369 | 0.779 / 0.775 / 0.381 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
