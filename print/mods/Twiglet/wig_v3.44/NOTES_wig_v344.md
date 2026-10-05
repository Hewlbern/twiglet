# Wig v3.44 (hair v3.44, final variant c14)

One-piece printed wig that sits on `head_upper` (4 pins + keyed tongue, same cap/pin fit as v3.30-v3.43).

| | v3.40 (y2) | v3.43 (b6) | **v3.44 (c14)** |
|---|---|---|---|
| mass at 4.5 % lightning | 176.4 g | 182.4 g | **186.2 g** (budget 186.5 g) |
| head-pitch hold on the hair base body (`quick_static`, 0.4897 N·m / ctrl) | 2.13× | 2.112× | **2.151×** (ctrl 0.2277); 2.297× with the skin-COM estimate |
| head-pitch hold on the v3.34 body (this repo, 0.49 N·m / ctrl) | 2.09× | – | **2.11×** (ctrl 0.2323) |
| eye coverage / overlaps | 0 / 0 | 0 / 0 | **0 / 0** |
| wig vs arms inside the soft limits (yaw 0/−45/+45) | 0/0/0 | 0/0/0 | **0/0/0** (raw 3/32/38) |
| 315-pose head range: any contact / wig contact / wig-only | 154 / 34 / 0 | 154 / – / 0 | **154 / 32 / 0** |
| min wall (60k copy) | – | 2.41 mm | **2.39 mm**, none < 2 mm |
| mesh | watertight | watertight | **watertight, 1 body, 59,984 faces, 624.9 cm³** |
| print size (oriented) | 248 × 223 × 242 mm | – | **243.1 × 246.4 × 239.9 mm** (fits the P1S), support ~473 cm³, overhang 212 cm² |

What changed from v3.43 b6 → v3.44 c14:
- fuller side curtains (S1 lower half ×1.8, split into 2 felt-like blades) and longer sideburn lower halves, front fringe blades thinned 6.0 → 5.2 mm;
- longer central lock tip; back locks B1/B2 lifted 1.5 mm (they are the head's pitch counterweight, so the hidden back hair was kept);
- hidden-under-hat squash in front of the pitch axis only (fades out by θ 24–28°);
- crown closed again (c13 had a top opening); the hidden crown top under the hat (θ < 14°) thinned 7.5 → 3.0 mm and the side-curtain blades 6.5 → 5.6 mm to stay inside the mass budget.

Files: `FINAL_WIG.stl` (print this; print-oriented, crown axis 38° from straight down, centred, z0 = bed), `FINAL_WIG_model_frame.stl` (same mesh in the head model frame, used by the sims/checks), `final_export.json` (export report). Blender source: `../source/blender/hair_v344.blend` (object `FINAL_WIG_v344_c14`). Edit set: `../source/scripts/wig_v3.44/variants/c14.*`.
Print settings: [docs/print_guide.md](../../../../docs/print_guide.md).
