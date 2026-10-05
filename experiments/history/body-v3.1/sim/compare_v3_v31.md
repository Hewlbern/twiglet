| Metric | v3 | v3.1 |
|---|---|---|
| Total mass (kg) | 2.173 | 2.213 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 233.0 | 231.1 |
| Support margin front / back / side (mm) | 51 / 51 / 70 | 53 / 49 / 70 |
| Tipping angle side / front (deg) | 16.7 / 12.3 | 16.9 / 13.0 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.26 (0.53x) / 0.39 (0.80x) / 0.14 | 0.24 (0.49x) / 0.37 (0.76x) / 0.11 |
| Standing bus current (A) | 5.08 | 4.81 |
| Push survived, no controller F/B/L/R (N·s) | 0.94 / 0.94 / 1.29 / 1.31 | 1.01 / 0.91 / 1.31 / 1.34 |
| Push survived, IMU balance F/B/L/R (N·s) | 0.94 / 0.96 / 1.31 / 1.34 | 1.12 / 0.80 / 1.36 / 1.38 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.11 / 0.00 | 0.07 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.168 m/s / 12.34 A | 100% / 0.172 m/s / 12.37 A |
| Walk energy-aware: success / speed / current | 100% / 0.133 m/s / 11.04 A | 100% / 0.137 m/s / 10.87 A |
| Head+arm test: fell / min margin / neck peak | no / 33.7 mm / 0.84 N·m | no / 29.3 mm / 0.814 N·m |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.74 / 0.99 / 1.63 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.28 / 0.51 / 1.36 | 0.29 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.046 (0.31x) | 0.063 (0.43x) |
| Fingertip payload continuous / brief (g), arm horizontal | 83 / 322 | 51 / 229 |
| Arm mass per side (g) | 86 | 97 |

v3.1 walks re-use the v3 gait parameters (walk_eval.py: nominal + 20 randomized 10 s trials); no new gait search.
