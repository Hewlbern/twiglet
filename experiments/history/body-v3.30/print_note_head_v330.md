# Twiglet head v3.30 - print note (Blender-modelled one-piece wig + re-aimed snout + lowered, rounder eyes; wig attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v330_head_wig.stl | 244.9 x 240.0 x 242.8 | yes | 187 (+51) | 14.8 | 142.3 |
| v330_head_snout.stl | 71.6 x 71.6 x 101.5 | yes | 54 (+5) | 3.7 | 12.1 |
| v330_head_head_upper.stl | 207.9 x 207.9 x 90.3 | yes | 143 (+14) | 9.8 | 197.6 |
| v330_head_head_lower.stl | 209.0 x 210.0 x 72.9 | yes | 177 (+18) | 12.2 | 347.6 |
| v330_head_eye_bezel_L.stl | 70.8 x 70.8 x 6.3 | yes | 5 (+0) | 0.3 | 0.8 |
| v330_head_eye_bezel_R.stl | 70.8 x 70.8 x 6.3 | yes | 5 (+0) | 0.3 | 0.8 |
| v330_head_display_carrier_L.stl | 71.2 x 71.2 x 24.8 | yes | 9 (+1) | 0.6 | 5.9 |
| v330_head_display_carrier_R.stl | 71.2 x 71.2 x 24.8 | yes | 9 (+1) | 0.6 | 5.9 |
| v330_head_chin_collar_L.stl | 55.2 x 79.8 x 13.6 | yes | 4 (+0) | 0.3 | 0.1 |
| v330_head_chin_collar_R.stl | 55.3 x 79.8 x 13.6 | yes | 4 (+0) | 0.3 | 0.1 |
| v330_head_head_yaw_to_roll.stl | 77.2 x 80.0 x 42.2 | yes | 20 (+2) | 1.4 | 10.1 |

## Print list (vs v3.29)
- NOTHING HAS BEEN PRINTED YET, so print the full head set. CHANGED in v3.30 (all in this zip): wig (Blender locks), snout (re-aimed, mouth raised), head_upper + head_lower (eye openings 4 mm lower, wider wood rim, carrier posts shortened), eye_bezel_L/R (round, smaller ring), display_carrier_L/R (same shape, re-exported at the new height), head_lower + chin_collar_L/R + head_yaw_to_roll (HEAD-RANGE REDESIGN: roll-bearing holder moved forward, collar tabs -> internal insert bosses, collars cut to the front band, neck part rear re-cut - see 'Head-range redesign' below). head_yaw_to_roll is a NECK MECHANICS part: print this one INSTEAD of v39_head_yaw_to_roll from the body pack.
- Head range on the v3.31 rev C body (whole printed head vs torso shells / frame / leaves / kilt / arms at rest, 315-pose grid pitch +-45 / yaw +-160 / roll +-30): whole head 221 -> 153 of 315 grid poses with any contact (exact meshes, arms at rest; v3.30a trimmed collars -> head-range redesign); clean range from level at yaw 0: back pitch +9 -> +26 deg (now limited by the roll bearing itself vs the back torso shell; printed head alone +30), roll +-15 -> +-18 deg (head_lower side shell vs upper arms), forward pitch -36 (neck yaw ring vs front torso shell, unchanged), yaw +-160; at yaw != 0 back pitch +18-19 (neck yaw-ring sides, unchanged).

## Head-range redesign (v3.30) - assembly
- Roll bearing: the same 20x32x7 bearing, now pressed into the new head_lower housing (12.1 mm further forward on the same roll axis; the bearing outer ring shows through the housing's bottom window - that is intended, 282 deg wrap + rear lip hold it). The new head_yaw_to_roll hub slides 7 mm into it exactly as before; assembly order as the ODM guide.
- Chin collars: press 4 x M3 x 5 x 4 mm heat-set inserts (vertical, from below) into the 4 bosses inside the head_lower rim; each collar's 2 inner ledges then take 2 x M3 x 8 screws from below up into them (4 screws total). The old 4 radial collar screws / external tabs are gone.
- BALLAST (required, 25 g steel): moving the bearing forward and removing the rear strut / tabs moved the head COM forward (head-pitch hold would drop to 1.9x). Epoxy 25 g of steel on the new ledge inside the back of head_lower, against the shell, centred on the rear centreline within +-30 deg (e.g. 5 x M8 hex nuts standing on edge, or 5 x 5 g adhesive wheel-balance weights cut to <= 14 mm tall). Weigh it: 23-27 g. The sims include exactly this.
- Range achieved (exact, rev C body, arms at rest): back pitch at yaw 0 +26 deg (was +9/+10; now limited by the roll bearing itself touching the back torso shell - the printed head alone clears +30), roll at yaw 0 +-18 deg (was +-15; limited by the head_lower side shell vs the upper arms - more would cut the visible ball sides), forward pitch -36 (neck ring vs front torso shell, unchanged), back pitch at yaw != 0 +18-19 (neck yaw-ring sides, unchanged).
- The head-half joint (4 M3 screws into heat-set inserts), head_upper pin holes + key groove and the snout socket are unchanged. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).
- Sim basis (v3.30 on the v3.31 rev C body): every head part is simulated at 2 walls (0.8 mm) + 8 % infill (wig 4.5 % lightning); head_upper / head_lower / snout / chin collars at PETG 1.27 g/cm3, the rest PLA 1.24. Print exactly these settings (heavier shells move the head COM forward and up).
- Materials: head_upper, head_lower, snout, chin collars = wood-brown PETG; wig = yellow / blond PLA (lightning infill, tree supports); eye bezels + display carriers = matte black PLA.

## Per-part orientation / supports / infill

| part | material | orientation (as exported) | supports | settings / infill |
|---|---|---|---|---|
| v330_head_wig.stl | yellow / blond matte PLA | as exported: crown axis tilted 56 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs | tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim | 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 4.5 % LIGHTNING - REQUIRED: the sims assume this wig at 4.5 % (simC/sweepR2.txt (v3.31 rev C body, head-range redesign incl. 25 g rear ballast, PETG head shells): margin 33.5 / 33.5 / 33.3 / 33.1 / 32.1 mm at 0 / 2 / 3 / 4.5 / 6 % wig infill; 4.5 % stays the required value (>= 32 mm everywhere, head-pitch hold 2.10x at 4.5 %).), so print exactly that |
| v330_head_snout.stl | wood brown PETG | as exported: mouth face DOWN on the bed (flat rim annulus), spigot + key tab up | none needed (the root plug / spigot are bridged by the cone) | brown PETG (240-250 C, bed 70-80 C): 0.2 mm layers (0.16 mm makes the grain pop), 2 walls (0.8 mm), 8 % gyroid - the sims assume 8 % |
| v330_head_head_upper.stl | wood brown PETG | split-plane rim down (dome up) | tree supports INSIDE only (crown above ~60 deg, hidden under the hat) + the two eye bores' top edge | brown PETG: 0.16 mm layers, 2 walls (0.8 mm) + 3 top / 3 bottom, 8 % gyroid - the sims assume exactly this at 1.27 g/cm3 (3 walls / 15 % would add ~130 g to the head and break the head-pitch and balance margins); slicer modifier (4 walls, 40 %) only on the M3 heat-set insert bosses / screw holes (~2 g); 240-250 C nozzle / 70-80 C bed, textured PEI (glue stick as release), part fan 30-50 % |
| v330_head_head_lower.stl | wood brown PETG | split-plane rim down | tree supports inside the eye bores' upper edges, as before | brown PETG: 0.16 mm layers, 2 walls (0.8 mm) + 3 top / 3 bottom, 8 % gyroid - the sims assume exactly this at 1.27 g/cm3 (3 walls / 15 % would add ~130 g to the head and break the head-pitch and balance margins); slicer modifier (4 walls, 40 %) only on the M3 heat-set insert bosses / screw holes (~2 g); 240-250 C nozzle / 70-80 C bed, textured PEI (glue stick as release), part fan 30-50 % |
| v330_head_eye_bezel_L.stl | matte BLACK PLA | front ring face DOWN on the bed (spigot up) | none | 0.16 mm, 2 walls (0.8 mm), 8 % infill (the sims assume this), textured PEI for a matte front |
| v330_head_eye_bezel_R.stl | matte BLACK PLA | front ring face DOWN on the bed (spigot up) | none | 0.16 mm, 2 walls (0.8 mm), 8 % infill (the sims assume this), textured PEI for a matte front |
| v330_head_display_carrier_L.stl | black PLA | ring back face on the bed | none | 0.2 mm, 2 walls (0.8 mm), 8 % infill (the sims assume this); modifier 4 walls on the M3 screw holes |
| v330_head_display_carrier_R.stl | black PLA | ring back face on the bed | none | 0.2 mm, 2 walls (0.8 mm), 8 % infill (the sims assume this); modifier 4 walls on the M3 screw holes |
| v330_head_chin_collar_L.stl | wood brown PETG | as exported (collar flipped, flat top face on the bed) | none | brown PETG: 0.16 mm layers, 2 walls (0.8 mm) + 3 top / 3 bottom, 8 % gyroid - the sims assume exactly this at 1.27 g/cm3 (3 walls / 15 % would add ~130 g to the head and break the head-pitch and balance margins); slicer modifier (4 walls, 40 %) only on the M3 heat-set insert bosses / screw holes (~2 g); 240-250 C nozzle / 70-80 C bed, textured PEI (glue stick as release), part fan 30-50 % |
| v330_head_chin_collar_R.stl | wood brown PETG | as exported (collar flipped, flat top face on the bed) | none | brown PETG: 0.16 mm layers, 2 walls (0.8 mm) + 3 top / 3 bottom, 8 % gyroid - the sims assume exactly this at 1.27 g/cm3 (3 walls / 15 % would add ~130 g to the head and break the head-pitch and balance margins); slicer modifier (4 walls, 40 %) only on the M3 heat-set insert bosses / screw holes (~2 g); 240-250 C nozzle / 70-80 C bed, textured PEI (glue stick as release), part fan 30-50 % |
| v330_head_head_yaw_to_roll.stl | PLA+ / PETG (structural, hidden) | as exported (= v39_head_yaw_to_roll print orientation: yaw ring face on the bed) | supports from the build plate under the new rear frame (cross-bar / side arms 6.75 mm above the bed) and under the roll hub | 0.2 mm, 4 walls, 40 % infill (as the ODM guide for the neck parts) |

## Mesh gate (every STL re-loaded from disk: open edges / non-manifold edges / bodies / volume)

| part | open edges | non-manifold edges | bodies | watertight | volume cm3 | faces |
|---|---|---|---|---|---|---|
| wig | 0 | 0 | 1 | True | 721.02 | 56390 |
| snout | 0 | 0 | 1 | True | 185.29 | 40246 |
| head_upper | 0 | 0 | 1 | True | 137.52 | 311722 |
| head_lower | 0 | 0 | 1 | True | 233.31 | 400612 |
| eye_bezel_L | 0 | 0 | 1 | True | 5.36 | 3072 |
| display_carrier_L | 0 | 0 | 1 | True | 14.28 | 4292 |
| eye_bezel_R | 0 | 0 | 1 | True | 5.36 | 3072 |
| display_carrier_R | 0 | 0 | 1 | True | 14.34 | 4246 |
| chin_collar_L | 0 | 0 | 1 | True | 4.23 | 10220 |
| chin_collar_R | 0 | 0 | 1 | True | 4.23 | 9984 |
| head_yaw_to_roll | 0 | 0 | 1 | True | 23.63 | 7010 |

## Snout (v3.30) - wood brown PETG
- v3.30 re-aim: yaw -4 / pitch +22 deg (v3.29 -12 / -6): mouth raised to the photos; modelled in Blender 4.5 (3 mm root fillet, wood-grain grooves); same keyed spigot into the unchanged head_lower socket. Orientation: as exported: mouth face DOWN on the bed (flat rim annulus), spigot + key tab up. Supports: none needed (the root plug / spigot are bridged by the cone). Settings: brown PETG (240-250 C, bed 70-80 C): 0.2 mm layers (0.16 mm makes the grain pop), 2 walls (0.8 mm), 8 % gyroid - the sims assume 8 %. ~54 g, ~3.7 h.
- Fit: dry-fit so the key tab sits in the head_lower key slot and the root lies flush on the ball, then glue (CA or epoxy). The root top is trimmed inside the head-split lift cylinder, so head_upper still lifts straight off with the snout glued in.

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 56 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~51 g of tree support, ~14.8 h (P1S standard).
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 4.5 % LIGHTNING - REQUIRED: the sims assume this wig at 4.5 % (simC/sweepR2.txt (v3.31 rev C body, head-range redesign incl. 25 g rear ballast, PETG head shells): margin 33.5 / 33.5 / 33.3 / 33.1 / 32.1 mm at 0 / 2 / 3 / 4.5 / 6 % wig infill; 4.5 % stays the required value (>= 32 mm everywhere, head-pitch hold 2.10x at 4.5 %).), so print exactly that. Sharp lock points: 5 mm brim, 'thick bridges' off.
- File size: the wig STL is the Blender-decimated mesh (blender/decimate_v330.py, COLLAPSE) of the simulated wig, re-gated closed/manifold; 564k -> 56k faces (ratio 0.10), surface deviation p99 0.02 mm / max 0.06 mm, volume 721.06 -> 721.02 cm3.
- Shape (v3.30, MODELLED IN BLENDER - smooth sleek locks): every lock is a Bezier spine (v3.29 lock layout) lofted with a smooth rounded section on a 2 mm side wall, Catmull-Clark subdivided, all locks unioned by a 0.7 mm voxel remesh and Taubin-smoothed in Blender (blender/build_wig_v330.py, wig_v330.blend) -> clean continuous lock outlines (no stair-stepped / serrated edges, no felt grooves, no V-notches), locks blend into each other with soft partings; central fringe triangle, soft sideburns and temple flicks kept. Seat / crown / hat band / pins / key unchanged (procedural, hair_v330.wig_blend).
- Felt hat (NOT printed - your fabric hat): pull it on so its edge sits in the recessed band all the way round (front edge just above the fringe roots, down over the left ear, tail flopping to the robot's left). The green hat in the renders is a render proxy of that fabric hat.
- No fly-away blades any more (v3.30): the lower side-lock ends still overhang - let the slicer's tree supports (auto) reach them. Handle the printed wig by the crown.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 5 mm into the 4 blind holes (5 mm deep, v3.30; was 6.5) in the wig; the 7 mm ends drop into the 4 vertical 3.2 mm holes (7.5 mm deep) in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.333/0.45 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


