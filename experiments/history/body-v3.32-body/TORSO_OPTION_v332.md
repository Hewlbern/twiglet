# Costed option (ANALYSIS ONLY, not built): photo-like torso, ~40 mm more torso between kilt and head

## The gap
In the photos (cameras fitted on the head), the torso centroid sits 37-47 mm lower relative to the head than in the model, and the visible torso is about 96 mm tall vs 57 mm on ours.
The head/neck stack is fixed: head-pitch axis at z 90, roll 128, yaw 147 (trunk frame). The ODM hip height is fixed too: hip yaw 45.9, hip pitch -44.1, knee -100.7, ankle -179.4.
So the photo proportions need the head to sit further above the hips. Shorter legs alone lower the whole robot and do not add visible torso.

## Options (sims: run_all.sh with the v3.32 masses and the v3.32 retuned max-speed gait; head range: hb_check, 7x9x5 grid, poses with any head contact)
| | A: neck riser +40 mm + torso shells 40 mm taller | B: A + legs 40 mm shorter (thigh -8 / shin -32, feasible split) | B': A + legs -20/-20 (NOT feasible, reference) | v3.32 (built) |
|---|---|---|---|---|
| e-margin (head+arm motion) | 34.4 mm | 32.0 mm (at the 32 limit) | 34.5 | 34.7 |
| head-pitch stall/peak | 2.36x | 2.29x | 2.27x | 2.36x |
| max-speed gait (seeds 5000-19) | 13/20 (needs a retune) | 17/20 (needs a gait re-search) | 20/20 | 20/20 |
| efficient gait | 19/20 | 20/20 | 20/20 | 20/20 |
| speed max / eff (m/s) | 0.182 / 0.151 | 0.116 / 0.100 (-38 % / -35 %) | 0.154 / 0.106 | 0.187 / 0.154 |
| CoM above foot origin | 224.8 mm (+14) | 189.0 mm (-22) | 189.9 | 210.6 |
| total mass | +40 g (riser 15 g + taller shells 25 g) | +40 g | +40 g | 2.714 kg |
| head range (poses with contact /315) | riser with rev C shells: 37 (v3.32: 153). With the shells raised to follow the head, it returns to about 153 (same neck geometry). | same as A | same | 153 |

## What it would take
**A (neck riser + taller torso), about 1 day of agent work and about 8 h of printing:**
- New printed neck riser (PETG/PLA+, ~15 g) between the frame's neck cradle and the head-pitch bracket, plus 40 mm longer head servo leads.
- torso_shell_front/back re-modelled 40 mm taller, then re-cut for the shoulder rails and neck collar (~25 g more).
- The chin collars / head side need sign-off from the head owner, because the head moves up 40 mm.
- Sims: margin and pitch are fine, but the max-speed gait falls to 13/20 and needs a retune (walk_refine, cheap). The efficient gait gives 19/20.
- The arms clear the wig better, because the head is 40 mm higher.

**B (A + shorter legs), about 2-3 days and about 12 h of printing, plus a gait re-search:**
- Custom thigh sheets (-8 mm) and shin sheets (-32 mm) replace the stock ODM sheets, which are fixed at 56.6 / 78.6 mm joint-to-joint.
  - At rest, the servo cases leave only 9.2 mm (thigh) and 33.5 mm (shin) of room, so -8/-32 is the maximum split.
  - Shin covers and boots shorten or change with it.
  - The kilt then sits 8 mm closer to the knee, so the swing check has to be redone (expect more petal contacts).
- Same height and CoM as today (head at the same height), and the proportions match the photo (long torso, short legs).
- Walking cost: about 35-38 % slower at the same joint amplitudes, and the max-speed gait falls to 17/20.
  - Needs a full walk_search (several CPU hours) plus new IK/joint offsets for the ODM policy.
  - The e-margin falls right to the 32 mm limit.

Recommendation: if the look matters, A is the cheaper path (margin and pitch hold are kept, and only a light gait retune is needed). B gets closest to the photo, but it means new leg structure and a full gait re-search.
Model files: sim/torso_option.py builds sim/twiglet_v3_opt_neck40*.xml; measure/hb_check_dz.py is the riser head-range check.
