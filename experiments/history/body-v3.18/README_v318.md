# Twiglet v3.18: flowing, less obstructive wig (only the wig changed)

**Change** (hair_v318.py). The wig is 15 locks, and each lock now follows a swept path instead of a straight wedge:
- The path sweeps along a smoothstep arc and adds an S-wave of ±4-9 deg.
- Each lock has a gentle twist: the crest drifts across the lock from root to tip (twist ±0.2-0.5).
- Lengths vary.
- The chunky, full-shouldered wedge section from v3.17 is kept.

Layout, matched to the original photo:
- Parted fringe: two centre locks sweep up and out from the part (curl ±45 deg), and two over-eye locks sweep outward (curl ±35 deg). The tips end above the heart screens.
- A short, narrow centre bang dips between the eyes.
- Eye-level side flares curl out and back, with more seat lift at the sides (FLARE SIDE 34 vs 26).
- Long S-swept side locks, plus 4 back locks of different lengths.

Free lock edges now end in a lip at least 1.3 mm thick instead of a feather edge.

Eye screens covered (L/R): 2.4% / 4.2% (v3.17: 13.1% / 18.1%). Eye coverage is mostly driven by how long the fringe is: making the fringe locks just 4 deg longer raised it to 8-10%.

The crown blend still passes: 0 kinks over 20 deg. head_upper is identical to v3.16/v3.17 (same pins, key and glue land). There is zero overlap with every head part, bezel and the snout.

**Wig.** One piece, 204 x 222 x 207 mm (fits the P1S). 150 g at 5% lightning infill, plus about 29 g of support, about 11.2 h.

**Walls.** Wall thickness from inward rays, leaving out tips:
- Minimum 1.12 mm, p1 2.0 mm, median 9.7 mm.
- 4.4% of all samples read under 1.2 mm. These are the lock tips and rays running along the edge lips.

**Infill and the head+arm margin.** The head+arm minimum margin changes by several mm with just a few grams of wig mass (it is a single dynamic minimum):

| Wig infill | 0% | 2% | 3% | 4% | **5%** | 6% | 7% | 8% |
|---|---|---|---|---|---|---|---|---|
| Head+arm min margin (mm) | 24.5 | 23.0 | 25.3 | 30.6 | **32.7** | 30.4 | 30.2 | 31.8 |

The v3.17 wig showed the same scatter: 32.9 mm at 0%, 33.6 mm at 3% and 19.8 mm at 8%.

5% is the best v3.18 value. It is 0.9 mm under v3.17's 33.6 mm. The static head-pitch load is lower in v3.18: 0.205 N·m vs 0.211 N·m, because the wig's mass moment about the nod axis dropped from 1618 to 949 g·mm.

**Light checks** (final geometry):
- Arm sweep vs wig, contacts at head yaw 0/-45/+45: 0/14/14 of 156 poses each (v3.17: 0/23/23).
- Head range (315 poses): 8 wig contacts (v3.17: 13).

**Sims.** The max-speed gait was re-tuned locally with walk_refine (95% before, 100% after). The pre-refine parameters are in sim/bak_pre_refine_v318/.

| Metric | v3.17 | v3.18 |
|---|---|---|
| Total mass (kg) | 2.547 | 2.537 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 245.1 | 244.5 |
| Support margin front / back / side (mm) | 57 / 45 / 70 | 57 / 45 / 70 |
| Tipping angle side / front (deg) | 16.0 / 13.0 | 16.0 / 13.1 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.23 (0.47x) / 0.38 (0.77x) / 0.07 | 0.23 (0.46x) / 0.37 (0.75x) / 0.06 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.211 (0.43x) | 0.000 (0.00x) / 0.205 (0.42x) |
| Standing bus current (A) | 4.33 | 4.27 |
| Push survived, no controller F/B/L/R (N·s) | 1.34 / 1.08 / 1.64 / 1.66 | 1.34 / 1.05 / 1.64 / 1.66 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.48 / 0.94 / 1.69 / 1.71 | 1.50 / 0.91 / 1.69 / 1.71 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.06 / 0.00 | 0.00 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.181 m/s / 10.87 A | 100% / 0.182 m/s / 11.03 A |
| Walk energy-aware: success / speed / current | 100% / 0.150 m/s / 10.44 A | 100% / 0.150 m/s / 10.43 A |
| Head+arm test: fell / min margin / neck peak | no / 33.6 mm / n/a (no joint) N·m | no / 32.7 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.771 / 0.775 / 0.377 | 0.761 / 0.774 / 0.374 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
