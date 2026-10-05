# Twiglet body v2 (option 2: photo-accurate)

This is a new body for the ODM humanoid. It gives Twiglet narrow hips, legs directly under a slim wood-brown torso, arms hanging at his sides, and **head A unchanged** on top. The hat and kilt are fabric.

It uses the same 20 × STS3215 servos and the same electronics as the stock ODM. The stock leg links, arm links, fingers and boots are reused. All earlier parts are left untouched; the new parts are the `v2_*` files.

Renders are in `renders/`. The comparison sheet is `renders/compare_photo_current_opt1_opt2.png` (reference photo, current build, option 1, option 2). The simulation is described in `sim/README.md`.

## New printed parts (`stl/`)
All exports are watertight, a single body each, and fit a Bambu P1S.

| Part | Size (mm) | Est. g | Colour | Print orientation |
|---|---|---|---|---|
| v2_torso_frame | 94.5×80×119.5 | 85 | grey (hidden) | back rail face down; tree supports under the deck, yaw sleeves and neck cradle |
| v2_hip_cradle | 63×79×72 | 13 | grey (hidden) | keel down, supports under the T-heads. **PETG, 100% infill** (it is slender) |
| v2_hip_ring | 132×106×16 | 20 | wood brown (under the kilt) | flat, groove up, no supports |
| v2_hip_bracket_L/R | 48×54×75 | 21 each | black | sleeve axis vertical, supports under the webs |
| v2_shoulder_mount_L/R | 32×52×69 | 19 each | wood brown | side plate down, no supports |
| v2_torso_shell_front | 93×98×81 | 34 | wood brown | split face down; tree supports under the shoulder-window tops |
| v2_torso_shell_back | 96×98×58 | 39 | wood brown | split face down; bridge over the switch slot |

- Default print settings: PLA, 0.2 mm layers, 3 walls, 15% gyroid infill.
- Reused from `../stl/`: `twiglet_arm_link_*`, `twiglet_finger_*`, `twiglet_boot_*`.
- In the zip, the reused files are in `stl_reused/`.
- Also reused: the stock ODM leg and hip-yaw parts.
- `v2_shoulder_mount` replaces the old `twiglet_shoulder_mount`.

## Assembly
1. **Frame and hip yaw servos.** Seat both hip-yaw STS3215 in the `torso_frame` sleeves. The back rail carries the battery tray: 2 × 18650 cells in the holder, with the tray floor and side lips.
2. **Hip cradle.** Press the bearings into the cradle's 35 mm seats. Bolt the cradle under the deck using the T-head posts.
3. **Hip brackets.** Fit them on the yaw horns, then fit the stock hip-roll, pitch and leg chain. The legs sit 45 mm either side of the centreline (the stock ODM is much wider).
4. **Electronics.**
   - The BMS and the charger stand upright in front of the back rail. The charger's USB-C port points down, so you reach it by lifting the kilt.
   - The Waveshare bus-servo board and the Pi Zero 2W stack flat on the yaw sleeves (z 87 and 94).
   - The BNO055 IMU stands on the rail's front face.
   - The power switch sits in the slot in the back shell, left of the battery.
   - Neck, arm and head cables pass up through the neck-sheet slots.
5. **Neck and head.** The neck servo cradle is on the frame front, and head A mounts on it unchanged. The head sits 20 mm lower than on the stock build, right on the shoulders like in the photo.
6. **Shoulder mounts.** Each takes 4 × M3 heat-set inserts and bolts to the frame's side rails. The shoulder servo drops into the mount's pocket.
7. **Shell.** The front and back halves join at x = −30 with 4 inner lap tabs and M2.5 screws. Shoulder windows let the arms swing.
8. **Kilt ring.** It clips around the waist. The fabric kilt hooks into the ring's groove through its 12 hook holes.

## Stance and soft limits
**Stance**
- Walking stance: crouch 0.30 with a 0.17 rad forward lean. Without the lean the robot falls forward in the sim.
- Idle stance: straighter (crouch about 0.1) to cut knee load.

**Soft limits** (from `collide_report.json`)

| Joint | Limit |
|---|---|
| Hip roll | ±20 with both legs together; on one leg, inward roll ≤ 9 and the difference between legs ≤ 9° |
| Thigh forward | ≤ 12 (the same hard stop as the stock ODM) |
| Ankle | −65..+47 |
| Hip yaw | ±30 |
| Neck | −5..15 |
| Head pitch | −45..22; ≤ 5 in practice (see head rules) |
| Head roll | ≤ 10 |
| Shoulder | −12..103; if below 0, keep the elbow ≥ 20 |
| Elbow | −20..103; don't combine shoulder > 85 with elbow > 85 |

- Head rules: when |roll| > 5, keep head pitch ≤ 0. When |yaw| > 45, keep head pitch ≤ 0, and ≤ −10 if you are also rolling. Also keep neck − head pitch ≤ 55°: with the neck fully up and the chin tucked, the chin collar hits the shoulder mount. With all these rules the head grid (588 poses) was collision-free.
- With these rules there were no collisions in the rest pose, in 120 walking samples, or in the head and arm sweeps.

## BOM changes vs the stock ODM
**Added**
- **Digital eyes:** 2 × 2.1" round 480×480 displays (e.g. Waveshare), about 30 g each with the PCB, plus an ESP32-S3 or RP2040 driver (about 10 g). They show animated orange-ring and pupil eyes.
  - Extra power: about 0.5–1 W, roughly 0.1 A at 7.4 V. That is about 1–2% of the walking draw (8–10 A peaks).
  - Budgeted in the sim at 70 g in the head.
  - The head's eye sockets will be redesigned separately. **This body release does not change the head.**
- 12 × M3 heat-set inserts (8 for the shoulder mounts plus spares for the frame).
- About 8 × M2.5×8 screws (shell tabs and the hip cradle).
- 2 bearings for the cradle, the same type as the stock hip bearings.

**Removed**
- The printed eye cups, orange rings and eye LEDs.
- The stock chest/pelvis shell parts.
- The SG90 antennas and the cache covers.

**Unchanged:** 20 × STS3215, the Waveshare bus board, Pi Zero 2W, 2 × 18650 with BMS and charger, and the BNO055. They are only relocated.

## Design trade-offs (read before building)
| Aspect | v2 | stock | Notes |
|---|---|---|---|
| Height | 519 mm | 504 (opt1) | head/height 0.33, like Twiglet's chibi look |
| Leg spread | 143 mm | 246 mm | |
| Shoulder width | 213 mm | 117 (opt1, arms in front) | head/shoulder 0.80 vs about 1.16 in the photo |
| Side tipping angle | 13.9° | 29° | |
| Front tipping angle | 4.6° | 13° | |
| Walking speed (open-loop gaits) | 0.05–0.08 m/s | 0.19–0.21 m/s | |
| Standing current | 8 A | 4 A | |

- The shoulders are wider than in the photo because the STS3215 arms are thick and the hip modules sweep a lot of space. Possible fixes are forward-canted arms or micro servos in the arms.
- The main problem is a nose-heavy upper body. Head A is about 480 g with its servos, and the COM sits about 40 mm ahead of the hip-pitch axis. That makes the knees and hips carry 0.7–0.9 N·m standing, above the 0.49 N·m rated torque.
- The RL walking policy must be retrained on `sim/twiglet_v2.xml`.

## Recommendation
Build **option 2** with these changes:
1. Print the head light (2 walls, 5–10% infill). This saves about 100 g and about 0.1 N·m at each joint.
2. Raise the servo P gain (Kp about 20). This halves the sag.
3. Use the straighter idle stance and keep IMU balance on.
4. Plan v2.1 with the hips moved 25 mm forward (this needs the neck servo relocated). Static torque roughly halves.

Use **option 1** (the stock ODM with Twiglet parts) only as a robust fallback. It is not photo-accurate: the legs are wide, the arms sit in front of the trunk, and it weighs 2.73 kg.

## Scripts
| Script | Purpose |
|---|---|
| `design_v2.py` | Parametric parts |
| `view_v2.py` | Dev renders |
| `export_v2.py` | STL export and `build_report.json` |
| `collide_v2.py` | Collision study |
| `render_options.py` | Option renders and the comparison sheet |

Python: `$PYTHON`. pyvista needs `xvfb-run -a -s "-screen 0 1600x1600x24"`.
