| Metric | v3.5 | v3.6 |
|---|---|---|
| Total mass (kg) | 2.184 | 2.323 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 233.6 | 244.6 |
| Support margin front / back / side (mm) | 60 / 42 / 70 | 56 / 46 / 70 |
| Tipping angle side / front (deg) | 16.7 / 14.3 | 16.0 / 13.0 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.18 (0.37x) / 0.30 (0.61x) / 0.00 | 0.22 (0.45x) / 0.35 (0.72x) / 0.07 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.201 (0.41x) | 0.000 (0.00x) / 0.225 (0.46x) |
| Standing bus current (A) | 3.94 | 4.28 |
| Push survived, no controller F/B/L/R (N·s) | 1.17 / 0.80 / 1.36 / 1.38 | 1.17 / 0.96 / 1.48 / 1.48 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.22 / 0.75 / 1.38 / 1.41 | 1.31 / 0.82 / 1.50 / 1.52 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.06 / 0.00 | 0.06 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.171 m/s / 11.65 A | 100% / 0.172 m/s / 11.28 A |
| Walk energy-aware: success / speed / current | 100% / 0.143 m/s / 10.58 A | 100% / 0.140 m/s / 10.55 A |
| Head+arm test: fell / min margin / neck peak | no / 32.4 mm / n/a (no joint) N·m | no / 31.3 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.542 / 0.754 / 0.33 | 0.667 / 0.77 / 0.357 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.065 (0.44x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 50 / 228 | 49 / 228 |
| Arm mass per side (g) | 98 | 98 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged in v3.6 (arm_heat_v3.json carried over; TILT 13->10, YS 46->45, elbow rest 30) (arm_heat_v3.json carried over).

Notes: v3.6 has the 210 mm head (was 180), a smooth concave cone torso (torso_env_v36.py), and tucked arms (TILT 13->10, YS 46->45, elbow rest 20->30). The max-speed gait was re-tuned with one walk_refine round (80% at 0.166 m/s before, 100% at 0.172 m/s after). The energy-aware gait passed 100% without re-tuning. Arm rows are carried over from v3.5 because the arm links are unchanged.
