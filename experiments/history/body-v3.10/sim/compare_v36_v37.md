| Metric | v3.6 | v3.7 |
|---|---|---|
| Total mass (kg) | 2.323 | 2.417 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 244.6 | 241.4 |
| Support margin front / back / side (mm) | 56 / 46 / 70 | 56 / 46 / 70 |
| Tipping angle side / front (deg) | 16.0 / 13.0 | 16.2 / 13.1 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.22 (0.45x) / 0.35 (0.72x) / 0.07 | 0.22 (0.46x) / 0.36 (0.73x) / 0.07 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.225 (0.46x) | 0.000 (0.00x) / 0.222 (0.45x) |
| Standing bus current (A) | 4.28 | 4.3 |
| Push survived, no controller F/B/L/R (N·s) | 1.17 / 0.96 / 1.48 / 1.48 | 1.22 / 1.01 / 1.52 / 1.55 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.31 / 0.82 / 1.50 / 1.52 | 1.38 / 0.84 / 1.59 / 1.59 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.06 / 0.00 | 0.00 / 0.05 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.172 m/s / 11.28 A | 100% / 0.166 m/s / 11.33 A |
| Walk energy-aware: success / speed / current | 100% / 0.140 m/s / 10.55 A | 100% / 0.135 m/s / 10.62 A |
| Head+arm test: fell / min margin / neck peak | no / 31.3 mm / n/a (no joint) N·m | no / 30.6 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.667 / 0.77 / 0.357 | 0.703 / 0.77 / 0.362 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 98 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged in v3.7 apart from grain + leaf sockets (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).

Notes: v3.7 adds chunky hollow boots (+~33 g each; the contact footprint is the same TPU sole box as v3.6), wood grain (material removed <3 cm3 in total), 7 peg-in leaves (~1 g each) and a chunky fringe (+27 g in the head; static head pitch unchanged because the head is centred over the pitch axis). The boots lower the COM by ~3 mm, which gives slightly better tipping and push numbers. No gait re-tune was needed (both gaits 100 % success, 2-4 % slower).
