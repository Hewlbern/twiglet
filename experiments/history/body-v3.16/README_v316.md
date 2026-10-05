# body-v3.16: triangular-lock wig blended into the crown, keyed/pinned/glued attachment, printed kilt

## Hair (hair_v316.py, head_v316.py)
- One-piece wig built as a single radial height field over the head.
  - The crown dome and 16 wedge locks are merged with a smooth (C1) maximum, so the lock ridges rise straight out of the dome. There is no step, ledge, feather edge or seam.
- Each lock is a faceted wedge: triangular planform tapering to a sharp point, a gable/tent cross-section (two planar facets, slightly off-centre crest), cresting at about 35% of its length and falling straight to the point.
  - Neighbouring locks overlap in soft V valleys; the front locks are layered over the sides.
- Layout from the photos: 5 front locks, with tips hanging over the top of each eye (hearts stay readable, eye cover 7% L / 11% R).
  - Thick side flares at eye level; long side locks past the cheeks; 7 back locks.
  - The lower lock ends peel off the head (flare, up to 25 mm at the sides).
- Below theta 86 deg the seat is vertical, so the rigid wig slides straight down (no undercut).
- Wig 131 g sim (v3.15: 199 g); moment about the nod axis 1538 g·mm (v3.15: 1734).
- Blend check (meridian profiles of the real mesh, 1.85 mm steps):
  - crown (theta < 34 deg): max kink 16 deg, 0 kinks over 20 deg, max height jump 0.56 mm;
  - lock transition zone (12-62 deg): p99 kink 16 deg, max jump 0.96 mm (the remaining kinks are the lock crest lines themselves).

## Attachment
- 4 vertical 3 mm pins: blind holes in the wig, 3.2 mm holes in head_upper. All pins are parallel to the push-on direction, so nothing binds (the 3 old radial v3.15 holes are filled).
- Keyed tongue: 2.4 × 1.1 mm, 4 arcs of 70/40/40/40 deg, fits one way only. It sits in a 3.0 × 1.0 mm groove in head_upper (0.3 mm side gap, 0.2 mm bottom gap); the groove floor wall is 1.47 mm.
- Glue land: the whole crown seat, with a 0.30-0.45 mm gap (p5/p50). Glue with 2-part epoxy (medium CA works but is brittle).
- Checks: 0 overlap with head_upper, head_lower, snout, bezels, chin collars and display carriers. The pins don't touch any internal part. Walls are 1.25 mm or more (1.47 mm at the groove).

## Kilt (kilt_v316.py, kilt_check_v316.py)
- kilt_band = the hip_ring reprinted with a rolled rim on top, plus 10 green PLA leaf petals.
  - Petals are 1.2 mm thick, with a raised centre vein, a big leaf point and small side teeth.
  - They are layered: alternate petals sit 1.6 mm further out.
  - Bell flare from the waist; hem points reach z -52 (upper/mid thigh).
- Each petal's top lip hooks over the rim (hinge) and rests against the rim face.
  - It can't swing in toward the legs.
  - Anything pushing from inside swings it out.
  - Lift a back petal to reach the power switch or the USB-C charger.
- Arm slots at |az| 46-93 deg each side, because the elbows rest against the hip ring (the arms cover the slots).
- Mass 69.4 g (petals 59.9 g + band 9.5 g).
- Petals print upside down on their lip with no supports (flare ≤ 36 deg). The band prints upside down with no supports. TPU option: same petal STLs in 95A TPU.
- How it avoids the legs:
  - Above z -24 the legs are narrow (|y| ≤ 37 mm).
  - Below that, the petals are already flared out past the thigh servos (|y| 72.5 mm).
  - The front petals stay inside the forearms.
- Clearance results (kilt fixed at rest = worst case):
  - Both final sim gaits (after the energy-aware re-tune), nominal + 2 randomized runs each, 1500 poses: 0 leg contacts, 0 arm contacts.
  - Single-leg stance: 0 contacts.
  - collide_v3 gait sets: single-leg 7/120, both-legs 1/120, arms+legs 1/80. These are all a foot touching a front petal at extreme knee+thigh angles, which pushes the petal out (free swing). Arm contacts: 0.
  - Full ranges:
    - Legs touch petals past hip roll ±15-17 deg, at hip pitch ±70 deg and knee ±90 deg. These contacts all push the petal outward.
    - The arms touch the kilt only with the shoulder swung back past -16 deg or the elbow bent back past -16 deg. Both are outside the soft limits.

## Sims (final geometry; sim/compare_v315_v316.md)
| Metric | v3.15 | v3.16 |
|---|---|---|
| Total mass (kg) | 2.522 | 2.518 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 248.8 | 243.1 |
| Support margin front / back / side (mm) | 55 / 47 / 70 | 57 / 45 / 70 |
| Tipping angle side / front (deg) | 15.7 / 12.5 | 16.1 / 13.1 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.25 (0.50x) / 0.39 (0.80x) / 0.10 | 0.23 (0.47x) / 0.37 (0.76x) / 0.07 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.214 (0.44x) | 0.000 (0.00x) / 0.216 (0.44x) |
| Standing bus current (A) | 4.46 | 4.33 |
| Push survived, no controller F/B/L/R (N·s) | 1.24 / 1.10 / 1.59 / 1.62 | 1.31 / 1.05 / 1.62 / 1.64 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.29 / 1.05 / 1.64 / 1.66 | 1.50 / 0.89 / 1.69 / 1.71 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.00 / 0.00 | 0.07 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.178 m/s / 11.53 A | 100% / 0.182 m/s / 11.29 A |
| Walk energy-aware: success / speed / current | 100% / 0.147 m/s / 10.3 A | 100% / 0.152 m/s / 10.53 A |
| Head+arm test: fell / min margin / neck peak | no / 17.9 mm / n/a (no joint) N·m | no / 30.6 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.825 / 0.777 / 0.387 | 0.749 / 0.772 / 0.369 |

- The energy-aware gait was re-tuned by walk_refine (95% → 100%).
- Head collisions (collide_head_v316, partial run): rest 0; head pitch -36..9, roll ±9, yaw ±160 (same as v3.15).
  - The full script was killed twice mid-run on the shared box. The arm sweep was re-run with a lighter FCL script (armsweep_v316.json): hair contacts 2/19/23 at head yaw 0/-45/+45 out of 156 poses each. v3.15 counted 0/19/6 with a different checker, so the numbers aren't directly comparable. The contacts come from the wider side flares, with the arms raised to the head.
  - Kilt contacts in the arm sweep: 6 per yaw. All have the shoulder or elbow at -10 deg, beyond the -5 / 0 deg soft limits.

## Reprint list
- Head pack (twiglet-head-v3.16-stl.zip): wig and head_upper.
- Kilt pack (twiglet-kilt-v3.16-stl.zip): kilt_band (replaces hip_ring) and petals 00-09.
- Unchanged: head_lower, bezels, snout, chin collars, display carriers, body, legs, arms, hat.
- Print and assembly notes: print_note_head_v316.md and print_note_kilt_v316.md (both inside the zips and copied to $WORK/).
