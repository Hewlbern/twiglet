# Twiglet head v3.22 - print note (photo-matched one-piece wig; attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v322_head_wig.stl | 236.2 x 206.0 x 207.8 | yes | 160 (+36) | 12.3 | 184.1 |

## Reprint list (vs v3.21)
- REPRINT: the wig only (one piece). Same 4 pins / keyed tongue / glue land as v3.16-v3.21 (head_upper identical), so it fits the v3.16 head_upper as printed.
- KEEP (unchanged since v3.16): head_upper, head_lower, eye_bezel_L/R, snout, chin_collar_L/R, display_carrier_L/R (+ screens), felt hat. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 19 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~36 g of tree support, ~12.3 h (P1S standard). (Straight crown-down: ~44 g support / 215.4 cm2 overhang - worse.)
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 2 % LIGHTNING (the locks print as near-hollow sealed shells; lightning only props the top skins) - the sims assume this wig at 2 %, keep 2 % (infill sweep: sim/sweep322.txt). Sharp lock points: 5 mm brim, 'thick bridges' off.
- Shape (v3.22): v3.21's deep triangular prisms (flat facets, hard crest ridge, V notches), made CHUNKIER and BROADER: 13 locks (the two narrow long side locks S2+S3 merged into one broad swept side wedge per side), full-width bases at the hat brim (th 38) instead of at the crown, bases x1.9 fringe / x1.25 outer fringe / x1.4 sides / x1.3 back, fuller wedges (facet exponent 0.85), crests x1.45 fringe / x1.3 sides; the mid-side locks brush ACROSS the head backward on a steady diagonal (S1 curl 56 deg, S23 curl 40 deg, outer fringe 32 deg, near-linear drift); sawtooth tips on the outer fringe + back; trims (ARM_CUT, TRUNK_CUT) unchanged. Hollow: 2 walls + 2 % lightning.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 6 mm into the 4 blind holes in the wig; the 6 mm ends drop into the 4 vertical 3.2 mm holes in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.336/0.444 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


