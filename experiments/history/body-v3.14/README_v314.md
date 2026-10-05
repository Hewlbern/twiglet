# body-v3.14: fitted, clumpy wig (only the hair changed vs v3.13, plus 3 pin holes in head_upper)

## Fit
- **Seat surface:** the wig is a separate piece. Its seat is the real outer surface of head_upper + head_lower (+ the bezel fronts) + 0.3 mm (`hair_v314.Envelope`).
  - The surface was measured on an icosphere(6) grid from the ball centre, with the wood-grain grooves bridged.
  - The head is not a perfect sphere: the radius runs from 104.56 mm at the crown to 105.13 mm at theta 80°. The v3.13 ball + 0.3 seat therefore had 0.54 mm clearance at the crown and ~0 mm at the sides.
- **Closed crown cap:** a 2 mm cap (theta 0–26°, under the hat) ties all the clump roots together.
- **Contact:** every strand's underside is cut by the seat surface, so the roots sit in full contact. Below theta 86° the strands hang vertically, like hair.
- **Measured seat clearance** (`gap_v314.py`, exact closest point, 4465 seat samples):
  - min 0.30 / p5 0.31 / p50 0.33 / p75 0.49 / p95 1.20 mm.
  - 84 % of samples are within 0.2–0.6 mm. The larger values sit over wood-grain grooves.
- **Interference:** 0 mm³ overlap with head_upper, head_lower, the snout, both bezels, both chin collars and both display carriers.
- **Minimum gaps:** head_upper 0.30, head_lower 0.31, bezels 0.32/0.33, snout 1.96 mm.
- **Locating:** 3 pin bosses on the crown cap (theta 20°, phi 30/150/270) take 3 × 3 mm pins. They go into 3 new 3.2 mm through-holes in head_upper, which is a REPRINT. If you don't reprint, drill through the bosses, using the wig as the jig.
- **Renders:** `renders/hair_gapcheck_v314.png` (front / side / back / top, no hat) and `renders/hair_fit_sections_v314.png` (sections + zooms).

## Clumps
- **Layout:** 17 clumps made of 45 strands.
- **Strands:** puffy super-ellipse sections, 9–11 mm thick. That matches the photo, which measures ≈ 9–10 mm (lock edges ~11 px at 0.875 mm/px).
- **Clump shape:** 2–3 overlapping strands per clump give deep V-grooves between strands and between clumps. Lengths are irregular (random ±6° per strand).
- **Tips and surface:** twists of 15–40°, pointed tips, and flicks of up to 26 mm on the side flares. A 0.25 mm felt ripple covers the surface.
- **Eye cover:** L 10.6 %, R 12.2 % (v3.13: 6.7 / 10.2). The heart eyes stay readable (renders).

## Weight
- **Mass:** 166.9 g sim wig (v3.13: 120.6 g).
- **Moment about the calibrated pivot (x = −16.7):** 2458 g·mm (v3.13: 3650). The extra mass sits in the back and back-side clumps, behind the nod axis.
- **Crown note:** the crown itself is 28 mm in FRONT of the nod axis, so it was not used as a counterweight.
- **Static head pitch (sim, crouch 0.30):** 0.219 N·m, which is **2.24×** on the 0.49 rating (v3.13: 0.237 = 2.07×).
- **Total mass:** 2.486 kg.

## Sims (`sim/compare_v313_v314.md`)
- **Max-speed gait:** 95 % at first → re-tuned (`walk_refine`) → 100 %, 0.178 m/s. The pre-refine best is in `sim/bak_pre_refine_v314/`.
- **Energy gait:** 100 %, 0.144 m/s.
- **Head+arm:** no fall; min margin 26.6 mm (v3.13: 34.9). Peak head pitch 0.779 N·m (v3.13: 0.731).

## Collisions (`collide_head_v314.json`)
- **Head ranges:** rest 0; head pitch −36..9, roll ±9, yaw ±160. Nod and roll at yaw ±20/45/90 are identical to v3.13.
- **Arm sweep, head straight:** 49 poses, 0 involving the hair.
- **Arm sweep, head yawed ±45°:** 57 / 62 poses total (same as v3.13), of which 20 / 20 involve the hair (v3.13: 21 / 23). These are hand-to-face poses only.

## Print
- **Files:** `stl_head_v314/`: `v314_head_wig.stl` (one piece fits diagonally, 226 × 201 × 219 mm, but has 145 cm² of overhang), `v314_head_wig_split_a/_b` (recommended: 6–7 cm² overhang each, 2 mid-plane pins) and `v314_head_head_upper.stl` (REPRINT, holes).
- **Settings:** `print_note_hair_v314.md`. Wig: 2 walls, 3 top/3 bottom layers, 5 % lightning, which prints the clumps as sealed hollow shells.
- **Zip:** `$WORK/twiglet-hair-v3.14-stl.zip` (10.2 MB).
