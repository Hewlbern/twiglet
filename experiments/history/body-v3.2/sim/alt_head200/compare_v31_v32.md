| Metric | v3.1 | v3.2 |
|---|---|---|
| Total mass (kg) | 2.213 | 2.334 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 231.1 | 240.6 |
| Support margin front / back / side (mm) | 53 / 49 / 70 | 47 / 55 / 70 |
| Tipping angle side / front (deg) | 16.9 / 13.0 | 16.3 / 11.0 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.24 (0.49x) / 0.37 (0.76x) / 0.11 | 0.32 (0.65x) / 0.47 (0.96x) / 0.20 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.261 (0.53x) / 0.229 (0.47x) | 0.335 (0.68x) / 0.281 (0.57x) |
| Standing bus current (A) | 4.81 | 5.61 |
| Push survived, no controller F/B/L/R (N·s) | 1.01 / 0.91 / 1.31 / 1.34 | 0.94 / 1.12 / 1.34 / 1.36 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.12 / 0.80 / 1.36 / 1.38 | 1.17 / 0.87 / 1.45 / 1.48 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.07 / 0.00 | 0.08 / 0.07 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.172 m/s / 12.37 A | 100% / 0.151 m/s / 12.33 A |
| Walk energy-aware: success / speed / current | 100% / 0.137 m/s / 10.87 A | 100% / 0.128 m/s / 11.07 A |
| Head+arm test: fell / min margin / neck peak | no / 29.3 mm / 0.814 N·m | no / 26.9 mm / 0.875 N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.423 / 0.748 / 0.36 | 0.478 / 0.761 / 0.408 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.65 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.29 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.063 (0.43x) | 0.065 (0.44x) |
| Fingertip payload continuous / brief (g), arm horizontal | 51 / 229 | 50 / 228 |
| Arm mass per side (g) | 97 | 98 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). v3.2 max-speed gait = v3 params locally refined on v3.2 (walk_refine.py; unrefined v3 params on v3.2: 80 % / 0.158 m/s). Energy-aware gait unchanged.
