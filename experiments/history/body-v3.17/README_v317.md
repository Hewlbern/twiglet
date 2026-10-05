# Twiglet v3.17: chunkier wig (only the wig changed)

**Change.** The wig is now 13 locks instead of 16 (hair_v317.py). The locks are fewer, bigger and thicker, placed to match the photos:
- 5 across the forehead: a centre point dipping between the eyes, one over each eye, and one past each eye's outer edge.
- 2 big side flares.
- 2 long back-side locks.
- 4 broad back locks.

Lock geometry:
- Crest height goes up about 30% to 19-25 mm (v3.16 was 14-19 mm).
- Base widths are 58-80 mm.
- The cross-section is a fuller wedge, with a profile exponent of 0.7 to round out the shoulders.
- Locks stay broad for longer and taper to a point late along their length.
- Lock ends are thicker (tail exponent 0.5).
- The lower ends lift further off the head (flare 26/5 mm vs 22/3 mm).
- The crown dome is thicker (T0 14 mm vs 11 mm) so the bigger locks still blend smoothly into it: crown blend check shows 0 kinks over 20 deg and a 0.63 mm max jump.

The front lock tips stop at the top rims of the eyes, so the hearts are fully readable. The locks cover 13%/18% of the eye screens (L/R), all of it on the upper rim.

**Attachment.** Unchanged: 4 vertical pins, a keyed tongue/groove and a 0.3 mm epoxy glue land. head_upper comes out bit-identical to v3.16 (volume 123105.5 mm3, 325188 faces). The wig has zero overlap with head_upper, head_lower, the snout, the bezels, the collars and the display carriers. Minimum gap is 0.30 mm to head_upper and 2.95 mm to the bezels.

**Mass.** The wig weighs 160 g printed with 3% lightning infill (v3.16: 131 g at 8%). Keep the infill at 3%. At 8% the wig would be 187 g, and the head+arm margin dropped to 19.8 mm in that run.

**Walls.** Wall thickness was measured with inward rays from 2,500 samples, leaving out the last 6 mm of each lock point:
- v3.17: 1.16 mm minimum, 2.75 mm p1, 10.1 mm median.
- v3.16: 0.47 mm minimum, 1.57 mm p1, 6.8 mm median.

Only the knife-edge lock points and lock edges are thinner than 1.2 mm: 7.5% of the surface, against 14.6% in v3.16.

**Checks** (light scripts, final geometry):
- Arm sweep vs wig, contacts at head yaw 0/-45/+45: 0/23/23 of 156 poses each (v3.16: 2/19/23).
- Head motion range, wig contacts over a 315-pose grid of pitch ±45, yaw ±160 and roll ±30 deg: 13 (v3.16: 10). All the extra contacts are corner poses with pitch at ±30-45 deg and roll at ±30 deg at the same time.

**Sims.** The max-speed gait was re-tuned locally with walk_refine (95% before, 100% after; the pre-refine parameters are in sim/bak_pre_refine_v317/). The full table is in sim/compare_v316_v317.md.
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
