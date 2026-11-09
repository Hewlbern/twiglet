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

A later diagnosis did not replace this law. Dropping the yaw command while the pitch catch is on left the falls in place and made the 90° shorts worse, so that edit was reverted and the hash above is unchanged. The onset flip is what lets seed 253015 pass a −20°, and it is also what makes seed 268632 fall on a −45° the plain handoff completes. The 15°/s shorts sit on the ±0.10 rad hip-yaw clip with pitch near ±2° and a body rate of about 8–10°/s. At a declared 8°/s (2.5–13.75 s, episode 17.25 s) those shorts finish, seed 270260 still falls at 3.7 s, and seed 270924 still peaks 16° the wrong way. Fresh seeds 275000–275095 were 48/48 each way. That is a development screen, not a qualification. Restart seed 260842 reaches −27° at 10.8 s with hip yaw still near ±0.03 rad on that hash. Fast-stride seed 248518 still ends at +20.3° with the ±0.02 rad trim at its clip on 55% of samples.

## cfg_e, step guard and a later-cycle trim

Law `e13cd9c1ef2f529f3d4401626ef819b7e44df8c9358788879bacb48cf4228887`. After a heading move, a touchdown longer than 0.045 m shortens the next swing. The later restart cycle, and stride above 1, use a 0.04 rad yaw trim. Straight walks take neither path. Seed 268632 then completes the −45°, and two of the three recorded slalom falls stay upright. Seed 271181 still falls at 13.9 s. The 15°/s 90° shorts are unchanged. Fresh screens were diagnostic: −45° 47/48, slalom 48/48, ±90° 32/32, fast stride 47/48 with one yaw of +26°.

The preregistered restart block, seeds 277000–277999, is 999/1000. Wilson lower bound 99.44%. It does not clear 99.5%. The miss is seed 277378 at −15.27° of yaw, upright, with the stop and the second walk intact. Straight seeds 278000–278199 are 200/200. No mass block was run. cfg_d’s ±20° and +45° counts stay on hash `98facc72…`.

The run36 paired straight walks did not fall. Replayed here, seeds 253059, 258189, and 261613 stay upright. Seed 270260 was not in that set. It falls at 4.33 s when walked straight, at 10 s and at 12 s, and it also falls on the −90° command. That straight-walk fall is a different seed, not a change to the earlier logs.

## cfg_f, later-cycle integral reset

Law `08e856e0a1913a601c7f679d3ca639038d5ca10b52a8d7786176c424e21217dc`. At the edge of a restart’s later cycle the slow-yaw integral is set to zero once. On seed 277378 the hips were still the sign of the first walk while yaw ran to −24°. The preregistered block, seeds 280000–280999, is 1000/1000, Wilson lower 99.62%. Yaw on that thousand runs from −14.3° to +10.9°. The 0.82258 kg and 0.88458 kg heads are each 100/100, Wilson lower 96.30%, which is not a 99.5% mass claim. Straight seeds 281000–281199 are 200/200. cfg_e’s 999/1000 stays on its own hash. Seed 271181 still falls on that hash. Seed 276309 still finishes a ×1.3 stride at +26°. A 15°/s 90° command is still faster than the 8–10°/s measured with hip yaw at its clip.

Shortening the swing by 0.02 rad while a heading command is moving keeps the recorded slalom falls upright and cuts a declared 8°/s +90° (2.5–13.75 s, episode 17.25 s) to about +18° and +34°. At 0.01 rad, seed 271339 falls again and those +90° seeds reach about +50°. That bias was not kept. The law hash above is unchanged. Stride ×1.3 remains outside the qualified envelope because of seed 276309.

A continuous 4°/s chain of 20° arcs, with a declared 2 s hold between arcs and no pose reset, was scored on the same whole-trace rule. Several recorded −90° misses then finish, and the slalom fall seeds stay upright. Seed 269829 falls at 4.9 s during the first +20° arc; its straight walk does not. Seed 268632 reaches +19.2° the wrong way at 4.26 s during the first −20° arc, then finishes near −49°. Fresh seeds 282000–282063 were 16/16 on each profile. That screen is not a qualification, and no new thousand was opened. Hip yaw, clipped at 0.10 rad, is the only heading degree of freedom and tops out near 8–10°/s. Hip pitch is both the step length and the pitch catch.

## cfg_g, stance hip-roll support

Law `2ee3faeaab624dce936ac790b924bf1ba5e38ae456072d857a2bdc7ce8f3c4fe`. Knee and ankle already reach about ±1.91 N·m in a normal straight step, so they were not given the pitch catch. Hip roll still had torque left. A −0.08 rad command on the loaded hip, only while pitch is below −0.10 rad and still falling, kept seeds 271181 and 271339 upright. The opposite sign made 271339 fall. The preregistered slalom, seeds 284000–284999, is 999/1000, Wilson lower 99.44%. The miss is seed 284200, upright, at −1.8° where the target is −20°. No falls. Straight seeds 285000–285199 are 200/200. cfg_f’s restart thousand stays on its own hash. Seed 270924 still peaks 16.1° the wrong way on an 8°/s −90°. Seed 276309 still finishes stride ×1.3 at +26°.

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
