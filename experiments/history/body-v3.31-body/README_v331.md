# Twiglet body v3.31 (body only; head/wig/snout/bezels untouched)

All body modelling was done in Blender 4.2 (bpy scripts, run headless). Python/trimesh was used only for checks and measurement.

## Files
- blender/body_v331.blend: live, non-destructive model. Objects:
  - TorsoShellFront_v331 / TorsoShellBack_v331 (modifiers: Lattice TorsoSlim, then Boolean FrameClearance)
  - TorsoSlim (lattice)
  - FrameClearance_0p25 (v3.9 frame + Displace 0.25 mm)
  - LeafChest0-2_v331
  - ShoulderLeafCluster
  - v3.9 reference objects
- Scripts:
  - blender/build_body_v331.py builds the .blend.
  - blender/export_body_v331.py exports the STLs.
  - blender/clean_kilt_v331.py cleans the kilt petals.
- Print STLs: blender/out/stl/. Assembly-frame meshes: blender/out/.
- Zip: $WORK/twiglet-body-v3.31-stl.zip (8.8 MB, 41 STLs plus print_sheet_body_v331.md).
- Comparison image: $WORK/body_compare_v331.png.

## Changes vs v3.9 body (= v3.8 design)
1. Lower torso slimmed with the lattice TorsoSlim: up to 4.8% in Y at z 38-56, about -2.4 mm per side, giving a straighter barrel like the photo.
   - The rows at z <= 36.3 (kilt-band seat) and z >= 59.5 (frame shoulder rails and bosses) are left at 1.0.
2. Shell-to-frame clearance: a Boolean DIFFERENCE (EXACT) against the frame grown 0.25 mm.
   - This removes the 584 mm^3 overlap that already existed in v3.9 (neck-column base on the top rails at z 84-86, shoulder-rail collars at z 60-68).
   - Internal faces only; the outer silhouette is unchanged.
3. Shoulder leaf cluster (3 leaves fanned ±38°) replaces the single leaf_L on each shoulder.
   - It uses the same peg and socket.
   - It was voxel-remeshed at 0.12 mm, giving a watertight single body.
4. Kilt petals (v3.16) cleaned in Blender: the 62 degenerate faces per petal were removed. Shape and volume are unchanged.

## Quick edit in Blender
1. Open blender/body_v331.blend and select the TorsoSlim lattice.
2. Press Tab, select one z-row of points (Alt+click or box select in side view), type `S Y 0.97` and press Enter, then Tab out.
   - Both shell halves and the chest leaves update live.
3. Leave the rows at z <= 36 and z >= 59.5 at 1.0. Otherwise the kilt band and frame rails no longer fit.
4. Re-export: `blender -b blender/body_v331.blend -P blender/export_body_v331.py`
5. Alternative: edit the `SLIM` knot list in build_body_v331.py and re-run `blender -b -P blender/build_body_v331.py`, then run the export.
6. Clearance: change the Displace strength on FrameClearance_0p25 (0.25 mm).

## Metrics (torso vs photo; masks aligned by best 2D shift, head not occluding)
| | v3.9 | v3.31 |
|---|---|---|
| Front shape IoU / outline err | 0.724 / 6.59 mm | 0.723 / 6.60 mm |
| Front widths top->bottom (photo 89/92/94/97/100) | 83/87/92/99/105 | 83/87/92/95/104 |
| Original-photo shape IoU / outline | 0.685 / 8.01 mm | 0.683 / 8.02 mm |
| Shell-frame interference | 584 mm^3 | 0 (min gap 0.13 mm) |
| Hip-yaw sweep min gap (±30° hard limit) | 4.58 mm | 1.68 mm |
| Arm sweep contacts (162 poses) | 0 | 0 |
| Walk max-speed / energy-aware | 100% 0.210 m/s / 100% 0.162 | 100% 0.208 m/s / 100% 0.162 |
| Mass | 2.584 kg | 2.586 kg |

IoU barely moves. The remaining mismatch is vertical: in the photo the torso sits about 55-60 mm lower under the head and is taller. That belongs to the head/neck stack and kilt line, which were not changed here. The top of the torso is about 6 mm narrower than the photo, but it can't be widened because the shoulder servo cases are 1.6 mm away.

## Caveats
- No slicer run, so g and h are formula estimates.
- The 0.25 mm frame cut leaves small paper-thin skins (0.02-0.4 mm, about 0.2-0.5% of the surface):
  - front: the shoulder-rail collars, z 61-64, |y| about 41;
  - back: the top-rail seat, z 85-87.
  - The slicer will drop these and leave slots where the frame rails sit. They are hidden under the head and arms. Check the slicer preview.
- torso_frame has a disconnected battery-pod island and needs a design change, so it is not in the pack.
- The sims use the v3.29 head. Arm-heat results are carried over.
- No head-pitch sweep re-run (the top of the shell is unchanged). No 3/4-photo IoU. No physical dry fit.
- Folder contains unmodified copies of about 194 .py and .json files from body-v3.29, needed for the sim/model imports.

## Rev B (2026-10-01 ~23:00-00:00; rebuilt 00:10-00:25 after the 00:02 folder reset)
- torso_frame: v3.8 frame + battery-pod struts (Boolean UNION in `blender/rev_b_v331.py`, collection FRAME_STRUTS_v331b: per side at |y| 25-31 a bar x -79..-56 z 15-23.8, a column x -62..-56 z 15-47, a gusset). One watertight body; prints back-rail face down.
- Torso shells: ThinSkinSlotCutter (boxes from `blender/in/thin_slots_v331b.json` + `_pass2.json` + `_pass3.json` (pass 3 re-probed by `work/f2/slots3.py`, 168 boxes, front only)), voxel-remeshed and subtracted; `blender/export_body_v331b.py` cleans and exports. Shell thin samples touching the frame cut: v3.9 14/49, rev A 43 -> 2/2 (of 8000, < 1.0 mm).
- Hip-yaw clearance profile SLIM_B: gap at the +/-30 deg hard limit 3.0 mm (v3.9 halves 3.4, rev A 1.7).
- Kilt petals thickened outward (`blender/thicken_kilt_v331b.py`, live Displace 'thicken' 0.32 mm on the outer skin + lip top).

## Rev C (2026-10-02 00:03-01:15)
Blender scripts (run in this order after the rev B chain `work/f2/run_b.sh` + `thicken_kilt_v331b.py`): `blender/rev_c_kilt_v331.py` -> `blender/rev_c_parts_v331.py` -> `blender/rev_c_band_v331.py`; all write `blender/body_v331c.blend` (collections KILT_v331b with the extra modifiers, KILT_CUTTERS_v331c, PARTS_v331c) and `blender/out/stl/`. Rev B outputs are kept in `blender/out_revB/`.
1. Head+arm balance margin (sim test e): rev B 22 mm -> **33.1 mm** (min 32). Cause: not the mass. With the rev B1 balance gains, the +17.9 g of petal thickening costs only 0.2 mm (33.3 -> 33.1; trunk COM moves ~1 mm). `sim/run_tests.py` re-searches the balance gains every run and the push-sum score is quantised by the bisection, so many gain sets tie; in rev B the tie went to a set with a positive ankle gain (+0.55) that leans the COM 43 mm forward during the head nod -> 22 mm. Fix (`sim/run_tests.py`, old copy `sim/run_tests_revB.py`): the rev A / B1 gain sets are added to the candidate pool, and among candidates within 10 % of the best push score the one with the largest head+arm margin is used (both the unfiltered best and its margin are written to results_v3.json). The B1 set now also has the best push score (5.976). Push recovery with controller 1.52/0.96/1.73/1.76 N s (B1 1.50/0.94/1.73/1.73), static margin 45.5 mm (B1 45.7), mass 2.607 kg.
2. Petals 05 + 07: Boolean DIFFERENCE 'rail_notch' with the frame back-rail corner (frame cropped to x -83.5..-72.5, z -1.5..27.5, grown ~0.6 mm, cut to x -81.5..-74.5, |y| 25..35.5, z 0.5..25.5). Frame/petal overlap 145.7 + 145.5 mm3 -> 0. The frame (rail corners, strut roots) is not touched.
3. Thin walls (>= 1.2 mm where it does not touch a fit face): petals 01/06 side edges (Displace 'edgefix' up to 0.8 mm, outer skin) + 'innerfix' top-up on the leg side below z 20 where an overlapping neighbour blocks outward growth; every petal's outward growth is now clamped to keep >= 0.1 mm to its neighbours and the frame (rev B had 0.67 mm3 overlaps at 00/01 and 01/02). kilt_band rim +0.07 mm inside (14.1 % -> 0.3 % under 1.2). Shin covers: thin hull-side faces moved outward in the cross-section plane by 1.25 - t (max 0.6 mm), inner faces / length / bed face kept (back 11.6-12.0 % -> 5.9-6.2 %, front 6.8-7.0 % -> 4.2-4.9 %). thigh_sheet_b recess floor 0.88 -> 1.23 mm (8.0 % -> 2.6 %). Not changed: shoulder_sleeve (coarse CAD mesh, the move distorted the end faces; fillet corners round the square arm bore), thigh_spacer (pin-bore ligaments), hip_bracket (bolt-circle ligaments), boot (cuff tip).
4. Checks: see `work/c3/` (parts_chk, wall_survey_c.json, ov57, fit_reg, kilt_swing_*.json). Servo/frame fit: shin covers + thigh_sheet_b registered into their link frames (ICP 0.01-0.1 mm) - overlap with the servo/black meshes identical to v3.9. `check_body_v331b.py`, `kilt_check_v316.py`, `gen_mjcf_v3.py`, `measure_body_v331.py` need `body-v3.29/.cache/v3model.pkl`, which the reset deleted; stand-ins were used (`work/c3/kilt_swing_v331c.py` = same pose sets with the sim render meshes + MuJoCo FK; the MJCF was made by adding the measured mass deltas to the rev B1 MJCF, `work/c3/mass_deltas_c.py`). `render_compare_v331c.py` rebuilds the comparison sheet from the sim render meshes.
5. Leg swing (`work/c3/kilt_swing_v331c.py`, poses as kilt_check_v316): sim gaits 0 contacts (rev A/B/C); collide gait120 single-leg 8/8/8 poses with a leg-petal contact (petal 01 now in 5 of them vs 4; contacts swing the hinged petal outward), both-legs 1/1/1, arms 0. Hip-yaw gap at +/-30 deg 3.01 mm (unchanged from rev B). Walks: max-speed gait 19/20 randomized (same as rev B1; rev A 20/20), efficient gait 20/20.
