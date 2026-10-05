# Twiglet head v3.28 - wig only (head_upper unchanged since v3.16; attachment identical)

Mike's feedback on v3.27: "keep working on getting it closer with the hair."
Targets from the v3.27 vs photo comparison: fuller, more layered hair over the brow and temples (stacked, overlapping locks);
fringe side locks longer and fuller over the eye tops and outer eye corners; side hair further down toward the cheeks,
with less bare head shell showing near the hat edge (especially the robot's left in the front view); felt-like strand grooves along each lock.

## Changes (hair_v328.py, baked "v3.28 tuning" block = variant V5 of V1-V8 in $WORK/tmp/v328)
- Fuller clumps: front lock crests x1.42 (was x1.30), side crests x1.26 (was x1.20).
  x1.32 on the sides reached the raised forearms (arm contacts 13).
- F4/F5, the fringe side locks over the outer eye corners: 62 mm wide (was 56), crest 22 mm (was 19).
- F2/F3, the neighbours of the central strand: crest 19 mm (was 17.1), so fuller over the eye tops. The eye screens stay 100 % clear.
- Layering: a new shorter temple lock on each side (locks 15/16: phi +-38, th 18-60, 30 mm, crest 22 mm), stacked OVER F2/F4.
- Side hair lower: a new cheek lock on each side (locks 17/18: phi +-60, th 30-98, 30 mm, crest 16 mm). It hangs beside the cheek in front of the arm path.
  - th1 98 is the lowest that keeps the arm sweep at 0/7/7; th1 104 hit the raised forearm.
  - Rear-side locks at phi +-100/105 were also tried (V6-V8) and rejected (arm contacts 9).
- Felt strand texture: 4 soft grooves along every lock (8 % of local height), 2 faint ones on the central triangle.
  The central strand's flat facets and centre ridge are kept.
- Fly-away blades: the blade end is now a >= 2.2 mm wide rounded stub. The elliptical end cap used to taper the last ~1 mm to a sliver, and the first v3.28 wall check flagged 0.8 mm there.
- Kept from v3.27: central flat-faceted triangle strand + neighbours (shape and position), soft rounded sideburns, hat seat
  (8 mm smooth crown + 4.5 mm recessed band), felt-hat render proxy.

## Silhouette vs photos (IoU / outline outside hat mm / outline mm; same fitted cameras, new felt-hat proxy)

| view | v3.26 | v3.27 | v3.28 |
|---|---|---|---|
| original (primary) | 0.428 / 11.38 / 14.53 | 0.437 / 10.71 / 14.05 | 0.436 / 10.56 / 14.01 |
| front | 0.498 / 7.75 / 8.72 | 0.517 / 7.66 / 8.61 | 0.522 / 7.78 / 8.70 |
| 3/4 | 0.555 / 10.11 / 11.02 | 0.536 / 10.14 / 11.07 | 0.534 / 9.90 / 11.05 |

Old-hat like-for-like: v3.27 0.408 / 0.499 / 0.490, v3.28 0.410 / 0.516 / 0.493.
Silhouette is roughly flat vs v3.27. The front view improves, and the outline outside the hat tightens on the original and 3/4 views.
The main gains are in the look: fuller layered locks, the fringe over the eye tops, lower sides and felt grooves (hair_closeup_v327_v328.png, hair_flow_v328.png).

## Checks

| check | v3.27 | v3.28 | limit |
|---|---|---|---|
| eye coverage L / R | 0 / 0 % | 0 / 0 % | 0 % |
| head-range contacts | 6/315 | 6/315 | <= ~8 |
| arm contacts (pitch 0 / -45 / +45) | 0/7/7 | 0/7/7 | <= 0/7/7 |
| head pitch static (standing) | 0.203 N·m (2.4x) | 0.211 N·m (2.3x) | <= 0.245 (2x vs 0.49) |
| head+arm min support margin | 32.5 mm @ 4 % | 33.3 mm @ 5.5 % | >= ~32 mm |
| walls (wallsec, 2 seed sets) | 0 thin | 0 thin (min 1.39 / 1.5 mm) | >= 1.2 mm |
| watertight / bodies | yes / 1 | yes / 1 | 1 |
| size oriented | 241.0 x 248.7 x 247.7 | 239.6 x 247.1 x 248.8 mm | fits P1S (256) |
| wig volume / sim mass | 652.1 cm3 / 213.9 g | 658.6 cm3 / 216.4 g | - |
| fast gait (20 randomized) | 100 % @ 0.213 m/s | 100 % @ 0.210 m/s | 100 % |
| energy gait | 100 % @ 0.161 m/s | 100 % @ 0.162 m/s | 100 % |
| total mass | 2.575 kg | 2.587 kg | - |

Infill sweep (sim/sweep328.txt, head+arm min margin mm):
0 % 32.3, 0.5 % 29.5, 1 % 24.6, 1.5 % 32.6, 2 % 29.7, 2.5 % 29.8, 3 % 29.3, 3.5 % 27.5, 4 % 27.3, 4.5 % 20.7,
5 % 20.4, **5.5 % 33.3**, 6 % 29.6, 6.5 % 29.6, 7 % 21.0, 7.5 % 25.8, 8 % 25.6, 9 % 18.4, 10 % 25.0.
- The margin is noisy against infill.
- 5.5 % lightning is the only practical setting >= 32 mm: 0 % would leave the lock tops unsupported, and 1.5 % is marginal for top skins.
- The sims (gen_mjcf_v3 default) and the print note both assume 5.5 %.
- Walks were run at 5.5 % with no refine needed.
- Full sim table: sim/compare_v327_v328.md.

## Print
- Wig: ~200 g + ~55 g tree support, ~16.0 h on the P1S.
- 0.2 mm layers, 2 walls, 3 top / 3 bottom, **5.5 % LIGHTNING infill** (required by the sims; v3.27 was 4 %).
- One piece, oriented as exported (least support of 6120 orientations), tree supports auto + 5 mm brim.
- Reprint the wig only. Same 4 pins / keyed tongue / glue land as v3.16-v3.27, so it fits the head_upper already printed.

## Note - box restore (30 Sep ~23:35)
- The shared box was restored from a backup and every .cache dir was lost (including v3.27's head pickles).
- head_upper was rebuilt from the surviving v3.15 head pickle (old pin holes plugged, v3.16 pin holes + key groove re-cut).
- Checked against the v3.16 head_upper STL as printed: median surface deviation 0.18 mm, p99 0.41 mm, max 2.1 mm; volume 122906 vs 123105 mm3.
- Its mesh md5 is now 9602cf15..., not the old c7039022..., so byte-identity can no longer be shown. The wig envelope, pins and key are the same, so the v3.28 wig mates with the printed head_upper.
- v3.27 was rebuilt in ../body-v3.27r (hair_v327.py unchanged; reproduces 652.1 cm3 / 213.9 g) for the v3.27 columns of the renders. ../body-v3.27 was not modified.
