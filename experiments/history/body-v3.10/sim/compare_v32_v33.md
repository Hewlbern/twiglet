| Metric | v3.2 | v3.3 |
|---|---|---|
| Total mass (kg) | 2.291 | 2.256 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 237.3 | 235.5 |
| Support margin front / back / side (mm) | 47 / 55 / 70 | 48 / 54 / 70 |
| Tipping angle side / front (deg) | 16.5 / 11.2 | 16.6 / 11.4 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.32 (0.64x) / 0.46 (0.94x) / 0.19 | 0.30 (0.62x) / 0.44 (0.91x) / 0.18 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.317 (0.65x) / 0.268 (0.55x) | 0.302 (0.62x) / 0.252 (0.51x) |
| Standing bus current (A) | 5.66 | 5.53 |
| Push survived, no controller F/B/L/R (N·s) | 0.91 / 1.10 / 1.34 / 1.38 | 0.91 / 1.05 / 1.34 / 1.36 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.10 / 0.89 / 1.41 / 1.43 | 1.12 / 0.94 / 1.34 / 1.34 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.09 / 0.07 | 0.08 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.160 m/s / 12.13 A | 100% / 0.155 m/s / 12.27 A |
| Walk energy-aware: success / speed / current | 100% / 0.128 m/s / 11.04 A | 100% / 0.129 m/s / 11.07 A |
| Head+arm test: fell / min margin / neck peak | no / 29.9 mm / 0.826 N·m | no / 32.6 mm / 0.912 N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.44 / 0.756 / 0.386 | 0.439 / 0.751 / 0.383 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.065 (0.44x) | 0.065 (0.44x) |
| Fingertip payload continuous / brief (g), arm horizontal | 50 / 228 | 50 / 228 |
| Arm mass per side (g) | 98 | 98 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arms unchanged in v3.3 (arm_heat_v3.json carried over).
