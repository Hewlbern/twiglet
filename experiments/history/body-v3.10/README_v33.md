# Twiglet body v3.3

Builds on v3.2 (`README_v32.md`). The changes:
1. The head is 180 mm, measured against the photo, with its mounts re-cut to the real hardware.
2. The barrel torso is rounded, with a domed top.
3. A tapered wooden neck column sits on the barrel top.

## 1. Head: 180 mm ball (v3.2: 190)
- **Photo measurements** (`measure/v33_head_size.json`, `renders/head_size_photo_compare.png`):
  - Body proportions put the bare ball at about 150–180 mm (torso ratio ~161, floor-to-head ~165, shoulder ratio ~180).
  - With the same camera, the 180 mm model silhouette matches the photo's hair outline (x 495–795 px vs 485–795). 190 and 200 are visibly too big.
- **Re-cut to the 1:1 hardware** (`head_recut.py`):
  - Outer shells, snout, fringe, collars and bezels are scaled ×1.0588 about the chin line.
  - The deck (roll-mount holes, Pi and board bosses, dome columns) stays 1:1 and is bridged to the bigger wall.
  - The display carriers and 2.1" modules stay 1:1 and move with the bigger eye (about 1–2 mm out, 4.8 mm up). The M3 insert posts are re-made under them.
  - The pod lift-out clearances are re-cut, and the chin collars get 0.3 mm clearance to the deck.
- **Head print pack:** `$WORK/twiglet-head-v3.3-stl.zip` with `print_sheet_head.md` (about 487 g, ~31 h).
- **Neck torque:** static neck pitch is 0.302 N·m in MuJoCo, 1.62× under the 0.49 N·m rating (v3.2: 1.55×).

## 2. Torso: rounded barrel (`design_v3.py`)
- **Shape:** `BARREL_N` 4 → 2.5 (rounded, no flat faces). The rear and front half-depths now vary with height (`BARREL_ABZ`/`BARREL_AFZ`) and dome into the neck. The vine relief is kept.
- **Depth:** stays about 152 mm. The battery holder at x −100 (up to z 80) and the front cradle at x 42 set it. The rear is 2–5 mm deeper at z 65–83 for holder clearance, and the front 1.5 mm deeper at z 55–81 for the neck side-plate at −1° neck pitch.
- **Inside:**
  - battery 7 mm lower (`BAT_DZ` −14);
  - power switch moved inboard, with a left-side access slot;
  - back rail full width to z 70, then ±23 mm;
  - shoulder rails fused to the hip-yaw sleeves (the z 84–88 side ties are removed).

## 3. Neck column
- **Geometry:** `NECK_COL` is a rounded-rectangle tapered tube from z 84 to z 95 (wall 7 → 2.6 mm), with the front of its top bevelled.
  - The bore (x −4.5..38.5, y ±25.5) is the measured swept footprint of the neck mechanism (x −2..33, y ±23) plus clearance.
  - The head is 6 mm higher (`NECK_CUT` 10 → 4). About 5–8 mm of wooden column shows between the dome and the head's black chin collar (photo neck gap ~11.5 mm).
- **Collision sweep:** neck pitch −1..+5°, head pitch −34..+8°, yaw ±150°, roll ±5°.
  - Collision-free across the whole sim soft box as long as combined forward neck + head pitch is ≤ +3°.
  - The full −34° nod is kept.
- **Soft limits** (`sim/episode.py`): neck −1..+3°, head pitch −34..**0°** (v3.2: +3°). Any split with neck + head forward ≤ 3° is also collision-free.
  - The +3° could not be relaxed: past it, the chin collar's rear edge meets the barrel top when combined with roll or yaw.
  - Single-joint free ranges: neck −1..+9°, head −40..+10°, roll ±12°.

## Collision check (`collide_v3.py` → `collide_report.json`)
- **At rest and in gait:** no clashes at rest. Both-legs gait samples: 0 of 120. Arms moving during gait: 0 of 80 (v3.2: 1). Single-leg samples at stock limits: 20 of 120, the same foot/ankle contacts as before, which the soft limits avoid.
- **Arm sweep:** 56 poses collide, but only 2 are inside the arm rule (25 − shoulder ≤ elbow ≤ min(110, 105 − shoulder)). Both are shoulder 110° with elbow −10° (straight arm raised overhead), where the forearm touches the chin collar. v3.2 had 6 such poses, starting from shoulder 100°.

## Sims (`sim/compare_v32_v33.md`)
- **Mass:** 2.256 kg (v3.2: 2.291).
- **Tipping:** front 11.4° (11.2); side 16.6° (16.5).
- **Static loads:** knee 0.91× rated (0.94×); neck 0.302 N·m (0.317).
- **Walk:** 100% at 0.155 m/s max-speed (0.160, v3.2 gait not re-refined); energy-aware 100% at 0.129 m/s (0.128).
- **Head+arm test:** no fall, min support margin 32.6 mm (29.9). **Neck peak is 0.912 N·m (0.826).** That's a dynamic peak. It isn't caused by the new head-pitch limit (0.920 with the old +3°). It is probably the head riding 6 mm higher over the low neck-pitch axis (z 28), together with the re-cut head's mass distribution.

## Files
- `stl/v33_*.stl`: 37 print-oriented parts, all watertight, single body, P1S fit (`build_report.json`). The head parts are copied from `stl_head/`. v3.2 files are in `stl_v32_old/`.
- Renders (`renders/`):
  - `compare_photo_v32_v33.png` (photo | v3.2 | v3.3: front, side, photo angle);
  - `v33_three_quarter_photo_match.png`, `v33_front.png`, `v33_three_quarter_nokilt.png`, `v33_side_nokilt.png`;
  - `overlay_v33_on_photo.png`, `overlay_photo_v32_v33_side_by_side.png`, `head_size_photo_compare.png`.
- Collision results: `collide_report.json`.
- Scripts: `export_v3.py`, `export_head_v33.py`, `render_v33.py`, `head_size_compare.py`, `head_recut.py`, `sim/compare_v33.py`.
