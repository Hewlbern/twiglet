# Twiglet head v3.27 - print note (photo-matched one-piece wig; attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v327_head_wig.stl | 241.0 x 248.7 x 247.7 | yes | 188 (+53) | 15.1 | 168.6 |

## Reprint list (vs v3.26)
- REPRINT: the wig only (one piece). Same 4 pins / keyed tongue / glue land as v3.16-v3.26 (head_upper identical), so it fits the v3.16 head_upper as printed.
- KEEP (unchanged since v3.16): head_upper, head_lower, eye_bezel_L/R, snout, chin_collar_L/R, display_carrier_L/R (+ screens), felt hat. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 55 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~53 g of tree support, ~15.1 h (P1S standard).
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 4 % LIGHTNING - REQUIRED: the sims assume this wig at 4 % (head+arm margin 32.5 mm; 3 % 23.5, 6 % 31.3, 0 % 29.3, 2.5 % 24.0, 5 % 23.5 - see sim/sweep327.txt), so print 4 % (v3.26 was 3 %). Sharp lock points: 5 mm brim, 'thick bridges' off.
- Shape (v3.27, COHESIVE CLUMPS + PHOTO FRINGE + HAT SEAT): fewer, larger merged felt clumps (bases x0.9, 3 mm partings instead of 4 mm, fuller lock ends 0.14 x root width); CENTRAL STRAND traced from the photos = a straight-down, symmetric, flat-faceted triangle with a crisp centre ridge standing ~25 mm proud, its point between the eyes; the two NEIGHBOUR strands are narrower, flat-faceted and pointed, swept outward over the eye tops with a clear V parting from the central one (eye screens stay 100 % clear); front sides (F4/F5) ~11 mm lower and the side-lock arm relief starts 3 deg lower (sides ~5.5 mm lower); SIDEBURNS = soft rounded 26 mm strand bundles with 3 soft strand grooves and a wide rounded end (no spike). HAT SEAT (unchanged from v3.26): under the felt hat the wig is a smooth 8 mm crown with no locks, and just outside the hat edge there is a 4.5 mm-deep, ~4 mm-wide recessed band before the locks rise, so the fabric hat's edge sits on a clean shadow step all the way round. Min lip 1.65 mm radial.
- Felt hat (NOT printed - your fabric hat): pull it on so its edge sits in the recessed band all the way round (front edge just above the fringe roots, down over the left ear, tail flopping to the robot's left). The green hat in the renders is a render proxy of that fabric hat.
- Fly-aways: they are cantilevers (drooping) - let the slicer's tree supports (auto) reach them; they are solid-ish (lightning barely fills them). Handle the printed wig by the crown, not by the fly-aways.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 6 mm into the 4 blind holes in the wig; the 6 mm ends drop into the 4 vertical 3.2 mm holes in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.333/0.447 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


