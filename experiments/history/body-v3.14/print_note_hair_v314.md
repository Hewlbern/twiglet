# Twiglet hair v3.14 - print note (fitted clumpy wig; only the hair changed vs v3.13, plus 3 pin holes in head_upper)

## Parts
| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v314_head_wig.stl | 226.1 x 200.7 x 218.6 | yes | 167 (+30) | 12.3 | 144.7 |
| v314_head_wig_split_a.stl | 129.3 x 222.7 x 183.1 | yes | 88 (+16) | 6.5 | 6.3 |
| v314_head_wig_split_b.stl | 129.6 x 220.5 x 182.8 | yes | 83 (+15) | 6.1 | 6.7 |
| v314_head_head_upper.stl | 207.9 x 207.9 x 90.3 | yes | 134 (+13) | 9.2 | 195.3 |

## Wig (yellow / blond matte PLA, or PETG ~10 C hotter)
- Settings: 0.2 mm layers, 2 walls (0.8 mm), 3 top / 3 bottom layers, sparse infill 5 % LIGHTNING (supports only the top skins -> the clumps print as sealed hollow shells), 0.4 mm nozzle. The sim mass assumes 2 walls + 8 % infill (heavier than lightning), so the real wig is a few grams lighter than the 166.9 g used in the head-pitch check.
- One piece fits the 256 mm bed in the searched orientation, but the split halves are recommended (less support, flatter on the bed). Split: print v314_head_wig_split_a/_b as exported, tree supports (build plate only, 40 deg threshold, 0.2 mm interface gap), 5 mm brim. Pointed tips: keep 'thick bridges' off; 3-5 mm brim so they do not lift.
- Assembly: push 3 mm rod (or 2 x 1.75 mm filament) into the 2 mid-plane pin holes, CA the halves together. Then fit 3 x 3 mm pins (12 mm long) into the three crown pin bosses; they drop into the 3 matching holes in head_upper and register the wig repeatably. The wig then sits on the head with a 0.3 mm seat clearance (measured seat gap p5/p50/p95 = 0.333/0.444/1.115 mm; the p95 is over the wood-grain grooves). Glue optional (a few dots of hot glue or Blu-Tack on the crown cap) - the pins + the hat hold it.
- Felt look: the clumps carry a 0.25 mm surface ripple (prints fine at 0.2 mm). Optional: dry-brush ochre into the V-grooves.

## head_upper (REPRINT only if you want printed holes)
- Same as v3.13 plus 3 x 3.2 mm through-holes at the crown (under the hat). Settings as before: wood brown PLA, 0.2 mm, 3 walls, 15 % gyroid, rim down, tree supports inside only.
- No reprint: seat the wig (the crown cap and the cut-outs around the eye bezels centre it roughly), then drill 3.2 mm through each pin boss into the shell (2.6 mm wall, nothing behind it at those spots) and fit the pins.

