# Twiglet head v3.3 - print sheet (180 mm ball)

Printer: Bambu P1S, 0.4 mm nozzle, textured or smooth PEI. The STLs are already in print orientation (flat on z=0, centred). Load and slice as-is.

| Part | Qty | Colour / material | Orientation (as exported) | Supports | Settings | Size mm | Est. g (+support) | Est. h |
|---|---|---|---|---|---|---|---|---|
| v33_head_head_upper.stl | 1 | wood brown PLA | split-plane rim down (dome up) | tree supports INSIDE only, for the crown above ~60 deg (hidden under the hat) | 0.2 mm, 3 walls, 15 % gyroid | 178 x 178 x 81 | 100 (+10) | 6.9 |
| v33_head_head_lower.stl | 1 | wood brown PLA | deck (split plane) down, neck opening up | tree supports 'build plate only' under the snout collar, bearing-holder pocket and the display-post undersides | 0.2 mm, 3 walls, 15 % gyroid | 179 x 180 x 76 | 164 (+20) | 11.5 |
| v33_head_snout.stl | 1 | wood brown PLA | mouth (flat lip face) down, spigot up | none | 0.2 mm, 3 walls, 15 % gyroid | 65 x 65 x 75 | 40 (+0) | 2.5 |
| v33_head_fringe.stl | 1 | yellow / blond PLA | forehead up, concave underside down | tree supports under the concave underside and curled tips | 0.2 mm, 3 walls, 15 % gyroid | 114 x 254 x 137 | 79 (+16) | 5.9 |
| v33_head_chin_collar_L.stl | 1 | black PLA | top (joint) face down | none | 0.2 mm, 3 walls, 15 % gyroid | 153 x 76 x 12 | 8 (+0) | 0.5 |
| v33_head_chin_collar_R.stl | 1 | black PLA | top (joint) face down | none | 0.2 mm, 3 walls, 15 % gyroid | 153 x 76 x 12 | 8 (+0) | 0.5 |
| v33_head_eye_bezel_L.stl | 1 | matte black PLA | flat visible face down (smooth PEI side) | none | 0.12-0.16 mm, 3 walls, 100 % | 71 x 71 x 6 | 4 (+0) | 0.5 |
| v33_head_eye_bezel_R.stl | 1 | matte black PLA | flat visible face down (smooth PEI side) | none | 0.12-0.16 mm, 3 walls, 100 % | 71 x 71 x 6 | 4 (+0) | 0.5 |
| v33_head_display_carrier_L.stl | 1 | PETG (or PLA), black | ring front face (display side) down, foot plate up | tree supports under the foot plate | 0.2 mm, 4 walls, 40 % | 71 x 71 x 25 | 16 (+1) | 1.1 |
| v33_head_display_carrier_R.stl | 1 | PETG (or PLA), black | ring front face (display side) down, foot plate up | tree supports under the foot plate | 0.2 mm, 4 walls, 40 % | 71 x 71 x 25 | 16 (+1) | 1.1 |

**Total: ~487 g filament incl. supports, ~31 h printing** (rough estimate from volume/area; the slicer figure wins).

Optional: `v33_head_fringe_split_a/b.stl`. The 1-piece fringe is 254 mm long, which fits the 256 mm bed with ~1 mm spare. If the slicer complains, print the 2 halves (cut face down) and glue them with two 3 mm alignment pins.

Hardware (unchanged from head-v3): 2 x Waveshare ESP32-S3-Touch-LCD-2.1 displays on the display carriers (M2 screws). Carriers bolt to 2 M3 posts per eye in head_lower (M3 heat-set inserts in the post tops). The ODM head_roll_mount bolts to the head_lower deck, Pi Zero 2W on the deck bosses. Dome to deck: M3 screws into the deck columns.

What changed from head-v3 (170 mm): outer shells, snout, fringe, collars and bezels scaled x1.0588 about the chin line. The deck (roll-mount holes, Pi and board bosses, dome columns) is kept 1:1 and bridged to the bigger wall. The display posts are re-made under the displays' new position (the eyes moved out ~1-2 mm and up ~4.8 mm with the bigger face). The pod lift-out clearances are re-cut. The chin collars get 0.3 mm clearance to the 1:1 deck.

The felt hat (not printed) should be scaled up ~6 % to match, and made taller than the model's to match the photo's tall pointed hat.
