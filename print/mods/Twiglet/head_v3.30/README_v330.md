# Twiglet head v3.30

## What changed vs v3.29 (nothing has been printed yet)
- WIG: the locks are now modelled in Blender (`blender/`, see `README_blender.md`). The v3.29 lock layout, smooth central fringe triangle,
  soft sideburns and temple flicks are kept. The locks are smooth, sleek and blended, with no serrated or clumpy edges.
  The seat, 4 pins, key and hat band are unchanged (procedural).
- SNOUT (Blender 4.5: `blender/face_v330_bpy.py`, with a 3 mm root fillet and wood-grain grooves; `snout_v330.py` was the Python draft): re-aimed from yaw -12 / pitch -6 to yaw -4 / pitch +22 deg, still 72 mm long. This raises the mouth to match the photos.
  It keeps the keyed spigot into the head_lower socket, and the root is trimmed inside the head-split lift cylinder.
- EYES (Blender 4.5: `blender/face_v330_bpy.py`; `eyes_v330.py` was the first Python draft and is not used): both eye assemblies are 4 mm lower (bezel + display carrier + screen move together; the 2 M3 carrier posts in head_lower are
  4 mm shorter with re-drilled heat-set insert holes; the lift sweeps are extended).
  The rings are round revolved bezels and smaller: dark disc 70.8 mm (was 74.4), window 59.6 mm, ring 5.6 mm wide.
  The flat wooden rim is wider (flat to rho 42, blend to 49 mm; 6.6 mm of flat wood around the ring, was 2.8).
  The old openings are filled back into the ball wall and re-cut.
- Head-half joint (4 M3 screws into heat-set inserts) and head_upper pin holes / key groove: unchanged.

## STLs (twiglet-head-v3.30-stl.zip = the WHOLE head set, print-ready)
Changed in v3.30: wig, snout, head_upper, head_lower, eye_bezel_L, eye_bezel_R, display_carrier_L, display_carrier_R (re-exported 4 mm lower).
Unchanged, included for completeness: chin_collar_L, chin_collar_R. The kilt pack is separate and unchanged.
Print: the shells, snout and collars in brown PETG; the wig in yellow PLA (lightning infill, tree supports); the bezels and carriers in black PLA (see print_note_head_v330.md).

## Scripts
eyes_v330.py, snout_v330.py, head_v330.py, hair_v330.py, face_v330.py (landmarks), render_v330.py, edge_render_v330.py, export_head_v330.py, blender/*.

## v3.30 head-range relief on the v3.31 rev C body (chin collars)
- CHIN COLLARS L/R changed (Blender 4.5, `blender/trim_collars_v330.py` on `head_v330.blend`; cutters from `blender/trim_v330/mk_collar_cutters.py`):
  side-hem relief: the band below 4.1 mm from the collar top is removed 64-122 deg either side of the chin (cosine ramps), so the collars clear
  the upper arms when the head rolls. Front 0-64 deg, both screw tabs (50 / 130 deg) and their holes untouched; wall 2.2-2.5 mm unchanged; one piece each.
  Plus a 1.8 mm clearance notch under the snout root (the v3.30 re-aimed snout overlapped the collar top-front edge by 0.6 mm3; now 0).
  10.33 -> 8.12 cm3 each. head_lower, snout, shells, wig, bezels, carriers unchanged.
- Whole printed head vs rev C torso shells / frame / leaves / kilt / arms at rest (315 poses, exact meshes): 235 -> 221 poses with contact; neutral overlap 0.
  Clean range from level: roll +-9 -> +-15 deg; forward pitch -45 (full); yaw +-160; back pitch +10 (unchanged).
- Not trimmed: head_lower back edge. The back-pitch contact is the roll-bearing holder tube that hangs below the shell at the back, not the shell edge.
  What-if (not applied): removing the holder alone gives +12; holder + rear collar segment gives +37 at yaw 0. The 4 collar screw tabs block most roll/yaw combinations.
- Checks: `blender/trim_v330/` (collar_trim / wall_collars / thin_check / post_checks json), `revC/head_body_check_trimF.json`, `simC/sweepF.txt`, `renders/collar_trim_v330_before_after.png`.

## v3.30 head-range redesign (roll-bearing holder + collar fixing + neck part) - supersedes the "Not trimmed" note above
- CHANGED: head_lower, chin_collar_L/R and head_yaw_to_roll (NECK MECHANICS part - print it instead of v39_head_yaw_to_roll from the body pack).
- head_lower: old inclined bearing strut / housing / lower hanger removed; new deck-hung housing for the same 20x32x7 bearing 12.1 mm further
  forward on the same roll axis (1.8 mm wall, bottom window, rear lip); 4 external collar tabs removed -> 4 internal bosses with vertical
  M3x5x4 heat-set inserts; back-bottom rim relieved (hidden from the front); rear ballast ledge for 25 g steel (keeps head-pitch hold >= 2x).
- chin collars: front band only (0-64 deg either side of the chin, look unchanged), 2 inward ledges each, M3x8 from below into the inserts.
- head_yaw_to_roll: tower + hub moved 12.1 mm forward (hub still slides 7 mm into the bearing), rear ring sector replaced by cross-bar + side arms.
- Range on rev C (exact, arms at rest): yaw-0 back pitch +9 -> +26 (bearing-limited; printed head alone +30), roll +-15 -> +-18; grid counts in
  revC/head_body_check_rd.json; mechanism limits fwd -36 and back +18 at yaw != 0 (neck yaw ring) unchanged.
- Not done (options): +35 back pitch needs a smaller roll bearing (e.g. 688 / 6800, ~+32-34) or a lower torso back; +-30 roll needs cutting the
  visible ball sides; yaw +-40..160 roll is limited by the collar front band at 48-64 deg (trim = front-corner look change).
- Scripts / checks: blender/redesign_v330.py, blender/redesign_v330/ (mk_redesign_parts.py, load_redesign.py, post_checks_rd.py, STATUS.md),
  simC/sweepR2.txt, renders/head_range_redesign_v330_before_after.png.
