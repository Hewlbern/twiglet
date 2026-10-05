# Twiglet body v3.5: head centred on a fixed neck post

Built from v3.4 (body-v3.4/ is unchanged).

## What changed
- **Low neck-pitch STS3215 removed** (it only moved -1..+3 deg). The head-pitch servo (still hanging below its axis) is now bolted into a cup cradle
  on the torso frame (fixed neck post); `neck_pitch_assembly` is merged into the trunk and `head_pitch` hangs off the trunk (19 joints, 13 STS3215).
- **Head stack 15.6 mm rearward** (pitch axis x 17.5 -> 1.9). Limit: the rear face of the head-pitch servo sits 0.4 mm in front of the hip-yaw
  servo cases (x -10.9). The sleeve front walls are notched at |y| < 21 for it.
- **Head 3 mm further back relative to the yaw servo** (HEAD_RX): the non-head `head_yaw_to_roll` bracket is re-cut, moving its roll-horn wall and rear bearing arm
  3 mm back (front wall 2.8 mm, yaw-servo pocket kept). The head, roll servo and roll mount move as one unit, so the interface is unchanged.
- Front plate moved 12 mm back with the servo, which re-fits the cone. **Depth 133.1 -> 117.5 mm** (x -86.3..31.2); the neck column is now centred
  under the head (bore x -21.6..21.4). The back is still set by the hip-yaw servos (x -58.5 with sleeves).
- A forward-pointing (horizontal) head-pitch servo was tried first. It allows the pitch axis at x -0.4, but nose-down pitch then stops at -5 deg because the yaw stack lands on the servo, so it was rejected.
- Head-pitch soft range -38..+4 deg (collision-free -40..+6; v3.4: -34..0 plus neck -1..+3).

## Head centre (stance pose, x mm, + = forward)
| | head centre | vs boot centre (12.0) | vs ankle (-0.2) |
|---|---|---|---|
| v3.4 | 35.1 | +23.1 | +35.3 |
| v3.5 | 16.5 | **+4.5** | +16.7 |

## Head parts
No reprint. Head shells, fringe, bezels, carriers and chin collars are byte-identical (stl/v33_head_*.stl), and the roll mount is unchanged.
Re-print the non-head parts: v35_head_yaw_to_roll, torso_frame, torso_shell_front/back. The neck sheets are no longer needed.

## Checks
- nsweep35.py: rest clean; head pitch clear -40..+6 at all yaw (+-150) / roll (+-5)
- collide_v3: 0 rest clashes; gait both-legs 0, gait+arms 0, single-leg 20 (same leg-spacer cases as v3.3/v3.4); arm sweep 52 (arm vs head only)
- sims: sim/compare_v34_v35.md (gait re-tuned; walk 100% at 0.171 m/s, energy-aware 100% at 0.143 m/s)
- STLs: 36 parts, all watertight, 1 body each, all fit the P1S (build_report.json); BOM delta: bom_v35.md
