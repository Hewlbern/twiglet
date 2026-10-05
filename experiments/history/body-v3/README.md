# Twiglet Open Duck: body v3 (proportion pass)

Goal: make the robot match the reference photo (`measure/photo.jpg`). The head stays at 170 mm (Head A with the digital eyes from `head-v3-digital-eyes/`), the robot is about 450 mm tall without the hat, and the shoulders are narrow. The legs and neck keep STS3215s with the same kinematics and servo count. The hat and kilt are fabric and are not printed.

## 1. Photo measurements (`measure/`)
- `measure_photo.py` produces `photo_measure.json` and the annotated `photo_measured.png`.
- `model_measure.py` produces `targets.json` (targets and achieved values for v3 and v2).
- The camera looks down: the view elevation is about 17° at the head, 24° at the waist and 38° at the floor. It was estimated from the torso-bottom ellipse. Vertical segments were corrected with a pinhole model (HFOV 60–80°, nominal 70°), scaled so the head is 170 mm. Uncorrected ratios are also in `photo_measure.json`. The photo looks like a render, so treat the figures as ±5–8%.

All segment ratios are divided by the head diameter D.

| Segment | Photo | **v3** (legs straight) | v2 |
|---|---|---|---|
| Head (visible height) | 0.816 | 0.771 | 0.771 |
| Neck / collar | 0.067 | 0.065 | 0.065 |
| Torso above the kilt | 0.30 | 0.312 | 0.659 |
| Kilt | 0.605 | 0.606 | 0.706 |
| Waist to knee | 0.745 | 0.834 | 0.922 |
| Shin (knee to boot top) | 0.309 | 0.239 | 0.496 |
| Boot / foot | 0.435 | 0.452 | 0.195 |

| Overall | Photo | **v3** | v2 |
|---|---|---|---|
| Height without hat (mm) | 454 (range 432–498) | 454 straight / 448 stance | 528 / 519 |
| Head / total height | 0.374 | 0.374 straight / 0.379 stance | 0.328 |
| Head / shoulder width | 1.12 raw, 1.09 corrected; target 1.16 | **1.166** (shoulders 146 mm) | 0.80 (213 mm) |
| Leg spacing (mm) | 113 | 100 | 90 |
| Knee height (mm) | about 126 | 117.5 | – |

Notes on the matches:
- The head reads shorter than in the photo because the photo's head includes the fringe and hair volume.
- The v3 boot includes the printed boot cuff.
- The shin (knee to boot top) cannot be shortened below the stock shin. The knee sits 8 mm lower than the photo's, because the stock hip yaw/roll/pitch stack sets the waist-to-knee length.

## 2. Design changes from v2 (`design_v3.py`, parameters in `build_report.json`)
**Legs and hips**
- Thigh link 22 mm shorter: new `v3_thigh_sheet_a/b` and `v3_thigh_spacer`. The shin is the stock part; the stock knee-to-ankle sheets are reused.
- Hips 20 mm forward under the COM (`DX_P` 20; the v2 sim fix).
- New `v3_hip_cradle`, `v3_hip_ring` and `v3_hip_bracket_L/R`.
- The legs are now 100 mm apart.

**Neck and head**
- Neck 10 mm shorter, with new `v3_neck_sheet_L/R`.
- The head sits 42 mm lower than in v2.
- The digital-eye head (head-v3) is reused unchanged and printed light: 2 walls and 8% gyroid, about 290 g printed.
- Orange eye-ring annuli are modelled on the head.

**Torso**
- Kept slim (90 mm overall, 67 mm front block) but deepened front to back to 146 mm.
- Battery moved 18 mm back and 7 mm lower as a counterweight.
- New `v3_torso_frame`, and a closed two-piece `v3_torso_shell_front/back`. The shell is split at x = −20 with tabs and has a 2 mm top lid.

**Arms**
- Six STS3032 micro bus servos replace the STS3215s. See `servo_choice.md` for real specs, prices and sources.
- New arm parts: `v3_upper_arm_L/R`, `v3_forearm_L/R`, `v3_gripper_housing_L/R`, `v3_finger_moving_L/R`.
- A **6 V buck** (for example Pololu D36V50F6) must feed the arm branch, because the STS3032 maximum is 7.4 V and a full 2S pack is 8.4 V.

**Kilt and boots**
- Kilt hem at 0.605 D (fabric).
- `v3_boot_cuff` is printed and slips over the stock foot.

**Totals:** 2.17 kg (v2 2.42 kg). COM height 233 mm (v2 262 mm).

## 3. Printable parts (`stl/`, `build_report.json`)
- 21 v3 STLs. All are watertight single bodies, fit the 256 mm P1S bed, and are exported in the orientation with the most bed contact. `build_report.json` lists quantity, size, colour, estimated mass and orientation for each.
- `stl/reused_head_v3/` holds copies of the head-v3 parts.
- Reused stock parts: STS3215 leg and neck assemblies, shin (knee-to-ankle) sheets, feet, and electronics.
- Print notes:
  - Suggested settings: PLA at 0.2 mm layers. Use 3+ walls and 15–25% infill for load-bearing parts (frame, hip parts, thigh and neck sheets, arm links).
  - The torso shell and the head parts use 2 walls and 8% gyroid; the sim mass assumes this light head print.
  - Let the slicer add supports where it needs them. Parts are already oriented for the most bed contact, but the frame and the gripper housings have overhangs.
  - Colours are listed per part.

## 4. Renders (`renders/`)
- `compare_photo_v2_v3.png`: photo, v2 and v3 front, and v2 and v3 side, all at the same scale. Red lines mark the photo's proportions.
- `overlay_v3_on_photo.png`: the v3 render overlaid on the photo (az 15°; `_az10` and `_az20` variants included).
- `v3_three_quarter_photo_match.png`, `v3_front.png`, `v3_front_nokilt.png`, `v3_side_nokilt.png`, `v3_back_three_quarter.png`, `v3_three_quarter_noshell.png`.
- `dev_*.png` are development views.

## 5. Collision check (`collide_v3.py`, output `collide_report.json`)
This uses the body-v2 mesh checker. Free joint ranges:

| Joint | Free range | Limit / note |
|---|---|---|
| Hip yaw | −16..8° | Soft limit ±7° |
| Hip roll | +20° outward, 13° inward | |
| Thigh forward | ≤12° | Same as stock |
| Knee | −90..84° | |
| Ankle | −65..47° | |
| Neck pitch | −1..4° | |
| Head pitch | −34..5° | |
| Head roll | ±5° | |
| Head yaw | ±160° | |
| Shoulder | −5..84° | |
| Elbow | −2..124° | |
| Gripper | 0..60° | |

Coupled arm rule: elbow ≤ max(30, 98 − shoulder), and elbow ≥ 14° when the shoulder is below 8°. There is no overhead wave, because the head sits on the shoulders.

Final run, with hip yaw soft-limited to ±7°:
- **Both-legs gait samples (120): 0 collisions.**
- Single-leg random samples: 15 of 120 collide. All of them involve thigh-forward >12° (the stock limit) or ankle >47°, which are outside the soft limits.
- Gait with the arms moving (80 samples): 1 collision. It happens with the shoulder at 0° and the elbow at 14°: the arm hangs straight down and the gripper housing touches the hip bracket when hip roll is about 6°. **Rule: keep the shoulder at ≥8° (the rest pose) while walking.**
- Arm-sweep contacts (81) are grid points outside the coupled rule or the ranges above.

## 6. Simulations (`sim/`, see `sim/README.md`)
The full table, stock vs v2 vs v3, is in `sim/compare_stock_v2_v3.md`, with `sim/plot_compare.png`.

Videos: `sim/push_recovery_v3.mp4/.gif`, `sim/walk_v3.mp4/.gif`, `sim/walk_v3_eff.mp4/.gif`, `sim/head_arms_v3.mp4/.gif`.

## 7. Trade-offs and risks
**Head and arm motion**
- Head motion is restricted: neck pitch −1..4°, head roll ±5°, head pitch −34..5°. The yaw is free.
- No overhead arm wave, limited arm back-swing, and a coupled elbow limit.
- Continuous waving must be capped at about 0.6 Hz. At 0.8 Hz the STS3032 is at 0.99× rated; at 1.5 Hz it is at 1.63×.
- The gripper is weak: about 8.8 N stall and 2.9 N continuous at the fingertip, against about 38 N for the Feetech STS3215 gripper. The photo's STS3215-size gripper modules are not used.

**Appearance**
- The arm column is 37 mm deep against about 26 mm in the photo, but the overall shoulder width matches (head/shoulder 1.166).
- The torso front looks narrower than the photo (67 mm front block against about 103 mm). The fabric kilt and the shell hide most of this.
- The knee is 8 mm lower than the photo's, because of the stock hip stack.

**Mechanics and power**
- Hip yaw is limited to ±7°, which is fine for walking but gives a reduced turn rate.
- A 6 V buck is needed for the STS3032s.
- The STS3032 costs about US$33–47 (€37 at Eckstein) against €24 for the STS3215: about +€77 for six.
- Walking current is higher than v2 (12.3 A average bus current on the max-speed gait) because v3 actually walks at 0.17 m/s.

**Software and model confidence**
- The Open Duck RL policy must be retrained for the new link lengths and mass distribution.
- A 0.08 rad stance offset is still used in the gait, but the robot stands with no pre-lean.
- The armature, heat and current figures are model estimates.
- Photo measurements carry ±5–8% uncertainty.
