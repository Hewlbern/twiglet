# body-v3.13 — photo-matched hair (only the fringe changed; v3.12 snout kept)

## Photo study
- 13–16 chunky felt locks with a central ridge and pointed tips, of varied length and width, ragged and asymmetric.
- The hat band sits high: the hair emerges about 20° from the crown.
- The centre lock dips between the eyes. The locks droop over the top third of each screen.
- Broad locks flare out at eye level.
- Long side locks hang outside the cheeks toward the chin.

## Changes vs v3.12 (fringe only)
- **Locks:** 16 locks (v3.7/v3.12 had 11), built with `hair_v313.py` `lock2()`. Each lock is a lens section with a centre crease, a radial lift so it drapes over the bezels and stands off the ball, and a tip flick.
  - 5 front locks over and between the eyes.
  - 2 broad side flares (44–46 mm wide) plus 2 smaller in-between flares.
  - 4 long side locks down to theta 112–115°.
  - 2 wide back-side locks, which act as a counterweight behind the pitch axis.
  - 1 short layered lock on top.
  - Left and right are deliberately asymmetric.
- **Crown:** the solid crown cap (about 45 g, hidden under the hat) is replaced by a 1.8 mm band ring (theta 17–28°) that ties the lock roots together.
- **Lock thickness:** × 0.85.
- **Eye cover:** L 6.7 %, R 10.2 % of the visible screen circle (v3.7: 4.2 / 4.2). Only the top rim is covered; the heart and ring content stays clear (see renders).

## Mass and load
- **Fringe mass:** 120.6 g sim / about 121 g printed at 2 walls + 8 % gyroid (v3.12: 104.2 g).
- **Forward moment:** about the calibrated pitch reference, 3650 g·mm vs 4103.
- **Calibration:** `X_AXIS = -16.7`, calibrated against sim runs. The kinematic 4.3 mm estimate was wrong, and the first draft (137 g) raised the load to 0.250 N·m.
- **Static head pitch at crouch 0.30:** 0.237 N·m = **2.07×** margin on 0.49 (v3.12: 0.245 = 2.00×).
- **Total mass:** 2.439 kg.

## Sims (`sim/compare_v312_v313.md`)
- **Max-speed gait:** it first dropped to 90 %, so it was re-tuned with `walk_refine`. After the re-tune: 100 %, 0.175 m/s (v3.12: 100 %, 0.172). The pre-refine best is in `sim/bak_pre_refine/`.
- **Energy gait:** 100 %, 0.143 m/s. Unchanged, no re-tune needed.
- **Head+arm test:** did not fall, min margin 34.9 mm. Peak head pitch 0.731 N·m (v3.12: 0.725).

## Collisions (`collide_head_v313.json`; v3.12 baseline in `collide_head_v312_baseline_for_v313.json`)
- **Rest:** 0 clashes.
- **Head ranges:** pitch −36..9, roll ±9, yaw ±160. Nod and roll at yaw ±20/45/90 are identical to v3.12. They are still limited by the neck/chin collar, not the hair.
- **Arm sweep, head straight:** 49 colliding poses, 0 involving the hair (same as v3.12).
- **Arm sweep, head yawed ±45:** 57 / 62 total poses (same as v3.12). Of those, 21 / 23 hit the hair (v3.12: 25 / 25).
  - These contacts are only in hand-to-face poses (elbow ≥ 90 with shoulder + elbow > 105). Those poses are already outside the gait arm soft limit.

## Print
- **Files:** `stl_head_v313/v313_head_fringe.stl` (243.7 × 223.9 × 187.5 mm, fits the P1S diagonally) and split halves `_split_a/_b`, each with one 3 mm alignment pin at the mid-plane.
- **Notes and zip:** `print_note_hair_v313.md` and `$WORK/twiglet-hair-v3.13-stl.zip`.

## Renders
- `renders/hair_photo_v312_v313.png`
- `renders/hair_closeup_v313.png`
