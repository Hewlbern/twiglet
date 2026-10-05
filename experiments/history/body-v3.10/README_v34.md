# Twiglet body v3.4: head moved back, cone torso

Built from v3.3 (body-v3.3/ is unchanged). Changes answer the feedback "head not over the middle, body should be one cone".

## What changed
- **Neck stack 1.5 mm rearward** (DXN 18 -> 16.5; NECK_COL and HEAD_Q follow). This is the hard limit: the trunk neck-pitch servo sits right in front of
  the hip-roll horn plates of both hip brackets (x -2..3). At 7 deg hip yaw the plates swing ~1 mm forward and ~4 mm inboard. A 7 mm and a 3 mm shift were
  both built and failed the collision check (rest clash / gait clash). The neck-servo cradle rear wall and floor are now only a |y|<4 centre strip, and the
  hip-bracket front web is trimmed inboard (y>=26).
- **Cone torso shell** (torso_env_v34.py -> torso_env_v34.json): station rings = convex hull of the internals (incl. +-7 deg hip-yaw sweep, neck parts)
  + 2.6 mm, 45 deg chamfer, flared toward the waist, domed into the neck column. Shell section w x d: z25 109 x 128 -> z60 89 x 114 -> z86.5 77 x 99 ->
  neck column 51 wide. **Depth 155.5 -> 133.1 mm** (x -86.3..46.8). The torso axis moved 12 mm forward (centre x -32.2 -> -19.8).
- **Battery moved low**: the pod (cells along y) sits behind the hips under the kilt (x -71..-51, z -28..13); BMS and charger go on the pod rail front,
  boards and IMU at z 15-48; power switch and access slot lowered with them. The old battery floor and upper rail are removed.
- Kilt rendered as a bell continuing the cone (render_v34.py).
- Arms unchanged at 13 deg splay, still flush (no arm vs shell/frame contacts in the sweep).

## Head centre (stance pose, x mm, + = forward)
| | head centre | vs boot centre (12.0) | vs ankle (-0.2) | vs torso centre |
|---|---|---|---|---|
| v3.3 | 36.6 | +24.6 | +36.8 | +68.8 |
| v3.4 | 35.1 | +23.1 | +35.3 | +54.9 |

Full centring over the hips (~-20 mm more) needs a neck and hip-yaw redesign. Examples: drop the low neck-pitch DOF (its soft range is only -1..+3 deg),
or re-route the hip-yaw and hip-roll stack so the neck servo can sit over the hip axis.

## Head parts
No head reprint. Head shells, fringe, bezels, carriers and chin collars are byte-identical to v3.3 (stl/v33_head_*.stl). The roll mount relative to the
neck stack is unchanged.

## Checks
- neck/head sweep: clean within the soft limits (neck -1..+3, head pitch -34..0, combined forward <= 3 deg)
- collide_v3: 0 rest clashes; gait both-legs 0, gait+arms 0, single-leg 20 (same leg-spacer cases as v3.3); arm sweep 55 (all arm-vs-head, same arm rule)
- sims: sim/compare_v33_v34.md
- STLs: 37 parts, all watertight, 1 body each, all fit the P1S (build_report.json)
