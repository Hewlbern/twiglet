# Twiglet head v3.23 - print note (photo-matched one-piece wig; attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v323_head_wig.stl | 249.6 x 249.4 x 224.1 | yes | 181 (+76) | 16.1 | 200.6 |

## Reprint list (vs v3.22)
- REPRINT: the wig only (one piece). Same 4 pins / keyed tongue / glue land as v3.16-v3.22 (head_upper identical), so it fits the v3.16 head_upper as printed.
- KEEP (unchanged since v3.16): head_upper, head_lower, eye_bezel_L/R, snout, chin_collar_L/R, display_carrier_L/R (+ screens), felt hat. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 27 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~76 g of tree support, ~16.1 h (P1S standard).
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 4 % LIGHTNING (the locks print as near-hollow sealed shells; lightning only props the top skins) - the sims assume this wig at 4 %, keep 4 % (infill sweep: sim/sweep323.txt). Sharp lock points: 5 mm brim, 'thick bridges' off.
- Shape (v3.23): v3.22 (13 broad chunky triangular locks, mid-side locks brushed back across the head) PLUS (1) two FLY-AWAYS: lofted triangular blades that lift clear off the head at the temples just under the hat brim and flick OUT (slightly up/back) - robot's right 70 mm long, robot's left 52 mm; root section at the wig surface ~30 x 12 mm (>=4 mm everywhere except the last few mm of the tip), root buried in the S1 lock crest with a height-field boss fillet; and (2) two SIDEBURNS: narrow triangular locks hanging straight down in front of the ears beside the eyes (phi +-60, to th 108) with the tip flicking out. Hollow: 2 walls + 4 % lightning.

- Fly-aways: they are cantilevers - let the slicer's tree supports (auto) reach them; they are solid-ish (lightning barely fills them). Handle the printed wig by the crown, not by the fly-aways.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 6 mm into the 4 blind holes in the wig; the 6 mm ends drop into the 4 vertical 3.2 mm holes in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.335/0.445 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


