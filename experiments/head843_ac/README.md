# Head 843 manoeuvre tests

Simulation only. The early-rate walking file is not replaced.

`params/head843_earlyrate.npy` sha256 `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`.

Three heading laws are in this folder. Each qualification names the `sim/manoeuvre.py` hash that produced it. The current file is the onset right-stance flip, `98facc7220b9fb69d51599943f2a818f65ace2ce5fa669366e98f468690e8bd5`. cfg_c was `cf5fe2037cbcc2a94c40f3203b6c131248ddad50c7bb68cfd7f92894e1b20202`. cfg_b was `50db0a024acbd66fc1bc6faac621ba126a5ab22823be64aee810f71c8d5cb898`. Meshes are the existing files in `experiments/twiglet_sim/models/meshes`, linked from `sim/models/meshes`. Nothing here has been run on hardware, and a finished trial is not evidence that a part will not break.

## cfg_d, onset right-stance flip

Preregistered 2026-11-08T07:47:28Z in `results/head843_manoeuvre_d_prereg.json`. The cfg_c handoff stays. For the first 0.40 s after the command rate rises through 2°/s, a phase-selected right hip whose sole has more than 55% of the sole load gets the opposite sign. After that the sign matches cfg_c. Gains are not reduced. Holding the flip for the whole slew was measured on seeds 263000–263263 and dropped: fresh 90° finishes went 20–30° short.

| Command | Seeds | Task | Wilson 95% lower | Bar |
|---|---|---:|---:|---|
| +20° at 4°/s | 265000–265999 | 1000/1000 | 99.62% | met |
| −20° at 4°/s | 266000–266999 | 1000/1000 | 99.62% | met |
| +45° at 15°/s | 267000–267999 | 1000/1000 | 99.62% | met |
| −45° at 15°/s | 268000–268999 | 999/1000 | 99.44% | not met |
| +90° at 15°/s | 269000–269999 | 998/1000 | 99.27% | not met |
| −90° at 15°/s | 270000–270999 | 995/1000 | 98.84% | not met |
| Slalom on this law | 271000–271999 | 997/1000 | 99.12% | not met |

The −45° miss is a pitch fall at 9.54 s, minimum pitch −44.4°. The 90° misses are mostly shorts (finals +63°, +72°, −74°, −72°, −44°), plus one pitch fall and one opposite peak of 16.0°. The slalom misses are three pitch falls. Straight, no schedule, seeds 272000–272199: 200/200, Wilson lower 98.12%. Yaw median −2.1°. Shoulder mean 20.9°, shoulder travel 17.7°, head yaw travel 15.8°.

Half-turns were not in this sample. Seeds 258189, 259341, and 259556 still fall near −43° of pitch on this law, and the same seeds walk those horizons straight. Restart and stride ×1.3 do not set a heading schedule, so this alloc does not run on them.

## cfg_c, timed handoff

Preregistered 2026-11-08T07:07:35Z. Hash above. These counts are not retaken and are not pooled with cfg_d.

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

The negative-turn misses on this law finish near the command and fail an opposite peak of 15.0–17.6°, about 0.3 s after the slew starts.

## cfg_b, still the record for slalom, stop, and the slow stride

Preregistered 2026-11-08T06:27:18Z. Config hash `2f8ba5c261624f6c7526a7f12f9231687924070cc64bc2f1b6edc55d7cd936ab`.

| Command | Seeds | Task | Wilson 95% | Bar |
|---|---|---:|---|---|
| Slalom ±20° at 4°/s | 244000–244999 | 1000/1000 | 99.62% to 100% | met |
| Stop at 6 s, baseline 1 s start | 245000–245999 | 1000/1000 | 99.62% to 100% | met |
| Stride ×0.7 | 247000–247999 | 1000/1000 | 99.62% to 100% | met |

The stop and the ×0.7 stride were also 100/100 on the 0.82258 kg and 0.88458 kg heads. That bound’s Wilson lower bound is 96.3%. cfg_b’s own turns, restart, and stride ×1.3 missed 99.5%. Stride ×1.3 still fails seeds 248518 and 248767 at +20.5° and +21.0° of yaw.

## Earlier score, not recounted

`results/head843_manoeuvre_fix_val.json` holds the −180° block at 21/40 under the sign rule written for that run.

## Run

From `experiments/head843_ac/sim`:

```bash
python3 run_head843_manoeuvre_d_val.py
```

The script refuses to start if `sim/manoeuvre.py`, `params/head843_manoeuvre_cfg_d.json`, or the early-rate file no longer matches the preregistration. It resumes from `results/head843_manoeuvre_d_val.json` if that file is already present. The cfg_b and cfg_c logs in this folder are completed samples. Reproducing them means checking out the commit that recorded their manoeuvre hash.
