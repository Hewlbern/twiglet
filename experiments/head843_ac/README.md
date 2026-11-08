# Head 843 manoeuvre tests

Simulation only. The early-rate walking file is not replaced.

`params/head843_earlyrate.npy` sha256 `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`.

This folder is the later heading-schedule candidate. While a turn or a route is commanded, the slow-yaw integrator is frozen and a stance-hip term (gain 0.45, clip 0.08 rad) is added to the 0.20 rad per rad/s feedforward. A straight walk does not set that schedule. Meshes are the existing files in `experiments/twiglet_sim/models/meshes`, linked from `sim/models/meshes`. Nothing here has been run on hardware, and a finished trial is not evidence that a part will not break.

## What cleared a 99.5% bar

Preregistered 2026-11-08T06:27:18Z in `results/head843_manoeuvre_b_prereg.json`. Task success means upright and inside the command rule. Each line is its own seeds. A perfect 1000 has a Wilson 95% lower bound of 99.62%.

| Command | Seeds | Task | Wilson 95% | Bar |
|---|---|---:|---|---|
| Slalom ±20° at 4°/s | 244000–244999 | 1000/1000 | 99.62% to 100% | met |
| Stop at 6 s, baseline 1 s start | 245000–245999 | 1000/1000 | 99.62% to 100% | met |
| Stride ×0.7 | 247000–247999 | 1000/1000 | 99.62% to 100% | met |

The stop and the ×0.7 stride were also 100/100 on the 0.82258 kg and 0.88458 kg heads. That bound’s Wilson lower bound is 96.3%. It is not a 99.5% mass claim.

## What did not

| Command | Task | Wilson lower |
|---|---:|---:|
| +20° and −20° arcs at 4°/s | 997/1000 each | 99.12% |
| +45° at 15°/s | 999/1000 | 99.44% |
| −45°, +90°, −180° at the declared rates | 991/1000 each | 98.30% |
| −90° at 15°/s | 994/1000 | 98.70% |
| +180° at 10°/s | 993/1000 | 98.56% |
| Restart | 998/1000 | 99.27% |
| Stride ×1.3 | 998/1000 | 99.27% |

Many heading misses end near the command and fail because the unwrapped yaw went about 15–21° the wrong way before the turn. A few finish short. A few fall near −43° of pitch. The two restart misses stopped and started and finished at −17° and −29° of yaw. The two fast-stride misses walked at about 0.13 m/s and finished just past 20° of yaw.

Straight regression, no schedule: 200/200 at 10 s (Wilson lower 98.12%) and 80/80 at 20 s (Wilson lower 95.42%). Those samples are too small for a 99.5% claim. Yaw medians were −1.9° and −2.3°.

## Earlier score, not recounted

`results/head843_manoeuvre_fix_prereg.json` and `results/head843_manoeuvre_fix_val.json` are the previous candidate. Its −180° block is 21/40 under the sign rule written for that run. A wrapped half-turn failed that sign clause. This folder does not change that score.

## Run the fixed test

From `experiments/head843_ac/sim`, with the prereg file left as it is:

```bash
python3 run_head843_manoeuvre_b_val.py
```

The script refuses to start if `sim/manoeuvre.py` no longer matches the hash in the preregistration. It resumes from `results/head843_manoeuvre_b_val.json` if that file is already present, so move the committed log aside before a clean rerun.
