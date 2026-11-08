# Head 843 manoeuvre tests

Simulation only. The early-rate walking file is not replaced.

`params/head843_earlyrate.npy` sha256 `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`.

Two heading laws are in this folder. Each qualification names the `sim/manoeuvre.py` hash that produced it. The current file is the timed handoff, `cf5fe2037cbcc2a94c40f3203b6c131248ddad50c7bb68cfd7f92894e1b20202`. cfg_b’s scores were produced by `50db0a024acbd66fc1bc6faac621ba126a5ab22823be64aee810f71c8d5cb898`, which is the parent of this commit. Meshes are the existing files in `experiments/twiglet_sim/models/meshes`, linked from `sim/models/meshes`. Nothing here has been run on hardware, and a finished trial is not evidence that a part will not break.

## cfg_c, timed handoff

Preregistered 2026-11-08T07:07:35Z in `results/head843_manoeuvre_c_prereg.json`. The reset integrator runs until the heading command exceeds 2°/s, then stays frozen until the error is back under 6°. Stance gain 0.45 and feedforward 0.20 are unchanged. The 180° command in this file is 6°/s from 2 s to 32 s, episode 36 s. That rate was declared before the sample. The pass rule is the same whole-trace 15° rule as cfg_b.

| Command | Seeds | Task | Wilson 95% lower | Bar |
|---|---|---:|---:|---|
| +20° at 4°/s | 252000–252999 | 1000/1000 | 99.62% | met |
| +45° at 15°/s | 254000–254999 | 1000/1000 | 99.62% | met |
| −20° at 4°/s | 253000–253999 | 984/1000 | 97.42% | not met |
| −45° at 15°/s | 255000–255999 | 990/1000 | 98.17% | not met |
| +90° at 15°/s | 256000–256999 | 998/1000 | 99.27% | not met |
| −90° at 15°/s | 257000–257999 | 989/1000 | 98.04% | not met |
| +180° at 6°/s | 258000–258999 | 999/1000 | 99.44% | not met |
| −180° at 6°/s | 259000–259999 | 996/1000 | 98.98% | not met |
| Restart | 260000–260999 | 998/1000 | 99.27% | not met |
| Slalom on this law | 261000–261999 | 997/1000 | 99.12% | not met |

Straight, no schedule, seeds 262000–262199: 200/200. Wilson lower bound 98.12%. That sample is a regression, and the early-rate 4000-seed qualifications stay the walking claim. Yaw median −2.6°. Shoulder mean 20.9°, shoulder travel 17.8°, head yaw travel 15.8°.

The negative-turn misses finish near the command. The opposite unwrapped peak is 15.0–17.6°, and it occurs about 0.3 s after the slew starts. The same seeds walked straight peak near +11° to +13°. The first right-hip step of the slew adds the rest. Reversing that hip’s sign reversed the turn. Scaling it down enough to clear 15° also dropped a 90° finish from about 80° to about 38°, so this law keeps the full right-hip command. The 90° and 180° misses that are not that peak are pitch falls near −42° to −45°, plus one +90° that finished at +59°.

## cfg_b, still the record for slalom, stop, and the slow stride

Preregistered 2026-11-08T06:27:18Z in `results/head843_manoeuvre_b_prereg.json`. Config hash `2f8ba5c261624f6c7526a7f12f9231687924070cc64bc2f1b6edc55d7cd936ab`. Those counts are not retaken.

| Command | Seeds | Task | Wilson 95% | Bar |
|---|---|---:|---|---|
| Slalom ±20° at 4°/s | 244000–244999 | 1000/1000 | 99.62% to 100% | met |
| Stop at 6 s, baseline 1 s start | 245000–245999 | 1000/1000 | 99.62% to 100% | met |
| Stride ×0.7 | 247000–247999 | 1000/1000 | 99.62% to 100% | met |

The stop and the ×0.7 stride were also 100/100 on the 0.82258 kg and 0.88458 kg heads. That bound’s Wilson lower bound is 96.3%. It is a mass screen, and the 99.5% claim stays on the nominal 1000. cfg_b’s own turns, restart, and stride ×1.3 missed 99.5%. Stride ×1.3 still fails seeds 248518 and 248767 at +20.5° and +21.0° of yaw, because that path has no heading schedule and this edit does not change it.

## Earlier score, not recounted

`results/head843_manoeuvre_fix_prereg.json` and `results/head843_manoeuvre_fix_val.json` are the previous candidate. Its −180° block is 21/40 under the sign rule written for that run. A wrapped half-turn failed that sign clause. This folder does not change that score.

## Run

From `experiments/head843_ac/sim`:

```bash
python3 run_head843_manoeuvre_c_val.py
```

The script refuses to start if `sim/manoeuvre.py`, `params/head843_manoeuvre_cfg_c.json`, or the early-rate file no longer matches the preregistration. It resumes from `results/head843_manoeuvre_c_val.json` if that file is already present. `run_head843_manoeuvre_b_val.py` now refuses as well, because the working `manoeuvre.py` is the handoff law. The cfg_b log in this folder is the completed sample. Reproducing it means checking out the commit that recorded hash `50db0a02`.
