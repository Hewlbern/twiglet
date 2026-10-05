# Twiglet v3.19: lock-by-lock photo match (only the wig changed)

**Method**
1. Zoomed, upscaled hair crops of the three photos are in measure319/crop_*.png. The lock table built from them is lock_table_v319.md.
2. `measure_v319.py` does the measured check:
   - **Photo masks:** hair is segmented by HSV colour. Blond reads hue 29-62 in the warmer original photo and 34-62 in the other two; saturation > 0.28, value > 0.42.
   - **Model masks:** the model is rendered with flat colours: hair, an opaque felt hat, and everything else grey.
   - **Camera fit (per photo):** a pinhole camera over a grid of distance, azimuth and elevation. Scale comes from the 210 mm head-ball outline radius. Rotation and translation come from the ball centre and both eye-screen centres, with the snout mouth as a weak landmark. All landmarks were picked by hand.
   - **Comparison:** the model mask is warped into the photo frame, and the eye screens are masked out of both.
   - **Reported per photo:** IoU; IoU outside the model hat's footprint (the felt hat sits lower on the model than in the photos, which is not a wig issue); and outline distance (mean of both directed contour distances, in mm at hair depth).
3. v3.18 and every v3.19 iteration were measured with the same script. The arm sweep ran alongside, so arm clearance limited how far the side locks could go.

**Changes vs v3.18**

Fringe:
- The fringe now points down, as in all three photos, instead of v3.18's swept-up parting.
- 5 locks: a broad centre triangle (tip between the eyes), two short locks resting on the upper bezel rings, and two long outer locks curling out.

Sides:
- Eye-level side flares are bigger (27 mm crest) and stick out further (FLARE SIDE 40 mm).
- Long S-swept side locks hang to jaw level. The robot's right rear lock is longer, as in the 3/4 photo.
- The lock ends are trimmed below th 86 deg in the azimuth band phi +-66..102 deg. This is where the raised forearms pass when the head is yawed (ARM_CUT).

Kept from v3.18: the S-curve and twist on every lock, the >= 1.3 mm edge lip and the smooth crown.

Other checks:
- Eye coverage: 0.0% / 0.0%.
- Crown blend: 0 kinks over 20 deg.
- head_upper is identical to v3.16-v3.18 (volume 123105.5 mm3, 325188 faces, same pins and key).
- Zero overlap with every head part, bezel and the snout.
- Walls: minimum 1.15 mm (excluding tips), p1 2.1 mm, median 9.6 mm.

**Wig.** One piece, 213 x 247 x 220 mm (fits the P1S bed). About 153 g at 3% lightning infill, plus about 33 g of support, about 11.7 h.

**Silhouette match**

| Photo | IoU v3.18 | IoU v3.19 | IoU outside hat v3.18 | IoU outside hat v3.19 | Outline v3.18 (mm) | Outline v3.19 (mm) |
|---|---|---|---|---|---|---|
| Original (primary) | 0.354 | 0.381 | 0.525 | 0.563 | 15.5 | 12.6 |
| Front | 0.485 | 0.493 | 0.570 | 0.571 | 8.5 | 6.5 |
| 3/4 | 0.502 | 0.516 | 0.579 | 0.585 | 10.2 | 7.5 |

Outline distances are measured outside the hat footprint.

**Infill sweep** (head+arm minimum margin, mm):

| Wig infill | 0% | 3% | 4% | 5% | 6% | 8% |
|---|---|---|---|---|---|---|
| Margin (mm) | 30.0 | **33.3** | 31.3 | 30.2 | 31.8 | 30.1 |

3% lightning infill is the chosen setting.

**Light checks**
- Arm sweep vs wig, contacts at head yaw 0/-45/+45: 0/11/11 of 156 poses each (v3.18: 0/14/14).
- Head range (315 poses): 36 wig contacts (v3.18: 8). The extra contacts come from the longer jaw-length side and rear locks meeting the torso or forearms at combined pitch and roll corner poses.

**Sims.** Both gaits were re-tuned locally with walk_refine (max-speed: 95% before, 100% after; energy-aware: 95% before, 100% after, using REFINE_SEED=33 because the default seed found no improvement). The pre-refine parameters are in sim/bak_pre_refine_v319/.

| Metric | v3.18 | v3.19 |
|---|---|---|
| Total mass (kg) | 2.537 | 2.54 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 244.5 | 244.5 |
| Support margin front / back / side (mm) | 57 / 45 / 70 | 58 / 44 / 70 |
| Tipping angle side / front (deg) | 16.0 / 13.1 | 16.0 / 13.3 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.23 (0.46x) / 0.37 (0.75x) / 0.06 | 0.22 (0.45x) / 0.36 (0.74x) / 0.05 |
| Static neck pitch / head pitch N·m standing (x 0.49 rated) | 0.000 (0.00x) / 0.205 (0.42x) | 0.000 (0.00x) / 0.197 (0.40x) |
| Standing bus current (A) | 4.27 | 4.2 |
| Push survived, no controller F/B/L/R (N·s) | 1.34 / 1.05 / 1.64 / 1.66 | 1.36 / 1.03 / 1.64 / 1.66 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.50 / 0.91 / 1.69 / 1.71 | 1.48 / 0.91 / 1.69 / 1.71 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.00 / 0.00 | 0.00 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.182 m/s / 11.03 A | 100% / 0.177 m/s / 11.08 A |
| Walk energy-aware: success / speed / current | 100% / 0.150 m/s / 10.43 A | 100% / 0.148 m/s / 10.55 A |
| Head+arm test: fell / min margin / neck peak | no / 32.7 mm / n/a (no joint) N·m | no / 33.3 mm / n/a (no joint) N·m |
| Head+arm test peaks: head pitch / yaw / roll (N·m) | 0.761 / 0.774 / 0.374 | 0.755 / 0.774 / 0.378 |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.76 / 1.01 / 1.66 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.30 / 0.52 / 1.41 | 0.30 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.066 (0.45x) | 0.066 (0.45x) |
| Fingertip payload continuous / brief (g), arm horizontal | 49 / 228 | 49 / 228 |
| Arm mass per side (g) | 99 | 99 |

Walks: nominal + 20 randomized 10 s trials (walk_eval.py). Arm-heat rows: arm links unchanged since v3.8 (arm_heat_v3.json carried over) (arm_heat_v3.json carried over).
