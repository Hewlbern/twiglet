# Twiglet head v3.29 - wig only (head_upper = the v3.28 rebuilt head_upper, unchanged)

Mike on v3.28: "Make the side hair less spikey and make the hair more like the image still."

## Changes (hair_v329.py, baked "v3.29 tuning" block = variant W13 of W1-W14 in $WORK/tmp/v329)
- **Side hair softened.** This covers the front side locks over the outer eye corners (F4/F5), side locks S1/S23, temple layers, cheek locks and back locks.
  - Fully rounded felt-clump sections (ROUND 1.0, was 0.8).
  - The taper stops at 0.22 x root width (0.20 on the back locks; was 0.14), and then a round end cap about 2 x the end width long. The ends are blunt and domed, with no points.
  - The felt strand grooves (4 per lock) are kept.
- **Fly-away blades removed.** In the renders they read as horns or flaring spikes; a round-section version (W4/W8) still looked like a horn.
  - They are replaced by two soft **temple flick locks** that follow the head: the robot's right one (phi -84, th 40-90, 46 mm wide) and the robot's left one (phi 86, th 42-90, 44 mm wide), both with a 30 mm crest.
  - The robot's right one is the big outward flick in the original and front photos. Both use the same rounded style.
- **Arm relief starts at th 77** (was 80). The fuller, blunter side ends sit where the raised forearms pass, and this keeps the arm sweep at 0/7/7.
- **Kept unchanged:** the central flat-faceted triangle strand + its two pointed neighbour strands (v3.27/v3.28), the soft sideburns, the v3.28 temple/cheek layer locks, the hat seat and the felt-hat proxy.
- **Pin-hole fix (found while checking v3.29; v3.26-v3.28 had it too).**
  - The front-left blind pin hole (th 20 / phi 45) sits in the 4.5 mm hat-edge shadow band. Its 6.5 mm depth went right through the wig there, and the two back holes had only ~1.2 mm of wig over them.
  - The holes are now 5.0 mm deep, and a >= 7.8 mm boss over each hole leaves >= 2.1 mm of wig above every hole (measured 2.12 / 2.22 / 2.22 / 2.69 mm).
  - Only the front-left boss rises noticeably: about 3.3 mm, in the band under the felt hat's edge. The other three are already covered by the 8 mm hat seat or the lock roots.
  - Same 12 mm rods: glue 5 mm into the wig; 7 mm go into head_upper's 7.5 mm holes.
- **Rejected variants:**
  - FLARE 18-28 (side ends hugging the head even more) lowered IoU.
  - Very blunt/full ends (W1-W3) and FLARE 46 (W14) gave 11-17 arm contacts.
  - Longer F4/F5 (th1 98) covered 0.6 % of the eye screens.
  - Jaw-length sideburns (W10) gave 18 head-range contacts.

## Silhouette vs photos (IoU / outline outside hat mm / outline mm; same fitted cameras, felt-hat proxy)

| view | v3.28 | v3.29 |
|---|---|---|
| original (primary) | 0.436 / 10.56 / 14.01 | 0.444 / 10.60 / 14.13 |
| front | 0.522 / 7.78 / 8.70 | 0.525 / 8.04 / 8.84 |
| 3/4 | 0.534 / 9.90 / 11.05 | 0.539 / 9.93 / 11.08 |

Old-hat like-for-like: v3.28 0.410 / 0.516 / 0.493, v3.29 0.421 / 0.516 / 0.498.
- IoU is up in all three views: the rounder, fuller side clumps and the temple flicks fill more of the photo's side hair.
- The outline distance is 0.03-0.26 mm longer, because the blunt rounded ends don't follow the photo's pointed lock tips as closely. That was the trade for "less spiky".

## Checks

| check | v3.28 | v3.29 | limit |
|---|---|---|---|
| eye coverage L / R | 0 / 0 % | 0 / 0 % | 0 % |
| head-range contacts | 6/315 | 6/315 | <= ~8 |
| arm contacts (0 / -45 / +45) | 0/7/7 | 0/7/7 | <= 0/7/7 |
| head pitch static (standing) | 0.211 N·m (2.3x) | 0.214 N·m (2.3x) | <= 0.245 (2x vs 0.49) |
| head+arm min support margin | 33.3 mm @ 5.5 % | 33.0 mm @ 4.5 % | >= ~32 mm |
| walls (wallsec, 2 seed sets) | 0 thin (but see pin-hole fix) | 0 thin (min 1.49 / 1.30 mm) | >= 1.2 mm |
| wig over the blind pin holes | open (front-left) / ~1.2 mm | >= 2.12 mm | >= 1.2 mm |
| watertight / bodies | yes / 1 | yes / 1 | 1 |
| size oriented | 239.6 x 247.1 x 248.8 | 223.3 x 243.1 x 248.4 mm | fits P1S (256) |
| wig volume / sim mass | 658.6 cm3 / 216.4 g | 716.0 cm3 / 222.1 g | - |
| fast gait (20 randomized) | 100 % @ 0.210 m/s | 100 % @ 0.210 m/s | 100 % |
| energy gait | 100 % @ 0.162 m/s | 100 % @ 0.162 m/s | 100 % |
| total mass | 2.587 kg | 2.584 kg | - |
| head_upper md5 | 9602cf15... | 9602cf15... (same mesh) | identical |

Infill sweep on the final geometry (sim/sweep329.txt, head+arm min margin mm):
0 % 33.0, 1 % 32.9, 1.5 % 22.0, 2 % 32.9, 2.5 % 25.8, 3 % 25.6, 3.5 % 27.3, 4 % 29.9, **4.5 % 33.0**, 5 % 22.0, 5.5 % 30.3,
6 % 32.9, 6.5 % 19.2, 7 % 18.9, 8 % 27.2.
- The margin is noisy against infill.
- 4.5 % lightning is the practical setting >= 32 mm. The sims (gen_mjcf_v3 default) and the print note both assume it.
- Walks were run at 4.5 % with no refine needed.
- Full sim table: sim/compare_v328_v329.md.

## Print
- Wig: ~197 g + ~64 g tree support, ~16.3 h on the P1S.
- 0.2 mm layers, 2 walls, 3 top / 3 bottom, **4.5 % LIGHTNING infill** (required by the sims; v3.28 was 5.5 %).
- One piece, oriented as exported (least support of 6120 orientations), tree supports auto + 5 mm brim.
- Reprint the wig only. Same 4 pins / keyed tongue / glue land as v3.16-v3.28, so it fits the head_upper already printed.
- The pins are now glued 5 mm deep into the wig (was 6).

## Head_upper
head_v329 loads the v3.28 head pickle and reuses its head_upper object unchanged. The head_upper mesh md5 is 9602cf153e8eeff3143673c534feaa1b, the same as v3.28.
That head_upper was rebuilt after the 30 Sep box restore and checked against the v3.16 STL as printed: median 0.18 mm, p99 0.41 mm deviation.

## Renders
- hair_closeup_v328_v329.png: photo | v3.28 | v3.29 at the cameras fitted to each photo.
  - Below that: a zoomed SIDE-HAIR panel (original: both sides; front: both sides) and the front-fringe zoom.
- hair_flow_v329.png: front / 3/4 / both sides, v3.28 (top) vs v3.29 (bottom).
