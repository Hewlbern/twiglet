# Twiglet v3.21: deep triangular locks (only the wig changed)

**Changes from v3.20** (`hair_v321.py`, `FACET` / `FORK` dicts)

Unchanged from v3.20:
- Layout: all 15 locks, with the same roots, directions and lengths.
- Trims: S2/S3 shortening, `TRUNK_CUT` and `ARM_CUT`.
- head_upper: byte-identical (same pins, key and glue land).

Lock shape:
- **Cross-section:** linear, so each lock has flat facets meeting at a hard crest ridge (v3.20 used a (1-u)^0.7 rounded wedge). Straight-sided triangular taper along the length (v3.20: leaf-shaped).
- **Crest height:**
  - Fringe F1-F3: 1.35x taller (F1 about 26 mm) and 1.7x wider bases, so neighbouring locks meet in deep V notches.
  - Side and back locks: 1.12x / 1.2x, applied only below the temple (th > 52 deg), so the front silhouette and hat fit are kept.
- **Valleys:** a near-hard max between locks (EPS 1.2 → 0.25) gives sharp V valleys. The dome now fades out under the hat brim (th 34 deg; v3.20: 50 deg).
- **Valley floors:** they bottom out on a shell of at least 1.25 mm under the hat. Lower down, the notches open to the head.
- **Sawtooth tips:** the flares, the S2/S3 locks, the back locks and F4/F5 split into two points.
- **Eye clearance:** the over-eye fringe tips fall away faster, so the hearts stay 100% clear.

Crest and valley depth (`crest_valley_v321.json`, median around each ring):

| th (deg) | Crest height v3.20 → v3.21 (mm) | Valley depth, median (max), v3.20 → v3.21 (mm) |
|---|---|---|
| 50 | 14.3 → 15.1 | 3.6 (8.3) → 5.9 (12.8) |
| 60 | 13.0 → 15.2 | 5.9 (11.4) → 10.3 (17.1) |
| 70 | 11.5 → 14.0 | 7.5 (13.0) → 12.5 (18.7) |

**Silhouette match** (same method as `measure_v319`, v3.18 / v3.20 / v3.21)

| Photo | IoU | IoU outside hat | Outline outside hat (mm) |
|---|---|---|---|
| Original | 0.354 / 0.377 / 0.390 | 0.525 / 0.557 / 0.563 | 15.5 / 13.8 / 13.6 |
| Front | 0.485 / 0.499 / 0.469 | 0.570 / 0.582 / 0.546 | 8.5 / 8.1 / 8.6 |
| 3/4 | 0.502 / 0.494 / 0.497 | 0.579 / 0.561 / 0.557 | 10.2 / 10.4 / 10.0 |

The front IoU drops because the V notches between fringe locks now show the forehead, and the upper side crests are taller.

**Checks**
- Head range: 4/315 contacts.
- Arm sweep: 0/11/11.
- Eye coverage: 0/0%.
- Overlaps: 0.
- Walls: body minimum 1.22 mm, p1 2.9 mm.
- Fits the P1S: 250 x 204 x 181 mm.
- Print: about 147 g plus 30 g of support, about 11.1 h.

**Infill:** 3% lightning, unchanged. Head pitch 0.209 N·m (2.34x); head+arm margin 33.0 mm.

**Gait:** the max-speed gait scored 95% on v3.21 with the v3.20 parameters. walk_refine (REFINE_SEED=33) restored 100% at 0.196 m/s. The pre-refine parameters are in `sim/bak_pre_refine_v321/`.

Sim table: `sim/compare_v320_v321.md`.

Renders:
- `renders/hair_closeup_v320_v321.png`: fitted cameras, directional key light.
- `renders/hair_facets_v320_v321.png`: zoomed facet view; top row v3.20, bottom row v3.21.
