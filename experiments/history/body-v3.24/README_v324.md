# Twiglet head v3.24 - flowing locks (wig only; head_upper byte-identical to v3.23)

## Changes (hair_v324.py)
- Flow (new FLOW dict in lock_field): every lock centreline = swept arc + S-wave x1.6 (one phase per side -> neighbouring locks flow together in streams)
  + tip trail/curl 10 deg in the sweep direction (t^3) + theta bow 0.25 on the sides (fall first, then trail back diagonally into the fly-aways; back 0.075, fringe 0)
  + twist x1.6 (crest drifts across the lock). All C-infinity paths: no kinks along the locks.
- Fringe: tips shortened (F1 -9 deg, F2..F5 -6 deg, from the silhouette overlays: the v3.23 fringe edge sat ~15-20 mm below the photo's), F2/F3 curl out +-12 (flows down and out).
- Varied lengths: back B1 L/R 106/103 (was 110/106), B2 112/104.
- Fly-aways: root lowered th 55/58 -> 63/62, blades droop out-and-down with the stream (up -0.30 R / -0.10 L), same section (root ~29 x 10 mm, >=4 mm except last ~10 mm), same boss fillet.
- TRUNK_CUT PH1 134 -> 158 (the trailing S23/back tips at full pitch+yaw).
- Kept: broad chunky triangular cross-section, hard crests, V notches (EPS_LOCK 0.25), sawtooth forks, sideburns (+-60 to th 108).
- Iterated 12 variants (measure319/iou_A..L.json) - chosen = L.

## Silhouette (measure319/iou_v324.json)
| view | IoU v3.23 -> v3.24 | outline outside hat mm | outline (all) mm |
|---|---|---|---|
| original | 0.387 -> 0.412 | 12.50 -> 10.87 | 15.54 -> 14.96 |
| front | 0.442 -> 0.472 | 9.21 -> 9.06 | 10.33 -> 10.28 |
| 3/4 | 0.495 -> 0.496 | 10.35 -> 9.63 | 12.20 -> 11.77 |

## Checks
eye coverage 0/0; overlaps 0 (bezel gap 2.94 mm); watertight, 1 body; head-range contacts 6/315 (v3.23 7); arm sweep 0/7/7 (v3.23 0/11/9);
walls body_min 1.28 mm, p1 2.64, median 12.0; blend kinks >35 deg 34 (v3.23 42), max height jump 12.4 mm (26.7); 238.8 x 248.6 x 235.3 mm fits P1S;
~169 g + 47 g tree support, ~13.5 h (v3.23 at 4 %: 181 + 76 g, 16.1 h).

## Infill sweep on the final geometry (sim/sweep324.txt; head+arm margin mm)
0% 25.2 | 1% 33.2 | 1.5% 32.1 | 2% 32.1 | 3% 23.9 | 4% 29.5 (x3, identical) | 5% 32.0 | 6% 20.3.
Deterministic (fixed seed, repeats identical) but very sensitive to small mass changes (20-33 mm across 0-6 %). Chosen 2 % lightning (1-2 % plateau >= 32 mm).

## Sims (2 %, sim/compare_v323_v324.md)
mass 2.556 kg; head pitch standing 0.196 N·m (2.5x vs 0.49); head+arm margin 32.1 mm; walk max-speed 100 % / 0.197 m/s; energy-aware 100 % / 0.161 m/s (no refine needed).
