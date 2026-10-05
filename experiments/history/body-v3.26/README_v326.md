# Twiglet head v3.26 - soft-pointed felt locks + a hat seat (wig only)

Mike's feedback on v3.25: "Make it less spikey and more close to the image please." After the first v3.26 preview: "No it needs to be
somewhat pointed. Keep it like the photos hair, and make sure the hat on top is well separated and like the image."

## What changed (wig only; head_upper byte-identical to v3.25; v3.25 folder untouched)
- **Lock ends: soft small-radius points.** Each lock tapers to 0.1 x its root width (never under 4 mm). It then finishes in a round end about 2-4 mm in radius, both in plan and as a domed end in side view. There are no needles and no forks, and none of the blunt paddle ends from the first v3.26 preview. Fringe and fly-away blades end the same way.
- **Rounder felt clumps.** The cross-section is 80 % rounded (v3.25: 50 %). Crests are lower (CREST_K 1.45/1.3/1.2 -> 1.3/1.2/1.1). There are 4 mm V-gaps between locks. The flowing S-waves, twist and fly-aways are kept.
- **Silhouette.** Some shape from the earlier "M" variant is blended back in: taper exponent 0.65, gap depth 4 mm, F2 th1 51.
- **Sideburns.** Sideburn roots moved to phi +-79. They drift forward and hang at phi ~67-74 beside the ears. Crest height is 12 mm.
- **Arm-relief exemption.** The exemption now follows where the sideburn actually hangs. Before, it was letting the tail of lock F4 through, which gave 8 arm contacts. ARM_CUT TH is 77.
- **Hat seat (new).** The felt hat's edge is a tilted circle: 50 deg about an axis at az 169 / el 53. It sits just above the fringe at the front, drops over the robot's left ear, sits higher on the right, and is low at the back.
  - Inside that circle the wig is a smooth 8 mm crown with no locks.
  - Just outside it there is a recessed band, 4.5 mm deep and 2.4 deg (~4 mm) wide, before the locks rise.
  - So the edge of the fabric hat sits on a clean shadow step all the way round.
- **Edge lips.** Bare vertices now dive under the seat, so every free lock edge is a steep 1.65 mm lip. There are no knife-edge wedges.
- **Hat in the renders.** The real hat is Mike's fabric/felt hat and is **not printed**. The green hat in the renders is a render proxy (`hat_v326.py`) on the same edge circle. It has a rolled cuff (10 mm proud, ~16 mm tall, rounded lower edge), a full rounded crown, and the tail flopping over to the robot's left and down to neck level, as in the photo. It is opaque now; the old ghost hat was 60-85 % translucent, which is why it seemed to blend into the wig.

## Silhouette (measure_v326; 'outside hat' excludes each model's own hat footprint)
| photo | v3.25 IoU / outline outside hat / outline (mm) | v3.26 (new hat proxy) | v3.26 measured with the OLD ghost hat (like-for-like) |
|---|---|---|---|
| original (primary) | 0.400 / 11.73 / 14.86 | **0.428 / 11.38 / 14.53** | 0.398 / 10.67 / 14.72 |
| front | 0.500 / 7.80 / 8.79 | 0.498 / **7.75 / 8.72** | 0.485 / 7.93 / 8.92 |
| 3/4 | 0.492 / 10.23 / 12.09 | **0.555 / 10.11 / 11.02** | 0.507 / 9.77 / 11.47 |

## Checks (final geometry)
| check | v3.26 | limit |
|---|---|---|
| eye coverage L / R | 0 % / 0 % | 0 % |
| head-range contacts | 6 / 315 (trunk only, pitch 45 + roll 30 extremes) | <= ~8 |
| arm sweep contacts (yaw 0 / -45 / +45) | 0 / 7 / 7 | <= 0/7/7 |
| head pitch static | 0.197 N·m = 2.5x under 0.49 rated | >= 2x |
| head+arm test margin | 32.9 mm at 3 % (sweep: 0 % 32.9, 1 % 32.6, 2 % 27.3, 2.5 % 30.7, 3 % 32.9, 3.5 % 32.7, 4 % 23.8, 5 % 23.3, 6 % 28.7, 7 % 21.9, 8 % 31.2) | >= ~32 |
| walls | cross-section test: 0 spots genuinely < 1.2 mm, min local wall 1.25 mm (ray probe 0.6 mm only at lip edges) | >= 1.2 |
| wig mesh | watertight, 1 body, 609 cm3, 0 overlap with every head part, seat gap 0.3 mm | |
| P1S fit (as oriented) | 240.8 x 248.2 x 247.1 mm | 256 |
| head_upper | byte-identical to v3.25 (md5 of vertices + faces) | identical |
| total robot mass | 2.561 kg (v3.25 2.575) | |
| walk, max-speed gait | 95 % (19/20) at 0.206 m/s, 11.3 A. Refined 3x (seeds default/33/7), best stays 95 %; v3.25: 100 % at 0.200 | |
| walk, energy-aware gait | 100 % at 0.160 m/s, 10.8 A (v3.25 100 % at 0.163) | |

## Print (P1S, one piece, blond matte PLA)
- 0.2 mm layers, 2 walls, 3 top/bottom, **3 % lightning infill** (the sims assume 3 %). About 174 g + 51 g tree support, about 14.0 h (v3.25: 188 g + 71 g, 16.2 h).
- Put your fabric hat on so its edge sits in the recessed band all the way round.

## Files
- $WORK/twiglet-head-v3.26-stl.zip (wig STL, print note, print report, closeup, flow render, this README)
- $WORK/hair_closeup_v325_v326.png (photo crops | v3.25 | v3.26, lit, hats included; sideburn/fly-away panel below)
- body-v3.26/renders/hair_flow_v326.png (front / 3/4 / both sides, v3.25 top, v3.26 bottom)
- Sources: body-v3.26/hair_v326.py (final tuning block after LOCK_INDEX), hat_v326.py (render hat proxy), sim/sweep326.txt, sim/cmp326.log
