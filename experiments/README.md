# Experiments

These are undocumented experiments, some of them very old. I wouldn't recommend trying to run them :)

(That is upstream's note. Upstream's experiments (LeRobot, RL, placo, mujoco, v2, ...) are not copied; see https://github.com/apirrone/Open_Duck_Mini/tree/v2/experiments.)

Twiglet keeps every simulation we ran for the Twiglet robot here, in a form that re-runs from a fresh clone. Nothing has been checked on hardware yet.

| folder | what |
|---|---|
| [`twiglet_sim/`](twiglet_sim/README.md) | MuJoCo sims: standing, push, head + arm motion, head-pitch load, both walking gaits, gait search/refine, held-out seeds, arm heating, videos. 52 MJCF models (body v3.20 to v3.34, head/wig infill sweeps, the hair series, studies) and all 22 gait parameter files |
| [`twiglet_geom/`](twiglet_geom/README.md) | Mesh/collision checks on the assembled v3.34 + wig v3.44 scene (trimesh + FCL): 315-pose head range, wig vs arms, eye coverage, arm sweeps, kilt swing, print-file checks. Also renders the assembly-guide images |
| [`twiglet_eyes/`](twiglet_eyes/README.md) | Firmware for the two ESP32-S3 round-display eyes, plus the Pi helper |
| [`history/`](history/README.md) | Read-only archive of the results of every earlier version (body v2 to v3.34, hair v3.33 to v3.41, head v2, head v3 digital eyes): 1239 json/txt/md/csv/log files, 18 short mp4s and the sim plots. [`history/sim_history.md`](history/sim_history.md) is the per-version table |
| `tools/` | `history_table.py`, which rebuilds `history/sim_history.{csv,md}` |

Setup (any Python ≥ 3.10):
```bash
pip install mujoco numpy            # twiglet_sim
pip install trimesh python-fcl scipy manifold3d pyvista   # twiglet_geom (pyvista only for render_assembly.py)
```
All scripts use paths relative to the repo. Outputs go to `twiglet_sim/out/` and `twiglet_geom/out/` (both gitignored). The reference results are in each folder's `results/`, and the scripts never overwrite them.

## Index

Current robot: body **v3.34** + head **v3.30** + wig **v3.44** (c14) = model `twiglet_sim/models/twiglet_v3_v334_wig344.xml` (2.753 kg, head 0.814 kg) and scene `twiglet_geom/scene/scene_v334_wig344.npz`. Gaits: main `walk_v3_best.npy` (= `params/walk_v3_best_v334r1.npy`), efficient `walk_v3_eff_best.npy` (= `params/walk_v3_eff_best_v333r1.npy`).

"Latest" is the newest run. ✅ = re-run from this repo copy on 4 Oct 2026 (wig v3.44 rows: 5 Oct 2026); the others are copied from the original run records.

| # | sim | what it checks | how to run (from the folder) | latest result | pass criteria |
|---|---|---|---|---|---|
| 1 | standing margin (`run_tests.py` a) | static COM margin inside the support polygon, crouch 0.10, plus the open-loop COM window | `TWIGLET_XML=twiglet_v3_v334_wig344.xml python run_tests.py v3` | ✅ 50.5 mm (v3.34 body alone: 50.8) | no fall, margin > 30 mm (TODO: no formal limit in the records; v3.x ran 41–51) |
| 2 | push recovery (`run_tests.py` b) | largest impulse survived, with and without the balance controller | same run | ✅ with controller: fwd 1.59 / back 1.01 / left 1.81 / right 1.83 N·s | informative (no fixed limit) |
| 3 | weight shift / single support (`run_tests.py` c) | hip-roll sine shift; single-leg stance attempt | same run | ✅ in `results/v334_wig344/results_v3.json` | no fall at the 0.05–0.15 amplitudes |
| 4 | head + arm motion, neck load (`run_tests.py` e) | full head pitch/yaw/roll + arm waving while standing: min support margin and the peak servo torques (head-pitch headroom) | same run | ✅ e-margin **34.1 mm**, head pitch peak **0.796 N·m** = 2.40× the STS3215 stall (1.91 N·m); static hold 0.232 N·m = 2.11× the 0.49 N·m rating; v3.34 alone 34.0 / 0.808 (2.36×) | no fall, e-margin ≥ 30 mm, head-pitch hold ≥ 2× |
| 5 | main gait (`walk_eval.py`) | 10 s nominal walk + 20 randomized trials (mass ±10 %, friction, armature, latency…) | `TWIGLET_XML=twiglet_v3_v334_wig344.xml python walk_eval.py v3` | ✅ **19/20** at 0.206 m/s (wig v3.40: 20/20 at 0.210; v3.34: 20/20 at 0.208) | ≥ 19/20 |
| 6 | efficient gait (`walk_eval.py --eff`) | same, energy-aware gait | `... python walk_eval.py v3 --eff` | ✅ **20/20** at 0.156 m/s | ≥ 19/20 |
| 7 | held-out seeds (`walk_heldout.py`) | the main gait on 20 seeds never used in the search (6000–6019) | `TWIGLET_XML=twiglet_v3_v334_wig344.xml python walk_heldout.py v3 walk_v3_best.npy <tag>` | ✅ **18/20** at 0.206 m/s (wig v3.40: 19/20 at 0.202; v3.34 record: v334r1 = s35 19/20 at 0.207; s34 17/20, s36 18/20, v333r1 19/20 at 0.187) | ≥ 18/20 |
| 8 | all of 1–6 in one go (`run_all.sh`) | runs tests + both gaits for one model, logs to `out/<tag>/`, one line to `out/sim_summary.txt` | `./run_all.sh twiglet_v3_v334_wig344.xml mytag` | ✅ v334_repo, v334_wig340 and v334_wig344 (`results/sim_summary_repo_runs.txt`) | as 1–6 |
| 9 | gait refine (`walk_refine.py`) | local refine of a gait for a new body: 24 perturbations × 10 seeds; how v334r1 (= s35) was found | `TWIGLET_XML=... python walk_refine.py v3 [--eff]` | v3.34: s35 picked (`results/record_v334_r2/walk_refine_v334s3*.json`) | better success × speed than the start params |
| 10 | gait search (`walk_search.py`) | random search + CEM from scratch (12 params), then the robustness check | `python walk_search.py v3 [N] [--eff]` (hours; writes `out/*_search*`) | origin of the gait lineage in `params/` (see `params/MANIFEST.json`); not re-run | as 5/6 |
| 11 | arm heating (`arm_heat.py`) | 30 s continuous arm waving while standing: STS3032 RMS torque vs rated (0.147 N·m), copper loss | `TWIGLET_XML=twiglet_v3_v334_wig344.xml TWIGLET_RESULTS=results/v334_wig344/results_v3.json python arm_heat.py v3` | ✅ shoulder RMS/rated: **0.87× at 0.5 Hz**, 1.04× at 0.8 Hz, 1.70× at 1.5 Hz (v3 record: 0.99× at 0.8 Hz, 1.63× at 1.5 Hz → "cap continuous waving at ~0.6 Hz"; on v3.34 the cap should be ~0.5 Hz) | RMS ≤ 1.0× rated for continuous waving |
| 12 | head+arm diagnosis (`diag_e.py`) | test (e) alone with searched or fixed balance gains | `python diag_e.py v3 [g1,g2,g3,g4,g5]` | rev B1/C records in `history/body-v3.30/simC/` | as 4 |
| 13 | walk video (`walk_video.py`) | renders the gait to GIF/MP4 + torque traces (needs an OpenGL backend) | `MUJOCO_GL=egl python walk_video.py v3 [--eff]` | old videos (v2–v3.2) in `history/`; none for v3.3x | – |
| 14 | body version sweep | the same sims on every body v3.20–v3.34 model | `./run_all.sh twiglet_v3_body_v325.xml v325` etc. | per-version table: [`history/sim_history.md`](history/sim_history.md) | as 1–6 |
| 15 | head/wig infill sweep (simC) | head v3.30 variants (head330 / rd / trim / trimF) × wig infill 0–6 %: head mass vs e-margin and head-pitch load | `./run_all.sh twiglet_v3_head330rd_0.045.xml rd045` etc. | rd: infill 0 → 6 %: head 0.781 → 0.826 kg, e-margin 33.5 → 32.1 mm, head pitch 0.777 → 0.825 N·m (`history/body-v3.30/simC/sweepR2.txt`); 4.5 % chosen | all pass 1–6; head-pitch hold ≥ 2× |
| 16 | hair series | wig candidates s16 … y2 (v3.34–v3.40), c14 (v3.44) on the hair base body | `./run_all.sh hair_c14_v344.xml c14` etc. | c14 (= v3.44): pitch 2.151× hold on the hair base body (186.2 g wig); y2 (= v3.40): margin 33.4, standing 46.5, pitch 2.13× (`history/hair-v3.40/STATUS.md`) | pitch ≥ 2.0×, no falls |
| 17 | studies | neck 40 mm shorter (+ legs), no arms / arms only | `./run_all.sh twiglet_v3_opt_neck40_leg40.xml n40l40` etc. | v3.32 records: opt_neck40 main 13/20; neck40_leg40 20/20; s_noarm 19/20; s_armonly 18/20 | informative |
| 18 | mass / moment (`tools/mass_v334.py`, `tools/make_v334_wig.py`) | link masses and inertias from the meshes + densities; wig head inertial | `python tools/make_v334_wig.py` (runs; `mass_v334.py` is provenance only) | 2.753 kg total, head 0.814 kg (wig 186.2 g at 4.5 % infill) | head pitch hold ≥ 2× |
| 19 | 315-pose head range (`twiglet_geom/head_range.py` part 2) | head pitch × yaw × roll grid (7×9×5) vs trunk and arms | `python head_range.py` (3.5 min) | ✅ **154/315** poses with a contact (= v3.33h/v3.34 record), wig contact 32, wig-only **0** (wig v3.44) | ≤ ~154/315 and wig-only 0 |
| 20 | wig vs arms (`head_range.py` part 1) | wig vs both arms over the arm grid at head yaw 0/−45/+45 | same run | ✅ raw 3/27/35, **0/0/0 inside the arm soft limits** | 0 inside the soft limits |
| 21 | eye coverage (`twiglet_geom/eye_cover.py`) | wig triangles in front of the eye openings | `python eye_cover.py` | ✅ L/R **0/0** | 0/0 |
| 22 | arm sweeps (`twiglet_geom/arm_sweep.py`) | arms vs shells, kilt, leaves, head (162 poses) + per-joint sweeps | `python arm_sweep.py` | ✅ 0/0/0; elbow and gripper 0; shoulder 1 hit only at −10° (outside the −5° soft limit) | 0 inside the soft limits |
| 23 | kilt swing (`twiglet_geom/kilt_swing.py`) | kilt petals vs legs and arms over the shipped gaits + random poses | `python kilt_swing.py [--fast]` | ✅ sim gaits **0/1500** (leg 0, arm 0), stance **0/14**; single-leg 12/120, both legs 1/120, arms+legs 1/80, all front petals 00–02 vs a foot (= the v3.34b record) | sim gaits 0; random-pose hits only at extreme angles (free-swinging petals) |
| 24 | print-file check (`twiglet_geom/print_check.py`) | every STL in `print/mods/Twiglet`: watertight, 1 body, P1S fit, wall survey | `python print_check.py [subfolder]` | ✅ **61/61 pass** (50 body + 10 head + wig) | watertight, 1 body, fits 256³ |
| 25 | assembly renders (`twiglet_geom/render_assembly.py`) | the 26 step images of [docs/assembly_guide.md](../docs/assembly_guide.md) | `python render_assembly.py [step]` (15 s) | ✅ 26 PNGs in `docs/images/assembly/` | – |

