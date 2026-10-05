# Twiglet ODM robot: body v3.2 (bigger head, pyramid body)
Built from body v3.1 (`../body-v3.1`, unchanged). The v3.1 notes are kept in `README_v31.md` and the v3 notes in `README_v3.md`.

v3.2 changes, from user feedback on v3.1:
1. the head is larger relative to the body;
2. the body silhouette tapers more (narrow chest, flaring toward the waist and kilt hem);
3. the arms are less splayed, and the kilt line is lower so more of the wooden torso shows.

## What changed
**Head: 190 mm ball (v3.1: 170 mm), scale 1.118**
- *What scales:* the head-v3 printed shells (dome, lower shell, snout, fringe, chin collars, black eye bezels). They scale about the chin / roll-mount line (`HEAD_Q`, model frame (79, 0, 96)).
  - The chin stays at the same height, and the head grows up and out by 16 mm.
  - Height without the hat is 471 mm (v3.1: 454).
- *Eyes:*
  - **Screens:** the 2.1" Waveshare screens (Ø54 visible) keep their physical size. They and their unchanged carriers move outward with the scaled glass centre, so the screen recess goes from 4.6 mm to about 5.1 mm.
  - **Bezels:** the bezel disc scales to Ø75 mm, still 0.394 of the ball diameter (the photo's eye-disc ratio), with a Ø65 aperture. The screen's black non-active border fills the ring between the Ø54 active area and the aperture (black on black).
  - **Eye art:** the orange ring is drawn 1.118× larger in firmware (ring about Ø41 mm), which still fits inside the 54 mm active area. No bigger screen is needed.
  - **At 200 mm:** the aperture would be Ø68, and a 2.8"/Ø71-active round screen would be the next size up if the black ring looked too wide.
- **Why 190 mm:**
  - 180, 190, 200 and 210 mm were checked analytically (`measure/v32_neck_scale.json`); 190 and 200 mm were run in the full sim.
  - 190 mm is the largest size that keeps at least 1.5× margin on the STS3215's rated torque for static neck pitch: 0.317 N·m standing (final run) = 1.55× under 0.49 N·m rated. 200 mm gives 0.335 N·m = 1.46×.
  - Front tipping angle: 11.2° at 190 mm vs 11.0° at 200 mm (v3.1: 13.0°). Knee static: 0.94× rated at 190 mm vs 0.96× at 200 mm.
  - The 200 mm results are kept in `sim/alt_head200/` and `renders/alt_head200/`.
- **Neck margins at 190 mm** (STS3215: 0.49 N·m rated, 1.91 N·m stall):

| Load | Torque | Margin |
|---|---|---|
| Static neck pitch | 0.317 N·m | 1.55× under rated |
| Static head pitch | 0.268 N·m | 1.83× under rated |
| Head+arm motion peak, neck pitch | 0.826 N·m | 2.31× under stall |
| Head+arm motion peak, head pitch | 0.44 N·m | 4.3× under stall |
| Head+arm motion peak, head yaw | 0.756 N·m | |

- **Print light:** 2 walls (0.8 mm), 8 % gyroid, 3 top/bottom layers. The printed head parts come to about 383 g by the export mass estimate (`build_report.json`). The head assembly in the sim is 576 g, 83 g more than v3.1 (493 g); the whole robot is 78 g heavier.

**Pyramid body**
- The torso barrel now tapers from 103 mm wide at the waist to 80 mm under the collar (half-width table `BARREL_B`).

| Height z (mm) | 28 | 45 | 60 | 75 | 86 |
|---|---|---|---|---|---|
| v3.2 width (mm) | 102 | 98 | 92 | 86 | 80 |
| v3.1 width (mm) | 93 | 95 | 92 | 88 | 80 |

- The top can't narrow further: the hip-yaw sleeves of the internal frame reach y ±36.8 up to z 86.
- The kilt stand-in (fabric; render only) is a steeper cone. Half-widths: 53 mm at the top → 56 → 66 → 76 mm at the hem (v3.1: 50.5 → 66). Front-back half-depth goes to 95 mm.

**Arms and kilt line**
- **Splay:** 13° (v3.1: 18°).
  - 11° was tried first, but the gripper then hit the hip bracket at only 11° outward hip roll (the gaits use up to 13°, the sim soft limit is 15°).
  - At 13° the arms clear up to 17° hip roll.
  - The shoulder boss face moves 5 mm out (YS 41 → 46) so the arms clear the wider lower barrel and pass just outside the kilt hem, as in the photo.
- **Kilt line:** 8 mm lower (KILT_TOP 41 → 33). The hip ring is now z 25–33.

## Proportions (`measure/v32_measure.json`)
All three models are measured the same way; photo values use the ball only (head D 195 px = 170 mm).

| | Photo (ball only) | v3.1 | v3.2 |
|---|---|---|---|
| Height without hat (mm) | 454 | 454 | 471 |
| Head / height | 0.374 | 0.374 | **0.404** |
| Shoulder width at joint height (mm) | 152 raw | 153 | 161 |
| Head / shoulder | 1.12 raw / 1.09 corrected (target 1.16) | 1.11 | **1.18** |
| Span including grippers (mm) | about 274 | 276 | 260 |
| Arm splay | 10–15° | 18° | 13° |

The photo head reads bigger than its ball because of the hair and hat volume, so v3.2 intentionally goes above the ball-only photo ratios, as requested. At 200 mm the ratios would be head/height 0.419 and head/shoulder 1.24.

## Printable parts (`stl/`, `build_report.json`)
- 38 STLs (`stl/v32_*.stl`). All are watertight single bodies that fit the 256 mm P1S bed, exported in print orientation.
  - Body parts use the orientation with the most bed contact.
  - Eye bezels and display carriers are printed with their largest flat face down.
- **New or changed vs v3.1:** `torso_shell_front/back` (taper), `hip_ring` (lower, 8 mm tall), `torso_frame` (longer shoulder bosses, 13° splay), and `v32_head_*`.
  - `v32_head_*` are the scaled head shells; the fringe is split into `_a`/`_b` halves because it is 268 mm wide at this scale.
  - They are exported from the watertight head-v3 solids. The shipped head-v3 STLs have a wood-grain surface and are not watertight.
- `head_display_carrier_L/R` are unchanged 1:1 (they hold the screen module).
- `stl_v31_old/` holds the v3.1 STLs copied in with the folder; it is not part of the zips.

**Head interface caveat**
- Scaling the shells uniformly also scales their internal bosses. The interfaces to the unscaled hardware then sit up to about 4–7 mm off their v3 positions:
  - roll-mount deck holes, Pi Zero standoffs, eye-driver board;
  - display-carrier screw bosses: the carriers are placed at the new eye positions, but their M3 bosses in `head_lower` have moved.
- Before printing the head, re-cut these bosses to the hardware patterns, or rebuild the head with `parts_head3` at R = 95.
- The roll-mount deck is 7 mm higher than the roll mount (scaled about the chin line). It needs a 7 mm printed spacer with the stock 4-hole pattern, or the re-cut boss above.
- Everything outside the head is ready to print.

## Collision check (`collide_v3.py`, output `collide_report.json`)
See the report for details. The follow-up check of the final arm rule is in `collide_v32_rule_check.json`.
- **Rest pose:** no non-adjacent clashes, and nothing touches with the arms at rest.
- **Hip roll:** −17..13° per leg; both hips together ±17° (v3.1: −20..13° and ±20°).
  - The outward limit is now the gripper touching the hip bracket at 17°, because of the 13° splay. That still leaves 2° over the 15° outward soft limit.
  - The inward limit is boot against boot, as before.
- **Knee:** −90..90° (shin cover), unchanged. Hip pitch and ankle are unchanged.
- **Head:**
  - neck pitch −1..+3° (v3.1: +4°) and head pitch −41..+3° (v3.1: −40..+5°), limited forward by the bigger chin collar against the torso shell;
  - roll ±6°, unchanged; yaw free.
  - Sim soft limits were updated to +3°.
- **Gait samples:**
  - both legs: 0 of 120;
  - single leg at stock limits: 20 of 120, the same foot/ankle contacts as v3/v3.1; the soft limits avoid them.
- **Arm sweep** (shoulder −10..110° × elbow −10..110°): 61 contacts, all gripper, fingers or forearm against the chin collar or head at high shoulder + elbow. None fall inside the soft rule.
- **Arms + walking legs:** 1 of 80 poses under the v3.1 rule. The hanging right gripper touched the hip bracket at 10.7° outward roll + 7° yaw with the arm straight down (shoulder 2.8°, elbow 13°).
  - Fixed with a minimum-bend rule: elbow ≥ 25 − shoulder, which the rest pose (5° / 20°) already meets.
  - Final soft rule: shoulder −5..84°, 25 − shoulder ≤ elbow ≤ min(110, 105 − shoulder), in both `collide_v3.py` and `sim/episode.py`.
  - Re-check: the failing sample is clear, and 0 arm contacts in 120 random walking + arm poses (outward hip roll up to 15°, yaw ±7°).
- **Arms vs torso barrel and kilt:** no contacts. At rest the gripper passes just outside the kilt hem.

## Sims (`sim/`, full table in `sim/compare_v31_v32.md`)
Same harness as v3.1:
- `run_tests.py v3`: stand, push, weight shift, head+arm;
- `walk_eval.py v3 [--eff]`: 20 randomized trials;
- `arm_heat.py v3`.

Changes:
- Neck and head pitch soft limit forward is now +3° (v3.1: +4/+5°) because of the larger chin collar. The rest of `sim/episode.py` is unchanged.
- **Arm rule:** new minimum bend, elbow ≥ 25 − shoulder (see Collision check).
- The unrefined v3 max-speed gait reached only 95 % success on v3.2. `walk_refine.py` (new: 24 local perturbations × 10 seeds, verified on the standard 20 seeds) brought it to 100 % at 0.160 m/s. The energy-saving gait is unchanged.

Rows that changed vs v3.1:

| Metric | v3.1 | v3.2 |
|---|---|---|
| Total mass (kg) | 2.213 | 2.291 |
| COM height (mm) | 231.1 | 237.3 |
| Support margin front / back / side (mm) | 53 / 49 / 70 | 47 / 55 / 70 |
| Tipping angle side / front (deg) | 16.9 / 13.0 | 16.5 / 11.2 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.24 (0.49x) / 0.37 (0.76x) / 0.11 | 0.32 (0.64x) / 0.46 (0.94x) / 0.19 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.261 (0.53x) / 0.229 (0.47x) | 0.317 (0.65x) / 0.268 (0.55x) |
| Standing bus current (A) | 4.81 | 5.66 |
| Push survived, no controller F/B/L/R (N·s) | 1.01 / 0.91 / 1.31 / 1.34 | 0.91 / 1.10 / 1.34 / 1.38 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.12 / 0.80 / 1.36 / 1.38 | 1.10 / 0.89 / 1.41 / 1.43 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.07 / 0.00 | 0.09 / 0.07 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.172 m/s / 12.37 A | 100% / 0.160 m/s / 12.13 A |
| Walk energy-aware: success / speed / current | 100% / 0.137 m/s / 10.87 A | 100% / 0.128 m/s / 11.04 A |
| Head+arm test: fell / min margin / neck peak | no / 29.3 mm / 0.814 N·m | no / 29.9 mm / 0.826 N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.423 / 0.748 / 0.36 | 0.44 / 0.756 / 0.386 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.29 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.063 (0.43x) | 0.065 (0.44x) |
| Fingertip payload continuous / brief (g), arm horizontal | 51 / 229 | 50 / 228 |
| Arm mass per side (g) | 97 | 98 |

## Remaining visual differences from the photo
- **Head mechanics:** see the caveat above. The head is a uniform scale of head-v3, not a re-engineered one.
- **Head size:** at 190 mm it still reads a bit smaller than the photo's hair-plus-hat mass. 200 mm (in `alt_head200/`) is closer, but only 1.46× neck margin.
- **Torso top:** can't narrow further (internal hip-yaw sleeves), so most of the pyramid effect comes from the flared bottom and the kilt cone.
- **Side profile:** still deeper front-to-back than the photo (frame and battery).
- **Arms:** splay 13°, the top of the requested ~10–15°. They sit in the front third of the torso side.
- **Shoulders:** the black sleeves sit about 5 mm further out than v3.1.
- **Kilt:** a solid cone stand-in; the real fabric kilt will drape and scallop.

## Files
- **Scripts:** `design_v3.py` (parameters `HEAD_S`, `HEAD_Q`, `scale_head()`), `export_v3.py`, `render_v32.py`, `collide_v3.py`, `view_v3.py`.
- **Renders:**
  - `renders/compare_photo_v31_v32.png`: photo, v3.1 and v3.2 front / side / photo-angle 3/4;
  - `renders/overlay_v32_on_photo.png`: overlay, same camera as v3.1;
  - `renders/overlay_photo_v31_v32_side_by_side.png`;
  - `renders/v32_*.png`.
- **Sims:** `sim/compare_v31_v32.md/.json`, `sim/v31_ref/` (v3.1 results), `sim/walk_refine_v32.json`, videos `sim/v32_*.gif/.mp4`.
- **Measurements:** `measure/v32_measure.json`, `measure/v32_neck_scale.json`.
