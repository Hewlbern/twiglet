# Twiglet hair v3.13 - print note (photo-matched fringe; only the fringe changed vs v3.12)

Material: yellow / blond PLA (matte) - PETG also fine (print ~10 C hotter, slower first layer). Settings: 0.2 mm layers, 2 walls (0.8 mm), 8 % gyroid, 4 top / 3 bottom layers, 0.4 mm nozzle. The sim mass assumes exactly 2 walls + 8 % infill; heavier settings eat into the head-pitch margin (each +10 g of fringe at the front locks ~ +0.008 N m; the v3.13 margin is 0.245 - 0.237 = 0.008 N m).

| file | size (mm) | fits P1S | est. g (+support) | h | >45 deg overhang cm2 |
|---|---|---|---|---|---|
| v313_head_fringe.stl | 243.7 x 223.9 x 187.5 | yes | 121 (+22) | 8.9 | 30.5 |
| v313_head_fringe_split_a.stl | 221.8 x 109.5 x 162.3 | yes | 63 (+11) | 4.6 | 7.5 |
| v313_head_fringe_split_b.stl | 91.9 x 217.2 x 163.2 | yes | 59 (+11) | 4.4 | 7.4 |

One piece: fits the 256 mm bed in the searched orientation - print as exported. Split option (recommended - fewer supports, safer on the bed edge): print v313_head_fringe_split_a/_b as exported, tree supports (build plate only) under the lowest lock edges, brim 5 mm. Push 3 mm rod (or 2 x 1.75 mm filament) into the pin holes, glue the mid-plane with CA, then glue the fringe to head_upper under the hat (CA or hot glue on the band ring; there are no pins/sockets for the fringe on the head - same as v3.7-v3.12).

Supports: tree (auto), build plate only, threshold 40 deg; interface 0.2 mm gap. The lock tips are pointed - use 'thick bridges' off and a 3 mm brim so the thin tips do not lift.

Post-process: optional light sanding + a dry-brush of darker yellow/ochre along the lock ridges for the felt look in the photos.
