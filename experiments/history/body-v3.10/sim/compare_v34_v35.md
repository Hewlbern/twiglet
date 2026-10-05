| Metric | v3.4 | v3.5 |
|---|---|---|
| Total mass (kg) | 2.25 | 2.184 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 231.4 | 233.6 |
| Support margin front / back / side (mm) | 46 / 56 / 70 | 60 / 42 / 70 |
| Tipping angle side / front (deg) | 16.9 / 11.2 | 16.7 / 14.3 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.32 (0.65x) / 0.46 (0.94x) / 0.20 | 0.18 (0.37x) / 0.30 (0.61x) / 0.00 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.309 (0.63x) / 0.255 (0.52x) | 0.000 (0.00x) / 0.201 (0.41x) |
| Standing bus current (A) | 5.68 | 3.94 |
| Push survived, no controller F/B/L/R (N·s) | 0.94 / 1.17 / 1.41 / 1.43 | 1.17 / 0.80 / 1.36 / 1.38 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.20 / 0.91 / 1.48 / 1.50 | 1.22 / 0.75 / 1.38 / 1.41 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.08 / 0.07 | 0.06 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.148 m/s / 12.27 A | 100% / 0.171 m/s / 11.65 A |
| Walk energy-aware: success / speed / current | 100% / 0.124 m/s / 11.11 A | 100% / 0.143 m/s / 10.58 A |
| Head+arm test: fell / min margin / neck peak | no / 32.4 mm / 0.801 N·m | no / 32.4 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.383 / 0.753 / 0.364 | 0.542 / 0.754 / 0.33 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.065 (0.44x) | 0.065 (0.44x) |
| Fingertip payload continuous / brief (g), arm horizontal | 50 / 228 | 50 / 228 |
| Arm mass per side (g) | 98 | 98 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arms unchanged in v3.5 (arm_heat_v3.json carried over).

v3.5 notes: the neck-pitch joint is removed (fixed neck post). In the v3.5 head+arm test the head-pitch servo does the full nod (-34..+4 deg; v3.4: neck 65/-20 cmd clipped to -1..+3, head +-10 clipped to -10..0).
Ankle static torque is below the 0.02 N·m logging threshold (COM now almost over the ankles). Gait re-tuned with walk_refine.py (max-speed 2 rounds: 20% -> 95% -> 100%; energy-aware 1 round: 95% -> 100%).
