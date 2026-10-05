# Twiglet head v3.6 - print sheet (210 mm ball)

Printer: Bambu P1S, 0.4 mm nozzle, textured or smooth PEI. The STLs are already in print orientation (flat on z=0, centred). Load and slice as-is.

| Part | Qty | Colour / material | Orientation (as exported) | Supports | Settings | Size mm | Est. g (+support) | Est. h |
|---|---|---|---|---|---|---|---|---|
| v36_head_head_upper.stl | 1 | wood brown PLA | split-plane rim down (dome up) | tree supports INSIDE only, for the crown above ~60 deg (hidden under the hat) | 0.2 mm, 3 walls, 15 % gyroid | 208 x 208 x 90 | 152 (+15) | 10.5 |
| v36_head_head_lower.stl | 1 | wood brown PLA | deck (split plane) down, neck opening up | tree supports 'build plate only' under the snout collar, bearing-holder pocket and the display-post undersides | 0.2 mm, 3 walls, 15 % gyroid | 209 x 210 x 95 | 245 (+29) | 17.1 |
| v36_head_snout.stl | 1 | wood brown PLA | mouth (flat lip face) down, spigot up | none | 0.2 mm, 3 walls, 15 % gyroid | 75 x 75 x 88 | 57 (+0) | 3.5 |
| v36_head_fringe_split_a.stl | 1 | yellow / blond PLA | forehead up, concave underside down | tree supports under the overhanging curls | 0.2 mm, 3 walls, 15 % gyroid | 114 x 156 x 148 | 60 (+12) | 4.5 |
| v36_head_fringe_split_b.stl | 1 | yellow / blond PLA | forehead up, concave underside down | tree supports under the overhanging curls | 0.2 mm, 3 walls, 15 % gyroid | 133 x 156 x 148 | 54 (+11) | 4.1 |
| v36_head_chin_collar_L.stl | 1 | black PLA | top (joint) face down | none | 0.2 mm, 3 walls, 15 % gyroid | 178 x 89 x 14 | 13 (+0) | 0.8 |
| v36_head_chin_collar_R.stl | 1 | black PLA | top (joint) face down | none | 0.2 mm, 3 walls, 15 % gyroid | 178 x 89 x 14 | 13 (+0) | 0.8 |
| v36_head_eye_bezel_L.stl | 1 | matte black PLA | flat visible face down (smooth PEI side) | none | 0.12-0.16 mm, 3 walls, 100 % | 83 x 83 x 7 | 6 (+0) | 0.7 |
| v36_head_eye_bezel_R.stl | 1 | matte black PLA | flat visible face down (smooth PEI side) | none | 0.12-0.16 mm, 3 walls, 100 % | 83 x 83 x 7 | 6 (+0) | 0.7 |
| v36_head_display_carrier_L.stl | 1 | PETG (or PLA), black | ring front face (display side) down, foot plate up | tree supports under the foot plate | 0.2 mm, 4 walls, 40 % | 71 x 71 x 25 | 16 (+1) | 1.1 |
| v36_head_display_carrier_R.stl | 1 | PETG (or PLA), black | ring front face (display side) down, foot plate up | tree supports under the foot plate | 0.2 mm, 4 walls, 40 % | 71 x 71 x 25 | 16 (+1) | 1.1 |

**Total: ~707 g filament incl. supports, ~45 h printing** (rough estimate from volume/area; the slicer figure wins).

Fringe: the 210 mm head's fringe is ~296 mm wide, over the 256 mm bed, so it is printed as `v36_head_fringe_split_a/b.stl`. Print each half cut face down, then glue them with two 3 mm alignment pins (3 mm rod or doubled 1.75 mm filament).

Hardware (unchanged from head-v3): 2 x Waveshare ESP32-S3-Touch-LCD-2.1 displays on the display carriers (M2 screws). Carriers bolt to 2 M3 posts per eye in head_lower (M3 heat-set inserts in the post tops). The ODM head_roll_mount bolts to the head_lower deck, Pi Zero 2W on the deck bosses. Dome to deck: M3 screws into the deck columns.

What changed from head-v3 (170 mm): outer shells, snout, fringe, collars and bezels are scaled x1.2353 (210 mm ball) about the chin line. The deck (roll-mount holes, Pi Zero and eye-driver bosses, dome columns) is kept 1:1 and bridged to the bigger wall. The display carriers are 1:1 and move out with the scaled eye onto re-made M3 posts. The roll-mount interface to the neck is unchanged.

The felt hat (not printed) should be scaled up ~24 % vs head-v3 (about 17 % vs the v3.3 180 mm head) to match, and kept tall and pointed like the photo.
