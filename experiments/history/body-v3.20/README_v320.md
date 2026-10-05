# Twiglet v3.20: v3.19 wig with the long side locks trimmed (only the wig changed)

**What changed from v3.19** (`hair_v320.py`)
- Long side locks shortened:
  - S2 L/R now end at th 118/119 deg (v3.19: 124/126).
  - S3 L/R now end at th 112/116 deg (v3.19: 116/128).
- New tip trim, `TRUNK_CUT`: tips are cut below th 105 deg in the band |phi| 104-134 deg, with a 4 deg ramp. This is where the side-lock tips hit the torso at combined head pitch, yaw and roll. Trimmed edges still end in the 1.3 mm lip.
- Unchanged: the fringe (5 locks), the eye-level flares, the back locks B1-B4, the S-curves and twist, `ARM_CUT` and the crown blend.
- head_upper is byte-identical to v3.19 (same vertices, 4 pins, key and glue land).

**How the trim was chosen.** 8 variants were measured (`headrange_v320.py` plus `measure_v320.py`). Plain shortening reached only 10-11 contacts. Longer locks plus the tip trim reached 6 contacts and kept more of the photo match.

**Silhouette match** (same method as measure_v319; outline distance is measured outside the hat)

| Photo | IoU v3.18 / v3.19 / v3.20 | IoU outside hat v3.18 / v3.19 / v3.20 | Outline v3.18 / v3.19 / v3.20 (mm) |
|---|---|---|---|
| Original | 0.354 / 0.381 / 0.377 | 0.525 / 0.563 / 0.557 | 15.5 / 12.6 / 13.8 |
| Front | 0.485 / 0.493 / 0.499 | 0.570 / 0.571 / 0.582 | 8.5 / 6.5 / 8.1 |
| 3/4 | 0.502 / 0.516 / 0.494 | 0.579 / 0.585 / 0.561 | 10.2 / 7.5 / 10.4 |

**Checks**
- Head-range wig contacts: **6/315**, all against the trunk at the pitch 30-45 plus roll -30 corners (v3.19: 36; v3.18: 8).
- Arm sweep: 0/11/11.
- Eye coverage: 0/0%.
- Overlaps: 0 with every head part, bezel and the snout.
- Walls: body minimum 1.13 mm (at a lip; v3.19: 1.15), p1 2.1 mm, median 9.8 mm.
- Fits the P1S: 237 x 186 x 234 mm.
- Print estimate: about 146 g plus 30 g of support, about 11.0 h.

**Infill:** 3% lightning, unchanged. The head+arm margin is 32.7 mm, so no sweep was needed. The gaits carried over from v3.19 without a re-refine.

Sim table: `sim/compare_v319_v320.md`.
