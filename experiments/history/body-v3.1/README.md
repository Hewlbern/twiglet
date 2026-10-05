# Twiglet Open Duck: body v3.1 (look pass: arms at the sides, wooden barrel body)

v3.1 keeps everything that set the v3 proportions:
- 454 mm tall without the hat; head 170 mm = 0.374 of height;
- thigh 22 mm shorter, hips 20 mm forward, battery aft;
- STS3215 legs and neck, STS3032 arms, digital-eye head (head-v3).

It changes the look to match the photo: the arms hang at the sides, the torso is a rounded wood barrel, and the gripper is Feetech-style. v3 is untouched in `../body-v3/`. The v3 README is kept here as `README_v3.md` for the measurement method, the v3 design and the servo choice.

## What changed vs v3 (`design_v3.py`, parameters in `build_report.json`)
**Torso: rounded wooden barrel**
- New shape: an asymmetric superellipse plan (n = 4, front half-depth 60, rear 88), lofted smoothly from the waist (z 25) to a rounded top (z 90).
- Width: 95 mm at the lower chest, 92 mm mid, 88 mm under the collar. v3 was a stepped box, 90 mm overall with a 67 mm front block.
- Front face: 80–86 mm across its first 15 mm (v3: 67).
- Closed 2 mm lid; no servos or brackets visible from the front or side.
- Small printed vine + 4 leaves embossed 1 mm on the chest.
- The shell still splits at x = −20 into front and back halves with tabs.

**Arms at the sides**
- The shoulder STS3032 horn sits on a frame boss that ends flush with the barrel side: shoulder axis at x 4, z 74, just under the collar. v3 had it at x 18, z 80 on a boss in front of the narrow torso.
- The whole arm chain and its joint axes are splayed 18° outward.
- Elbow servo flipped: its horn faces inward, so the wood upper-arm plate runs down the inner side.
- Visible sequence, as in the photo: round **black shoulder joint** → wood upper arm → **black elbow joint** → wood forearm block → black gripper.
- Arm lengths: upper 46 mm, forearm 72 mm (v3: 42 / 45).
- The gripper hangs beside the kilt at hem level, with the fingertips about 7 mm below the hem. Rest pose: shoulder 5°, elbow 20°, so the forearm angles slightly forward.

**Gripper**
- Still STS3032-driven.
- The housing is now a boxy 25 × 27 × ~50 mm black body in the style of the Feetech gripper, with a recessed label panel on the outer face. Fixed and moving fingers as before.

**Legs**
- New wood-look snap-on shin covers (C-clip with a slit on the inboard side) between the knee servo and the boot cuff.
- The knee servos stay dark, as in the photo.
- Thigh covers were not added: the kilt hides the thigh down to the knee servo, and a cover there would clash with the hip-pitch servo at thigh-forward angles above 12°.

**Kilt**
- Still fabric. The render stand-in starts at the waist under the barrel and flares to the hem at z −62. It is now drawn opaque.

## Proportions: v3.1 vs photo (`measure/v31_measure.json`)
| | Photo | v3 | v3.1 |
|---|---|---|---|
| Height without hat (mm) | 454 | 454 / 448 stance | 454 / 448 stance (unchanged) |
| Head / height | 0.374 | 0.374 | 0.374 (unchanged) |
| Shoulder width at joint height (mm) | 152 raw | 146 | 153 |
| Head / shoulder (target 1.16) | 1.12 raw / 1.09 corrected | 1.166 | 1.11 |
| Torso width (mm) | about 100–103 | 90 (front block 67) | 95 / 92 / 88 (front face 80–86) |
| Arm span at elbows (mm) | about 178 | – | 189 |
| Span including grippers (mm) | about 274 | 146 | 270 |
| Arm splay | 10–15° | 0° | 18° |

## Printable parts (`stl/`, `build_report.json`)
- 27 v3.1 STLs (`stl/v31_*.stl`). All are watertight single bodies that fit the 256 mm P1S bed, exported in the orientation with the most bed contact.
- Arm parts are exported unsplayed, so they print flat.

New or changed vs v3:
- `torso_shell_front/back`: barrel with vine relief. Use a brim on the front half, which has a small first-layer area on its split face.
- `torso_frame`: tilted shoulder bosses at the barrel side; rails moved back to x −8..16.
- `hip_ring`: barrel outline.
- `shoulder_sleeve_L/R` (black), `upper_arm_L/R` (wood plate + floor tab, M2 to the sleeve bottom and the servo ears).
- `elbow_sleeve_L/R` (black), `forearm_L/R` (wood block + link).
- `gripper_housing_L/R` (boxy black body), `finger_moving_L/R`.
- `shin_cover_L/R` (wood).

Unchanged from v3: thigh sheets and spacer, neck sheets, hip cradle, hip brackets, boot cuff.
Reused: `stl/reused_head_v3/`, stock ODM parts, and the Twiglet boots.

`stl_v3_old/` holds the v3 STLs that were copied into this folder. It is not part of the v3.1 zips; the originals are in `../body-v3/stl`.

## Collision check (`collide_v3.py`, output `collide_report.json`)
See the report for the full list. The follow-up check of the tightened arm rule is in `collide_v31_rule_check.json`.
- **Rest pose:** no non-adjacent clashes with the arms hanging at the sides.
- **Hip roll:** free range −20..13° per leg, the same as v3. The 13° inward limit is boot against boot, and the arms don't limit it.
  - An interim geometry had the gripper touching the hip bracket at 15° outward. The sim soft limit was left at 15° outward as margin; the gaits use ≤ 13°.
  - Both hips rolling together: ±20°.
- **Knee:** −90..90° (v3: 84°). The shin cover is the limiting part.
- **Head:** pitch −40..5° (v3: −34..5°), roll ±6° (v3: ±5°).
- **Gait samples:**
  - both legs: 0 of 120 collide;
  - single leg at stock limits: 20 of 120, the same foot/ankle contacts as v3; the soft limits avoid them.
- **Arms vs torso, kilt, hips and legs:** no contacts found.
  - The arms sit on the torso sides, 41 mm out from centre at the shoulder boss, splayed 18°.
  - In the arm sweep (shoulder −10..110° × elbow −10..110°), every contact is the gripper, fingers or forearm hitting the chin collar or lower head when shoulder + elbow ≳ 110°.
- **Arm soft rule (v3.1):**
  - shoulder −5..84°, elbow ≤ min(110, 105 − shoulder); `collide_v3.py` and `sim/episode.py` both use it;
  - the sweep before tightening found 6 poses inside the earlier rule, elbow ≤ max(70, 125 − shoulder), that touched the collar, which is why it was tightened;
  - with the new rule: 0 of 24 boundary poses collide, and 0 arm contacts in 80 random walking + arm-swinging poses.
  - The sims ran with the earlier rule. Only the head+arm wave gets close to the new boundary (shoulder 80°, elbow 28° vs a cap of 25°), so the results are effectively unchanged.
  - v3's "elbow ≥ 14° when shoulder < 8°" rule is no longer needed.

## Sims (`sim/`, see `sim/compare_v3_v31.md`)
Same harness and tests as v3:
- standing, push recovery and head/arm motion from `run_tests.py`;
- walking: the v3 gaits re-evaluated on the v3.1 model over 20 randomized trials each (`walk_eval.py`; no new search);
- arm heat from `arm_heat.py`.

Only arm load, payload and the head/arm margin moved noticeably; see the table.

Videos:
- `sim/v31_push_recovery_v3.mp4/.gif`
- `sim/v31_walk_v3.mp4/.gif`, `sim/v31_walk_v3_eff.mp4/.gif`
- `sim/v31_head_arms_v3.mp4/.gif`: the frames were stored upside down by the offscreen renderer and were flipped afterwards.

## Renders (`renders/`)
- `compare_photo_v3_v31.png`: photo | v3 front | v3.1 front | v3 side | v3.1 side | v3 3/4 | v3.1 3/4, same scale; photo-angle 3/4 = az 15°, el 17°.
- `overlay_v31_on_photo.png`, `overlay_v3_on_photo_same_camera.png`, `overlay_photo_v3_v31_side_by_side.png`.
- `v31_three_quarter_photo_match.png`, `v31_front.png`, `v31_front_nokilt.png`, `v31_three_quarter_nokilt.png`, `v31_side_nokilt.png`, `v31_back_three_quarter.png`.

## Remaining differences from the photo
- **Head/shoulder** is 1.11 against the 1.16 target (photo 1.12 raw / 1.09 corrected). The shoulder sleeve has to enclose a 27.5 mm STS3032 on its axis, so each arm is about 34 mm thick against about 26 mm in the photo. The barrel is correspondingly slightly narrower than the photo's (88–95 mm vs about 100–103 mm).
- **Arms:** splayed 18° against 10–15° in the photo, needed to clear the hip brackets when the hips roll. Elbow span is 189 mm vs about 178.
- **Side profile:** the torso is deep front to back (148 mm) for the aft battery. The arms sit in the front third of the barrel, because the hip-yaw servos occupy the middle.
- **Colours:** the wood grain is colour only. The vine relief is simple.
- **Upper arm:** there is no wood cover over the wood upper-arm plate, which is visible only from the side and back.
- **Hip roll:** outward roll is limited to 15°.
- **Gripper payload** is lower than v3: about 50 g continuous at the fingertips, arm horizontal.
