# Twiglet head v3.29 - print note (photo-matched one-piece wig; attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v329_head_wig.stl | 223.3 x 243.1 x 248.4 | yes | 197 (+64) | 16.3 | 187.5 |

## Reprint list (vs v3.28)
- REPRINT: the wig only (one piece). Same 4 pins / keyed tongue / glue land as v3.16-v3.28 (head_upper identical), so it fits the v3.16 head_upper as printed.
- KEEP (unchanged since v3.16): head_upper, head_lower, eye_bezel_L/R, snout, chin_collar_L/R, display_carrier_L/R (+ screens), felt hat. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 51 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~64 g of tree support, ~16.3 h (P1S standard).
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 4.5 % LIGHTNING - REQUIRED: the sims assume this wig at 4.5 % (head+arm margin 33.0 mm; 4 % 29.9, 5 % 22.0, 5.5 % 30.3, 6 % 32.9, 3 % 33.1 - see sim/sweep329.txt), so print 4.5 % (v3.28 was 5.5 %). Sharp lock points: 5 mm brim, 'thick bridges' off.
- Shape (v3.29, SOFT ROUNDED SIDE HAIR + PHOTO FRINGE + HAT SEAT): central flat-faceted triangle strand (centre ridge, point between the eyes) and its two pointed neighbour strands kept from v3.27/v3.28; ALL side hair (front side locks over the outer eye corners, side locks, temple layers, cheek locks, back locks) now has fully rounded felt-clump sections and blunt domed ends (taper stops at 0.2-0.22 x root width, then a round end cap) - no points; the two fly-away blades are gone, replaced by two soft temple flick locks that hug the head (robot's right one is the big flick in the photos); soft rounded sideburns, 4 felt strand grooves per lock and the layered temple/cheek locks kept from v3.28. HAT SEAT (unchanged): under the felt hat the wig is a smooth 8 mm crown with no locks, and just outside the hat edge there is a 4.5 mm-deep, ~4 mm-wide recessed band before the locks rise, so the fabric hat's edge sits on a clean shadow step all the way round. Min lip 1.65 mm radial.
- Felt hat (NOT printed - your fabric hat): pull it on so its edge sits in the recessed band all the way round (front edge just above the fringe roots, down over the left ear, tail flopping to the robot's left). The green hat in the renders is a render proxy of that fabric hat.
- No fly-away blades any more (v3.29): the lower side-lock ends still overhang - let the slicer's tree supports (auto) reach them. Handle the printed wig by the crown.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 5 mm into the 4 blind holes (5 mm deep, v3.29; was 6.5) in the wig; the 7 mm ends drop into the 4 vertical 3.2 mm holes (7.5 mm deep) in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.332/0.447 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


