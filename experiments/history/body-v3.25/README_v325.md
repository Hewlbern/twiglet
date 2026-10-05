# Twiglet head v3.25 - less spiky, wispy felt clumps, clearer gaps, photo sideburns (wig only; head_upper byte-identical to v3.24)

Photos (zoomed crops, original primary): felt locks = broad flat slabs with softly rounded surfaces, soft tapered (blunt) points, no needles/forks,
clear dark V gaps between clumps. Sideburns: one long lock per side hanging BESIDE THE EAR (further back than v3.24's +-60), robot's right one to
about snout-top level, robot's left one a bit longer, standing off the cheek at the bottom.

## Changes (hair_v325.py: SOFT, SB_LIFT)
- Section 50 % rounded (superellipse n=2) + 50 % faceted (was fully faceted); no sawtooth forks; soft tapered ends (end width 0.12 x root, taper exp 0.8 -> 0.7).
- Gaps: bases x0.82 + a 5 mm V-gap carved along every lock/lock seam (not under the fly-away blades).
- Sideburns: phi +-60 -> +-73, 24 -> 20 mm root, th 108 (L) / 106 (R), stand-off 10 mm below th 88, narrow exemption from the arm relief.
- Crest heights x0.95; F1 th1 58 -> 59, F2 51 -> 46; B2 L 112 -> 108; min lip 1.65 mm radial, no sliver band at lock edges;
  fly-away ends blunted, 2.0 mm blade edge lip; ARM_CUT TH 86 -> 80; TRUNK_CUT PH1 158 -> 168.
- Variants: measure319/iou_{base,A..Z}.json (A-M softness/gaps, N-Z sideburn position/length/lift + wispiness); chosen Z.

## Silhouette (measure319/iou_v325.json)
| view | IoU v3.24 -> v3.25 | outline outside hat mm | outline (all) mm |
|---|---|---|---|
| original | 0.412 -> 0.400 | 10.87 -> 11.73 | 14.96 -> 14.86 |
| front | 0.472 -> 0.500 | 9.06 -> 7.80 | 10.28 -> 8.79 |
| 3/4 | 0.496 -> 0.492 | 9.63 -> 10.23 | 11.77 -> 12.09 |
| mean | 0.460 -> 0.464 | 9.85 -> 9.92 | 12.34 -> 11.91 |
(Variant M, before the wispy/sideburn feedback, beat v3.24 on all 9 numbers: 0.412/0.476/0.505, 10.63/8.59/9.12, 14.69/9.75/11.21 - the
photo-matched sideburns beside the ear gain a lot in front but cost some in the original and 3/4 views; with the arms raised the photo's long
side hair behind the ear cannot be reproduced without arm contacts.)

## Checks
eye coverage 0/0; overlaps 0 (bezel gap 2.94 mm); watertight single body; head-range 6/315; arm sweep 0/7/7; 246.2 x 247.5 x 248.1 mm fits P1S;
walls: wall_v325.py ray check on the exported STL body_min 1.41 mm, p1 2.31, median 12.4; 3 x 8000-sample model-frame ray check +
cross-section inscribed-circle test at every reading < 1.2 mm: 0 genuinely thin (min local wall 1.39 mm).

## Infill sweep on the final geometry (sim/sweep325b.txt; head+arm margin mm)
0% 29.4 | 1% 31.6 | 2% 31.2 (x2 identical) | 2.5% 32.6 | 3% 32.4 | 3.5% 29.8 | 4% 29.7 | 5% 25.1 | 6% 31.3 | 7% 32.3 | 8% 20.5.
Deterministic, but sensitive to small mass changes. REQUIRED: 3 % lightning (2.5-3 % plateau).

## Print (P1S, 3 % lightning): ~188 g + ~71 g tree support, ~16.2 h (v3.24: 169 + 47 g, 13.5 h at 2 %).

## Sims (3 %, sim/compare_v324_v325.md)
mass 2.575 kg; head pitch standing 0.187 N·m (2.6x vs 0.49); head+arm margin 32.4 mm; walk max-speed 95 % -> refined 100 % / 0.200 m/s;
energy-aware 100 % / 0.163 m/s.
