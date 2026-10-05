# Twiglet head v3.23 - fly-aways + sideburns (wig only; head_upper identical to v3.22)

## Photo findings (zoomed crops: measure323/z_*.png, z_all.png)
- Fly-away: temple flare just under the hat brim at eye-top level (~45 mm above eye centres); lifts clear off the head and flicks OUT (about horizontal, slightly up/back) as a broad triangular blade. Biggest on the robot's right (image-left in original/front), ~65 mm beyond the ball; shorter one on the robot's left.
- Sideburns: long narrow triangles hanging straight down in front of the ear beside the eye to snout/jaw level, standing off the ball, tip flicking out. Both sides.

## Changes (hair_v323.py)
- Sideburn locks (LOCKS 13/14): (+-60, 34, 108, 24, 17.0, +-3, -+0.1, 0.34, 0, 0).
- FLYAWAY: R th55 ph-86 L70 W38 T20; L th58 ph88 L52 W32 T17 (up 0.08/0.04, back 0.20). Lofted pentagonal blade on a Bezier, root buried in the S1 crest, root flare 1+0.6exp(-t/0.15), 1.4 mm edge lip, FLY_BOSS gaussian boss (A 18, SIG 7) fillet. Root section at the wig surface ~10x29 mm (R) / 8x23 mm (L); >=4 mm out to r~145/135 mm, only the last 10-15 mm is tip.
- v3.22 locks, broad chunky triangles and diagonal sweep kept unchanged.

## Silhouette (measure319/iou_v323.json)
| view | v3.21 | v3.22 | v3.23 IoU | v3.23 outline outside hat (mm) (v3.22) |
|---|---|---|---|---|
| original | see v3.22 README | 0.399 | 0.387 | 12.5 (14.9) |
| front | | 0.459 | 0.442 | 9.2 (11.1) |
| 3/4 | | 0.510 | 0.495 | 10.4 (12.5) |
The IoU dips slightly (the thin sideburns/blades add area that is not perfectly aligned); the outline error is clearly better.

## Checks
eye coverage 0/0; overlaps 0; bezel gap 2.94 mm; watertight; head-range contacts 7/315 (trunk); arm sweep 0/11/9; walls min 1.20 mm (p1 2.4, median 12.1); 249.6x249.4x224.1 mm fits P1S; ~181 g + 76 g tree support, ~16.1 h.

## Infill sweep (sim/sweep323.txt; head+arm margin mm)
0% 30.5 | 1% 32.9 | 2% 23.8 (repeat identical) | 3% 21.5 | 4% 33.2 | 5% 30.4 | 6% 30.4.
Deterministic run-to-run (fixed seed; repeat gives identical numbers) but very sensitive to small mass changes: 21.5-33.2 mm spread across 0-6%. Chosen: 4% lightning (33.2 mm).

## Sims (4%, final geometry; sim/compare_v322_v323.md)
mass 2.568 kg; head pitch 0.202 N·m standing (2.43x vs 0.49); head+arm margin 33.2 mm (v3.22 33.0); walk max-speed 100% / 0.195 m/s; energy-aware 95% -> re-refined (REFINE_SEED 33) 100% / 0.162 m/s.
