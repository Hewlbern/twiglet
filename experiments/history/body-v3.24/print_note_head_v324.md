# Twiglet head v3.24 - print note (photo-matched one-piece wig; attachment unchanged from v3.16)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v324_head_wig.stl | 238.8 x 248.6 x 235.3 | yes | 169 (+47) | 13.5 | 177.7 |

## Reprint list (vs v3.23)
- REPRINT: the wig only (one piece). Same 4 pins / keyed tongue / glue land as v3.16-v3.23 (head_upper identical), so it fits the v3.16 head_upper as printed.
- KEEP (unchanged since v3.16): head_upper, head_lower, eye_bezel_L/R, snout, chin_collar_L/R, display_carrier_L/R (+ screens), felt hat. The kilt is a separate pack (twiglet-kilt-v3.16-stl.zip, unchanged).

## Wig - one piece, yellow / blond matte PLA
- Orientation: as exported: crown axis tilted 45 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. ~47 g of tree support, ~13.5 h (P1S standard).
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 2 % LIGHTNING (the locks print as near-hollow sealed shells; lightning only props the top skins) - the sims assume this wig at 2 %, keep 1-2 % (infill sweep on the final geometry: sim/sweep324.txt; 3 % and 6 % were clearly worse for the head+arm test). Sharp lock points: 5 mm brim, 'thick bridges' off.
- Shape (v3.24, FLOWING): the v3.23 wig (broad chunky triangular locks with hard crests + V notches, fly-aways, sideburns) with every lock re-laid on a longer continuous S-curve: S-wave x1.6 with one phase per side so neighbours flow together in streams, a gentle twist (crest drifts across the lock, x1.6), tips that trail/curl ~10 deg on in the sweep direction, and side locks that fall first then trail back diagonally into the fly-aways (theta bow 0.25; back 0.075). Fringe tips shortened (F1 -9 deg, F2-F5 -6 deg) and the over-eye locks curl out (+-12 deg) - fringe flows down and out; back locks varied lengths (103-112 deg). FLY-AWAYS: root lowered to the eye-top temple (th 63/62) and the blades droop out-and-down with the stream (robot's right 70 mm, left 52 mm; root section ~29 x 10 mm, >=4 mm except the last ~10 mm of the tip, boss fillet into the S1 lock). SIDEBURNS unchanged (phi +-60 to th 108). Hollow: 2 walls + 2 % lightning.

- Fly-aways: they are cantilevers (now drooping, so less support than v3.23: ~47 g vs 76 g) - let the slicer's tree supports (auto) reach them; they are solid-ish (lightning barely fills them). Handle the printed wig by the crown, not by the fly-aways.

## Attachment (the wig cannot rotate, slide or lift)
- Locate: 4 x 3 mm steel or PLA-filament rods, 12 mm long: glue 6 mm into the 4 blind holes in the wig; the 6 mm ends drop into the 4 vertical 3.2 mm holes in head_upper. All pins are vertical = parallel to the push-on direction (no binding).
- Key: a 2.4 mm wide x 1.1 mm tongue (4 arcs of 70/40/40/40 deg - the long arc at the front, so it only fits one way) on the wig underside sits in the matching 3.0 x 1.0 mm groove in head_upper (0.3 mm side / 0.2 mm bottom glue gap). Groove floor wall 1.47 mm.
- Glue land: the whole wig underside is a seat with a controlled 0.3 mm gap to the head (p5/p50 0.336/0.444 mm); the lower lock ends lift off the head (flare) and are not glued.
- Glue: 2-part epoxy (5-min or 30-min, e.g. Loctite/Araldite) - thin bead on the crown seat band + tongue + pin holes, push down, tape for 1 h. Medium CA also works but is brittle on impact; epoxy fills the 0.2-0.3 mm gap properly. For a removable wig: pins + tongue + 3 dots of E6000 / hot glue.


