# Twiglet v3.22: chunkier, broader locks with the mid-side locks brushed across the head (only the wig changed)

**Changes from v3.21** (`hair_v322.py`)

Kept from v3.21:
- Deep triangular facets, hard crests and V notches.
- Eye clearance, `ARM_CUT` and `TRUNK_CUT`.
- head_upper: byte-identical.

Changes:
- **Fewer, bigger locks:** 13 locks instead of 15. The narrow long side locks S2 and S3 are merged into one broad swept side wedge per side (phi ±108, W 80, crest 23).
- **Broader bases:** the full-width base now sits at the hat brim (th 38°) instead of at the crown root, so the visible part of every lock is wide.
- **Base multipliers:** fringe x1.9 (v3.21: 1.7), outer fringe x1.25 (v3.21: 1.0), sides x1.4 (v3.21: 1.08), back x1.3 (v3.21: 1.15).
- **Fuller wedges:** the facet exponent is 0.85 (v3.21: 1.0 flat). Crests are x1.45 on the fringe (v3.21: 1.35) and x1.3 on the sides (v3.21: 1.12).
- **Brushed sweep:** the mid-side locks run back across the head on a steady, near-linear diagonal instead of a late S-curl:
  - S1 temple flare: curl 56° (v3.21: 14°), S-wave 2 (v3.21: 6).
  - Merged side wedge: curl 40°.
  - Outer fringe F4/F5: curl 32° (v3.21: 24°).
- **Sawtooth tips:** kept on the outer fringe and the rear back locks only. They were removed from the sides so those locks stay chunky.

**Measured on rings around the head** (`crest_valley_v322.json`):

| Ring | Mean lock width v3.21 → v3.22 (mm) | Crests v3.21 → v3.22 | Valley depth, median (mm) |
|---|---|---|---|
| th 60° | 31 → 40 | 13 → 11 | 10.3 → 8.7 |
| th 70° | 31 → 42 | 12 → 10 | 12.5 → 10.6 |

- Crest height is 15.2 mm at th 60° in both versions.
- Hair coverage at th 50° rises from 78% to 98%.

**Silhouette match** (v3.20 / v3.21 / v3.22)

| Photo | IoU | IoU outside hat | Outline outside hat (mm) |
|---|---|---|---|
| Original | 0.377 / 0.390 / 0.399 | 0.557 / 0.563 / 0.555 | 13.8 / 13.6 / 14.9 |
| Front | 0.499 / 0.469 / 0.459 | 0.582 / 0.546 / 0.533 | 8.1 / 8.6 / 11.1 |
| 3/4 | 0.494 / 0.497 / 0.510 | 0.561 / 0.557 / 0.561 | 10.4 / 10.0 / 12.5 |

**Checks**
- Head range: 6/315 contacts.
- Arm sweep: 0/11/11.
- Eye coverage: 0/0%.
- Overlaps: 0.
- Walls: body minimum 1.24 mm, p1 3.2 mm.
- Fits the P1S: 236 x 206 x 208 mm.
- Print estimate: about 160 g plus 36 g of support, about 12.3 h.

**Infill: 2% lightning** (v3.21: 3%). The heavier wig brought the head+arm margin down to 22.2 mm at 3%.

Sweep of head+arm margin (mm) against wig infill, from `sim/sweep322.txt`. The metric is noisy because the balance gains are re-searched on every run.

| Infill | 0% | 1% | 2% | 3% | 4% | 5% | 6% | 8% | 10% |
|---|---|---|---|---|---|---|---|---|---|
| Margin (mm) | 23.8 | 24.9 | **33.0** | 22.2 | 30.6 | 30.2 | 29.9 | 23.8 | 31.4 |

**Gait:** the max-speed gait scored 90% before a re-tune; walk_refine (default seed) restored 100% at 0.199 m/s. The pre-refine parameters are in `sim/bak_pre_refine_v322/`.

Sim table: `sim/compare_v321_v322.md`.
