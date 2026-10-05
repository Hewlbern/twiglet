# Twiglet body v3.32 (non-head body pass to match the photos)

Base: v3.31 rev C body + the final v3.30 head (unchanged). See CHANGED_PARTS_v332.md for the part list, print_sheet_body_v332.md for printing and TORSO_OPTION_v332.md for the costed (not built) "taller torso" option.

## Changes
- Arms: big black gripper box (29 x 45 x 53 mm) on the gripper housing, fingers +8 mm. The elbow stays black (exposed servo).
- Torso: chest vine added. The shells are kept as rev C, because trimming the dome detached the inner neck collar.
- Legs: brown shin block +6 mm. Thigh sheets re-specified BLACK, because the photos show no brown thigh block (brown is only between knee and ankle).
- Boots: sole rand lip and a rounded toe cap.
- Kilt: petals +12 mm (hem z -63.9).

## Checks (v3.32 vs rev C)
- Whole-head range (7x9x5 = 315 poses): 153 poses with any head contact, the same as rev C (153). No neutral gap under 3 mm.
- Arm sweep within soft limits: 0/162 contacts (rev C 0).
- Wig vs arm sweep (yaw 0/-45/45): 2/9/9 (rev C 0/7/7). All of these hits, in both versions, are outside the arm soft limits (shoulder 80-110 deg), so 0 are inside.
- Servo fit: housing vs S32 gripper servo 214.6 mm3, identical to rev C (press-fit sleeve). The housing has 0 overlap with forearm, horn and elbow. Finger sweep 0..60 deg is clear.
- Shins: rest overlaps match rev C; knee 0..90 and ankle +-45 sweeps are clear. Boots: 0 overlap with the foot parts; ankle sweep clear.
- Walls: housing 1.2 % of surface under 1.2 mm (finger-opening rims). Finger is the same as rev C (0.25 %). Boot 1.5 % (rev C 1.1 %). Petals 0.7-2.2 %. Shins are the same as rev C.
- Kilt +12 mm swing check (petals and hip ring vs legs/arms, rev C pose sets), v3.32 vs rev C (same tool):
  - sim gaits 0/1500 vs 0/1500; single-leg stance 0/14 vs 0.
  - Stress set gait120 single leg 10/120 vs 7; both legs 2/120 vs 1; arms+legs 1/80 vs 1.
  - The hot spot is petal 02 (front). These are the extreme pose sets, and the sim walking gaits make no contact.
- Photo IoU (aligned, mean): original view .444 -> .493, front .399 -> .435. Per part: kilt .52->.57, arm_R .29->.37, arm_L .39->.42, block_R .42->.48, block_L .45->.54, boot_R .64->.67, boot_L .66->.72, front arms .37/.36 -> .42/.42. Torso is unchanged (.18 / .47).

## Sims (MuJoCo, rev C test suite; masses: solid-PLA deltas, +104 g -> 2.714 kg)
- e-margin (head + arm motion): 34.7 mm (>= 32; rev C 33.1).
- Head-pitch stall/peak: 1.91 / 0.808 = 2.36x (>= 2; rev C 2.35x).
- Efficient gait: 20/20 (0.154 m/s; rev C 20/20, 0.161).
- Max-speed gait:
  - The rev C params give 17/20. Sensitivity: the gripper-box mass causes it (arm deltas only: 18/20; everything except the arms: 19/20).
  - After a light retune (2 rounds of walk_refine, 24 perturbations each, a few minutes) it reaches 20/20 at 0.187 m/s (rev C 19/20 at 0.209).
  - Held-out seeds 6000-6019: retuned v3.32 18/20, vs rev C params on the rev C model 16/20.
  - Retuned params: sim/walk_v3_best_v332r2.npy (the rev C params are kept as sim/walk_v3_best_rev_c.npy).

## Files
- blender/body_v332.blend: collections ARMS_v332, LEGS_v332, KILT_v332 and TORSO_v332 (asm frame). Rejected trials are in REJECTED_v332 (excluded from the view layer). Notes are in the text block V332_NOTES.
- blender/out/stl/v332_*.stl: print files. blender/out/asm/*.stl: the same parts in the assembly frame.
- sim/twiglet_v3_v332.xml: MJCF with the v3.32 masses. sim/sim_summary.txt holds all runs.
- metrics_v332.json: all metrics. STATUS.md: step log.
