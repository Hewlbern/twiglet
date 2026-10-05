# Twiglet head v3.25 - print note (photo-matched one-piece wig; attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v325_head_wig.stl | 246.2 x 247.5 x 248.1 | yes | 188 (+71) | 16.2 | 180.6 |

## Reprint list (vs v3.24)
- REPRINT: the wig only (one piece). Same 4 pins / keyed tongue / glue land as v3.16-v3.24 (head_upper identical), so it fits the v3.16 head_upper as printed.
- KEEP (unchanged since v3.16): head_upper, head_lower, eye_bezel_L/R, snout, chin_collar_L/R, display_carrier_L/R (+ screens), felt hat. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 55 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~71 g of tree support, ~16.2 h (P1S standard).
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 3 % LIGHTNING - REQUIRED: the sims assume this wig at 3 % (head+arm margin 32.4 mm; 2.5 % 32.6, 2 % 31.2, 3.5 % 29.8, 4 % 29.7 - see sim/sweep325b.txt), so print 3 % (not the v3.24 2 %). Sharp lock points: 5 mm brim, 'thick bridges' off.
- Shape (v3.25, WISPY FELT CLUMPS, CLEARER GAPS, PHOTO SIDEBURNS): the v3.24 flowing wig (S-curved locks, fly-aways) with softer clumps: lock section 50 % rounded (superellipse) / 50 % faceted, no sawtooth forked tips, soft tapered ends (end width 0.12 x root, taper exp 0.7), blunt fly-away ends with a 2 mm edge lip; clearly separated locks: bases 18 % narrower + a 5 mm V-gap carved along every lock-to-lock seam (not under the fly-away blades). SIDEBURNS re-done from the photos: one long soft-tapered lock per side hanging beside the ear (phi +-73, was +-60 in front of it), 20 mm root, down to th 108 (robot's left) / 106 (right), standing off the cheek below eye level. Crest heights x0.95, over-eye fringe lock F2 shorter. Min lip 1.65 mm radial. Hollow: 2 walls + 3 % lightning.

- Fly-aways: they are cantilevers (drooping) - let the slicer's tree supports (auto) reach them; they are solid-ish (lightning barely fills them). Handle the printed wig by the crown, not by the fly-aways.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 6 mm into the 4 blind holes in the wig; the 6 mm ends drop into the 4 vertical 3.2 mm holes in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.336/0.445 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


