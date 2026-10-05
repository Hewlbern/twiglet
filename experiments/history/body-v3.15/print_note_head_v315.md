# Twiglet head v3.15 - print note (ONE-PIECE chunky wig with a smooth crown + photo-matched eye facets and ring bezels)

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v315_head_wig.stl | 184.9 x 242.5 x 229.2 | yes | 199 (+32) | 14.4 | 156.4 |
| v315_head_head_upper.stl | 207.9 x 207.9 x 90.3 | yes | 136 (+14) | 9.4 | 197.6 |
| v315_head_head_lower.stl | 209.0 x 210.0 x 95.1 | yes | 193 (+19) | 13.2 | 337.5 |
| v315_head_eye_bezel_L.stl | 74.4 x 74.4 x 6.2 | yes | 6 (+1) | 0.4 | 0.5 |
| v315_head_eye_bezel_R.stl | 74.4 x 74.4 x 6.1 | yes | 6 (+1) | 0.4 | 0.4 |

## Reprint list (vs v3.14)
- REPRINT: wig (one piece), head_upper, head_lower, eye_bezel_L, eye_bezel_R.
- KEEP (unchanged): snout, chin_collar_L/R, display_carrier_L/R (+ screens), neck/body, felt hat.

## Wig - one piece, yellow / blond matte PLA (PETG ~10 C hotter)
- Orientation: as exported: crown axis tilted 48 deg from straight-down (least support volume of 6120 orientations searched); lies on the dome + clump backs. Supports: tree supports (auto, build plate only, threshold 40 deg, 0.2 mm top Z gap) + 5 mm brim. Estimated support ~32 g (tree), print ~14.4 h at P1S standard speed. (Straight crown-down would need ~55 g of support / 244.3 cm2 of overhang - worse.)
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 5 % LIGHTNING (clumps + crown dome print as sealed hollow shells), 0.4 mm nozzle. The sim mass assumes 2 walls + 8 % infill (heavier than lightning), so the real wig is a few grams lighter than the 198.9 g used for the head-pitch check.
- Pointed tips: 'thick bridges' off, 5 mm brim. Remove the tree supports from the clump undersides with flush cutters; the crown dome is smooth (no seam, no grooves, no bosses) and sits under the felt hat.
- Fit: pin 3 x 3 mm rods (12 mm long; 6 mm glued into the 3 BLIND holes inside the crown dome, 6 mm protruding) into the 3 matching 3.2 mm holes in head_upper; the wig seats with a 0.3 mm gap (seat gap p5/p50/p95 = 0.333/0.438/0.908 mm; p95 over the wood-grain grooves). Glue optional.
- The 3 pin holes are already printed in the new head_upper (the wig seat is fitted to the v3.15 shells, so print wig + shells together).
- Felt look: 0.25 mm surface ripple on the clumps (prints fine at 0.2 mm); optional ochre dry-brush in the V-grooves.

## head_upper + head_lower (wood brown)
- 0.16 mm layers (grain + facet edges read better; 0.2 mm OK), 3 walls, 15 % gyroid; rim down, tree supports inside only. New: flat eye facets, 36.3 mm bores, grain rings re-engraved around each eye; walls >= 1.25 mm everywhere (>= 2.1 mm on the facets).
- Assembly: display carriers + screens mount exactly as before (same internal bosses); push the new bezel spigot into the bore from the front (snug; a drop of CA or E6000 to fix).

## eye_bezel_L / eye_bezel_R (matte black)
- 0.16 mm, 3 walls, 30 % infill, ring face down on textured PEI (matte front), no supports. L and R are mirror-specific (marked by the file name).

