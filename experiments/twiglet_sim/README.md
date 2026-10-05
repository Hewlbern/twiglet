# twiglet_sim: MuJoCo sims for the Twiglet robot

The default model is `models/twiglet_v3_v334_wig344.xml`: body v3.34 + head v3.30 + wig v3.44 (c14). It has 19 actuators (10 legs STS3215, 3 head STS3215, 6 arms STS3032) and weighs 2.753 kg, with the head at 0.814 kg. All sims run from this folder with plain relative paths.

```bash
pip install mujoco numpy
python run_tests.py v3                 # (a) standing, (b) push, (c) weight shift, (e) head + arm motion -> out/results_v3.json
python walk_eval.py v3                 # main gait, nominal + 20 randomized trials -> out/walk_v3.json
python walk_eval.py v3 --eff           # efficient gait -> out/walk_v3_eff.json
python walk_heldout.py v3 walk_v3_best.npy mytag   # held-out seeds 6000-6019 -> line in out/sim_summary.txt
./run_all.sh twiglet_v3_v334.xml v334     # tests + both gaits on any model in models/, logs in out/v334/
```

## Environment variables

| var | default | what |
|---|---|---|
| `TWIGLET_XML` | `twiglet_v3_v334_wig344.xml` | the model: a file name in `models/` or a path |
| `TWIGLET_OUT` | `out/` | where outputs go (gitignored). `run_all.sh` sets `out/<tag>` |
| `TWIGLET_PARAMS` / `TWIGLET_PARAMS_EFF` | `walk_v3_best.npy` / `walk_v3_eff_best.npy` | gait params: a file name in `params/` or a path |
| `TWIGLET_RESULTS` | `$TWIGLET_OUT/results_v3.json` | balance gains for `arm_heat.py` (from `run_tests.py`) |
| `PYTHON` | `python3` | interpreter used by `run_all.sh` |

No script writes into `models/`, `params/` or `results/`, and `run_all.sh` no longer copies the model anywhere. The old `twiglet_v3.xml` symlink is gone, so a run can no longer overwrite the model in `mini_bdx/robots/twiglet_v334/`.

## Files

| file | what |
|---|---|
| `simlib.py`, `episode.py` | model loading (`TWIGLET_XML`), STS3215/STS3032 servo models, soft joint limits, gait generator, balance feedback, metrics, episode runner |
| `run_tests.py` | (a) standing / COM window, (b) push recovery, (c) weight shift + single support, (e) head + arm motion (min support margin, peak torques incl. head pitch) |
| `walk_search.py` | gait parameterisation (12 params: `f, stride, lift, sway, sway_ph, crouch, lean, kp_pitch, kd_pitch, kp_roll, kd_roll, ank_off`), random search + CEM, robustness check |
| `walk_eval.py [--eff]` | nominal + 20 randomized 10 s walks (mass ±10 %, friction 0.6–1.0, armature, latency) |
| `walk_refine.py [--eff]` | local refine for a new body (24 perturbations × 10 seeds); writes `out/*_refined.npy`, never the shipped params |
| `walk_heldout.py` | 20 held-out seeds (6000–6019) |
| `arm_heat.py` | 30 s continuous arm waving at 0.5 / 0.8 / 1.5 Hz: RMS torque vs rated, copper loss |
| `diag_e.py` | test (e) alone with searched or fixed balance gains |
| `walk_video.py [--eff]` | GIF/MP4 + torque traces (needs an OpenGL backend, e.g. `MUJOCO_GL=egl`) |
| `quick_static.py` | quick standing check |
| `run_all.sh <model> <tag> [params] [params_eff]` | run_tests + both gaits; one summary line per run in `out/sim_summary.txt` |
| `walk_v3_best.npy` | main gait = `params/walk_v3_best_v334r1.npy` (v3.34 refine s35) |
| `walk_v3_eff_best.npy` | efficient gait = `params/walk_v3_eff_best_v333r1.npy` |
| `tools/` | `make_v334_wig.py` rebuilds the current model from `models/twiglet_v3_v334.xml` + the head inertial and collision box of a hair-series model (default `hair_c14_v344.xml` = wig v3.44; runs from the repo). Provenance only, because they need the original build workspace: `gen_mjcf_v3.py` (MJCF generator), `mass_v334.py` (mass/inertia from the meshes), `make_xml_variant.py` |

## models/ (52 MJCF files, all load, nu = 19)

`models/meshes` is a symlink to `../../../mini_bdx/robots/twiglet_v334/meshes`. The meshes are visual only and are the same for v3.32–v3.34. Contact is only the floor plane vs 4 boxes (trunk, both feet, head), so self-collision between parts is not simulated here; that is what `../twiglet_geom/` checks.

| group | files | what |
|---|---|---|
| current | `twiglet_v3_v334_wig344.xml` | body v3.34 + head v3.30 + wig v3.44 c14 (2.753 kg) |
| previous | `twiglet_v3_v334_wig340.xml` | the same with wig v3.40 (2.743 kg) |
| body versions | `twiglet_v3_body_v320.xml` … `twiglet_v3_body_v329.xml`, `twiglet_v3_v331c_head330.xml`, `twiglet_v3_v332.xml`, `twiglet_v3_v333.xml`, `twiglet_v3_v333g.xml`, `twiglet_v3_v334.xml` | each released body (v3.34 = 2.753 kg with the old fringe) |
| head/wig infill sweep (simC) | `twiglet_v3_head330{,rd,trim,trimF}_{0.0,0.02,0.03,0.045,0.06}.xml` | head v3.30 variants × wig infill; `head330rd_0.045` is the hair base and equals `v331c_head330` |
| rev studies | `twiglet_v3_revB1.xml`, `twiglet_v3_revC.xml`, `twiglet_v3_revC2.xml` | the v3.31 arm/body revisions |
| studies | `twiglet_v3_opt_neck40*.xml`, `twiglet_v3_s_armonly.xml`, `twiglet_v3_s_noarm.xml` | neck 40 mm shorter (+ legs); arm sensitivity |
| hair series | `hair_s16_v334.xml`, `hair_t15_v335.xml`, `hair_u5_v336.xml`, `hair_v6_v337.xml`, `hair_w9_v338.xml`, `hair_x5_v339.xml`, `hair_y2_v340.xml`, `hair_c14_v344.xml` | each wig candidate on the hair base body; y2 = wig v3.40, c14 = wig v3.44 |

## params/ (22 gait files)

`params/MANIFEST.json` lists every file's 12 values and where it came from. Current: `walk_v3_best_v334r1.npy` (= refine s35), `walk_v3_eff_best_v333r1.npy`. Also the v3.34 refine candidates s34 / s36, v333r1, v332r1/r2, v39, rev C, the v3.1 search results and the `*cur` snapshots.

## results/

| folder | what |
|---|---|
| `v334_wig344/` | ✅ re-run from this repo on 5 Oct 2026 with the current model (wig v3.44): `results_v3.json`, `walk_v3*.json`, logs, `heldout_v334r1.log`, `arm_heat_v3.json` |
| `v334_wig340/` | ✅ the previous model (wig v3.40), 4 Oct 2026: `results_v3.json`, `walk_v3*.json`, logs, `heldout_v334r1.log`, `arm_heat_v3.json` |
| `v334_repo/` | ✅ re-run from this repo of the v3.34 body (old fringe): reproduces the v3.34 record exactly |
| `sim_summary_repo_runs.txt` | the summary lines of those runs |
| `record_v334_r2/` | the original v3.34 record (r2 run, refine s34/s35/s36, held-out lines) |

| result | v3.34 record | v3.34 re-run here | v3.34 + wig v3.40 | v3.34 + wig v3.44 (current) |
|---|---|---|---|---|
| standing margin | 50.8 mm | 50.8 mm | 50.5 mm | 50.5 mm |
| e-margin (head + arm motion) | 34.0 mm | 34.0 mm | 34.4 mm | **34.1 mm** |
| head-pitch peak | 0.808 N·m (2.36× stall) | 0.808 | 0.796 N·m (2.40×) | **0.796 N·m (2.40×)** |
| head-pitch static hold (`quick_static.py`) | – | – | 0.2345 N·m (2.09× of 0.49) | **0.2323 N·m (2.11×)** |
| main gait, 20 randomized | 20/20, 0.208 m/s | 20/20, 0.208 | 20/20, 0.210 | **19/20, 0.206** |
| efficient gait | 20/20, 0.156 m/s | 20/20, 0.156 | 20/20, 0.156 | **20/20, 0.156** |
| held-out 6000–6019 | 19/20, 0.207 m/s | – | 19/20, 0.202 | **18/20, 0.206** |
| arm waving, shoulder RMS/rated | – | – | 0.87× / 1.04× / 1.70× | 0.87× at 0.5 Hz, 1.04× at 0.8 Hz, 1.70× at 1.5 Hz (identical) |

The older versions are in [`../history/sim_history.md`](../history/sim_history.md).
