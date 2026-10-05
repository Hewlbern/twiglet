# Twiglet head v3.9 - print sheet (210 mm ball, wood grain, chunky fringe, snout with a clean root, wood chin collars)

Printer: Bambu P1S, 0.4 mm nozzle, textured or smooth PEI. The STLs are already in print orientation (flat on z=0, centred). Load and slice as-is.

| Part | Qty | Colour / material | Orientation (as exported) | Supports | Settings | Size mm | Est. g (+support) | Est. h |
|---|---|---|---|---|---|---|---|---|
| v39_head_head_upper.stl | 1 | wood brown PLA (wood-fill optional) | split-plane rim down (dome up) | tree supports INSIDE only, for the crown above ~60 deg (hidden under the hat); the grain grooves need none | 0.2 mm (0.16 mm shows the grain better), 3 walls, 15 % gyroid | 208 x 208 x 90 | 149 (+15) | 10.3 |
| v39_head_head_lower.stl | 1 | wood brown PLA (wood-fill optional) | deck (split plane) down, neck opening up | tree supports 'build plate only' under the snout collar, bearing-holder pocket and the display-post undersides | 0.2 mm, 3 walls, 15 % gyroid | 209 x 210 x 95 | 245 (+29) | 17.2 |
| v39_head_snout.stl | 1 | wood brown PLA (wood-fill optional) | mouth (flat lip face) down, spigot up | none | 0.2 mm, 3 walls, 15 % gyroid | 72 x 72 x 93 | 78 (+0) | 4.9 |
| v39_head_fringe.stl | 1 | yellow / blond PLA (matte) | as exported: tipped ~80 deg onto its back edge (least-overhang orientation found by search), locks rising | tree supports (build plate only) + brim; about 25 cm2 of >45 deg overhang, mainly under the lowest lock edges | 0.2 mm, 3 walls, 10 % gyroid | 227 x 198 x 181 | 138 (+25) | 10.2 |
| v39_head_chin_collar_L.stl | 1 | wood brown PLA (v3.9: was black) | top (joint) face down | none | 0.2 mm, 3 walls, 15 % gyroid | 178 x 89 x 14 | 13 (+0) | 0.8 |
| v39_head_chin_collar_R.stl | 1 | wood brown PLA (v3.9: was black) | top (joint) face down | none | 0.2 mm, 3 walls, 15 % gyroid | 178 x 89 x 14 | 13 (+0) | 0.8 |
| v39_head_eye_bezel_L.stl | 1 | matte black PLA | flat visible face down (smooth PEI side) | none | 0.12-0.16 mm, 3 walls, 100 % | 83 x 83 x 7 | 6 (+0) | 0.7 |
| v39_head_eye_bezel_R.stl | 1 | matte black PLA | flat visible face down (smooth PEI side) | none | 0.12-0.16 mm, 3 walls, 100 % | 83 x 83 x 7 | 6 (+0) | 0.7 |
| v39_head_display_carrier_L.stl | 1 | PETG (or PLA), black | ring front face (display side) down, foot plate up | tree supports under the foot plate | 0.2 mm, 4 walls, 40 % | 71 x 71 x 25 | 16 (+1) | 1.1 |
| v39_head_display_carrier_R.stl | 1 | PETG (or PLA), black | ring front face (display side) down, foot plate up | tree supports under the foot plate | 0.2 mm, 4 walls, 40 % | 71 x 71 x 25 | 16 (+1) | 1.1 |
| (alternative) v39_head_fringe_split_a.stl | 1 | yellow / blond PLA (matte) | as exported (least-overhang orientation) | tree supports (build plate only) under the lowest lock edges | 0.2 mm, 3 walls, 10 % gyroid | 183 x 92 x 185 | 71 (+13) | 5.2 |
| (alternative) v39_head_fringe_split_b.stl | 1 | yellow / blond PLA (matte) | as exported (least-overhang orientation) | tree supports (build plate only) under the lowest lock edges | 0.2 mm, 3 walls, 10 % gyroid | 135 x 157 x 192 | 71 (+13) | 5.2 |

**Total: ~751 g filament incl. supports, ~48 h printing** (rough estimate from volume/area; the slicer figure wins).

Fringe (new in v3.7): 11 broad, flat, felt-like locks (38-42 mm wide, ~7 mm thick, pointed tips) on a crown cap that sits under the felt hat. Use the one-piece fringe if listed in the table (it fits the P1S); the split halves (fewer supports; glued with two 3 mm alignment pins) are identical to v3.8's and ship in twiglet-head-v3.8-stl.zip (left out of this zip to stay under 20 MB). Glue the fringe to head_upper (under the hat) with CA or hot glue. The locks cover only the top rim of each screen (about 4 % of the visible circle; v3.6: 0 %).

Wood grain (new in v3.7): vertical plank-like striations, faint horizontal ring banding (as in the reference photos) and concentric rings around the eye sockets, engraved up to 0.55 mm and locally shallower so every wall stays at least 1.25 mm (measured minimum after grain: head_upper 1.4, head_lower 1.4, snout 1.41 mm). Mounts and inner faces are untouched. Tip: 0.16 mm layers and wood-fill PLA, or a dark wash wiped off, make the grain pop.

Hardware (unchanged from head-v3): 2 x Waveshare ESP32-S3-Touch-LCD-2.1 displays on the display carriers (M2 screws). Carriers bolt to 2 M3 posts per eye in head_lower (M3 heat-set inserts in the post tops). The ODM head_roll_mount bolts to the head_lower deck, Pi Zero 2W on the deck bosses. Dome to deck: M3 screws into the deck columns.

Changed vs v3.8 (REPRINT): (1) snout - the flared root ring is gone: the straight tube (OD 68, lip OD 72, bore 45, 72 mm from the face) meets the ball with a 3 mm blend fillet only, trimmed to the ball so it sits flush all round; axis 12 deg to the robot's right, 6 deg down (v3.8: 16 / 11); same keyed spigot + tab into the unchanged head_lower socket (glue); no internal void (8-15 % infill does the job). (2) chin_collar_L/R - same shape, now wood-grain textured and printed in WOOD BROWN (was black) so the ball reads down to the neck opening like the photos. Unchanged vs v3.8 (reuse): head_upper, head_lower, fringe, eye bezels, display carriers.

What changed from head-v3 (170 mm): outer shells, snout, fringe, collars and bezels are scaled x1.2353 (210 mm ball) about the chin line. The deck (roll-mount holes, Pi Zero and eye-driver bosses, dome columns) is kept 1:1 and bridged to the bigger wall. The display carriers are 1:1 and move out with the scaled eye onto re-made M3 posts. The roll-mount interface to the neck is unchanged.

The felt hat (not printed) should be scaled up ~24 % vs head-v3 (about 17 % vs the v3.3 180 mm head) to match, and kept tall and pointed like the photo.
