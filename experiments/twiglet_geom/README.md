# twiglet_geom: mesh / collision checks on the assembled robot

These checks complement `../twiglet_sim/`. MuJoCo there only simulates foot-floor contact, so part-to-part clearance is checked here on the real print meshes, with trimesh + FCL.

**Scene:** `scene/scene_v334_wig344.npz` (10 MB) is the v3.34b rest-pose assembly in the assembly frame (mm; x forward, y left, z up). It has 133 meshes grouped by MuJoCo link, plus the 19 joints in its JSON metadata. The head fringe is replaced by the hair v3.44 (c14) wig (`print/mods/Twiglet/wig_v3.44/FINAL_WIG_model_frame.stl`, decimated to 40k faces) by `tools/swap_wig_scene.py`, which runs from the repo. `scene/head_meta.json` holds the head-ball centre. Use another scene with `TWIGLET_SCENE=<path>`. `tools/export_scene.py` is how the original (wig v3.40) npz was made (provenance only: it needs the original Blender build workspace).

Items whose names start with `sim_` are lumped masses from the sim (boards, battery, screws), not printed parts. Servos and horns are the stock ODM / STS3032 meshes.

```bash
pip install trimesh python-fcl scipy numpy mujoco manifold3d   # + pyvista for render_assembly.py
python head_range.py     # 3.5 min
python eye_cover.py
python arm_sweep.py
python kilt_swing.py     # ~20 min (uses ../twiglet_sim for the MuJoCo FK and the gaits); --fast = main gait only
python print_check.py    # every STL in print/mods/Twiglet (a few minutes; parts > 100k faces get their wall survey on a 60k-face copy)
python render_assembly.py   # the docs/images/assembly/ step images (15 s)
```

Outputs go to `out/` (gitignored; override with `TWIGLET_GEOM_OUT`). The reference results are in `results/`; copy a new run there by hand when it should become the reference.

| script | checks | result (wig v3.44, 5 Oct 2026, from this repo) | pass |
|---|---|---|---|
| `head_range.py` | (1) wig vs both arms at head yaw 0/−45/+45 over 156 arm poses each; (2) 315-pose head pitch × yaw × roll grid vs trunk and arms | (1) raw hits 3/32/38, **0/0/0 inside the arm soft limits**; (2) **154/315** poses with any contact (= the v3.33h/v3.34 record), wig contact 32, wig-only **0** | (1) 0 in soft limits; (2) ≤ ~154 and wig-only 0 |
| `eye_cover.py` | wig triangles inside each eye's 26.7 mm viewing cylinder | **0 / 0** | 0/0 |
| `arm_sweep.py` | arms vs shells, kilt, leaves and head (162 poses); elbow, gripper and shoulder joint sweeps | 0/0/0; elbow 0, gripper 0; shoulder 1 hit only at −10° (outside the −5° soft limit; same as the record) | 0 inside the soft limits |
| `kilt_swing.py` | kilt petals (+ band stand-in) vs leg and arm links: 1500 poses from both shipped gaits (nominal + 2 randomized seeds), 120 single-leg, 120 both-leg, 80 arms + legs, the stance series | ✅ wig v3.44 (`--fast`, main gait only): sim gaits **0/750**, stance **0/14**; single-leg 12/120, both legs 1/120, arms+legs 1/80 (= the v3.34b record). Full run with wig v3.40: 0/1500. The kilt check does not involve the wig | sim gaits 0 and stance 0; the random grids are informative (record v334b: 12 / 1 / 1) |
| `print_check.py` | watertight, 1 body, volume, P1S fit (256³), wall-thickness survey | **61/61 pass** (50 body, 10 head, wig; the v3.44 wig re-checked 5 Oct: watertight, 1 body, 624.9 cm³, fits; `FINAL_WIG_model_frame.stl` is skipped, it is not print-oriented) | watertight, 1 body, fits |
| `render_assembly.py` | — | 26 PNGs for [docs/assembly_guide.md](../../docs/assembly_guide.md) | — |

The logic of each script is copied unchanged from the original measurement scripts (`body-v3.34-body/measure/*`, `hair-v3.40/checks/*`). Only the loading changed: the scene npz instead of the Blender exports. That is why the results match the records exactly.
