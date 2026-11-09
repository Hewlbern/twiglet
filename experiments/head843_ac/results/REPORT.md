# Twiglet AC motion study — simulation only

Scratch copy of the 7 November 2026 machine-local snapshot. No commit, push, pull request, merge, gait promotion, hardware command, or edit to keeper geometry. `params/reliable.npy`, `params/fast.npy`, `params/efficient.npy`, `sim/models/twiglet_v3_v335ac.xml`, and `geometry/scene_v335ac.npz` match the snapshot hashes.

Reliable `retune_ac_v6b0` stays the preferred candidate. Nothing in this study replaces it. `fast_f05` was not retuned. There is no calibrated thermal or battery model, so this report has no temperature or runtime.

## Baseline reproduction

Same evaluator as `walk_search.evaluate`: randomized 10 s, mass ±10%, friction 0.6–1.0, armature and damping ±30%, latency 0–5 steps of 2 ms, backlash 0.4°. The new flat rollout matches that evaluator on seeds 0, 5000, and 16058 (position to 1e-6 m, same fall).

| Check | Result | Published |
|---|---|---|
| reliable 5000–5199 | 200/200 at 0.2108 m/s, falls none | matches the handoff counts and, for reliable, the stored speeds |
| reliable 16000–16199 | 199/200 at 0.2101 m/s, falls [16058] | matches the handoff counts and, for reliable, the stored speeds |
| fast 16000–16199 | 197/200 at 0.2156 m/s, falls [16058, 16093, 16110] | matches the handoff counts and, for reliable, the stored speeds |
| reliable 19000–19199 | 199/200 at 0.2095 m/s, fall [19092] | identical to `reports/fresh19000.json` |
| reliable load window 5000–5019 | main RMS 0.9981 N·m, saturation 6.607%, speed 0.2125 m/s, current proxy 10.276 A | published 0.9981 N·m, 6.607%, 0.2125 m/s, 10.276 A |

Saturation is the fraction of 0.01 s samples with |torque| ≥ 1.90 N·m on the STS3215 joints. Current is `Recorder.current`, a datasheet idle-to-stall map, not a measured amp. Every main joint (hip pitch, knee, ankle, both sides) still reaches the 1.91 N·m stall on the fresh flat set.

## Fresh flat reliable gait

Seeds 28000–28199 were not used to choose any parameter. Reliable: **200/200**, speed **0.2100 m/s**, main RMS **0.977 N·m**, main saturation **5.76%**, leg RMS 0.678 N·m, current proxy 10.09 A. Load means use survivors only. Falls: none.

| Joint | RMS N·m | mean peak N·m | max peak N·m | saturation |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.064 | 0.302 | 0.404 | 0.00% |
| left_hip_roll | 0.389 | 0.964 | 1.371 | 0.00% |
| left_hip_pitch | 1.021 | 1.895 | 1.910 | 2.64% |
| left_knee | 0.848 | 1.910 | 1.910 | 5.02% |
| left_ankle | 1.059 | 1.910 | 1.910 | 9.51% |
| right_hip_yaw | 0.066 | 0.281 | 0.352 | 0.00% |
| right_hip_roll | 0.393 | 0.962 | 1.286 | 0.00% |
| right_hip_pitch | 1.020 | 1.896 | 1.910 | 2.62% |
| right_knee | 0.853 | 1.910 | 1.910 | 5.02% |
| right_ankle | 1.064 | 1.910 | 1.910 | 9.77% |

## Load screen

Tune seeds 22000–22019, chosen before scoring. A perturbation is accepted on that set only if survival is at least reliable’s, speed is at least 97% of reliable, and either main RMS drops 2% or main saturation drops 10% relative. Held-out seeds are not an input.

| Candidate | Tune survival | Speed m/s | Main RMS | Main sat |
|---|---:|---:|---:|---:|
| reliable | 20/20 | 0.207 | 0.971 | 5.39% |
| stride097 | 20/20 | 0.203 | 0.966 | 5.13% |
| f097 | 20/20 | 0.207 | 0.956 | 4.90% |
| f_stride097 | 20/20 | 0.203 | 0.951 | 4.73% |
| sway097 | 20/20 | 0.205 | 0.972 | 5.46% |
| lift098 | 20/20 | 0.209 | 0.966 | 5.16% |
| kp_pitch090 | 20/20 | 0.209 | 0.970 | 5.32% |
| ank_off_plus_0.01 | 20/20 | 0.207 | 0.972 | 5.43% |

`f_stride097` (frequency and stride ×0.97) passed the tune saturation gate. On held-out 27000–27199 it is **198/200** (falls 27072, 27128) at 0.203 m/s, main RMS 0.960 N·m, saturation 5.16%. Reliable on the same seeds is **200/200** at 0.210 m/s, main RMS 0.978 N·m, saturation 5.79%. Both still peak at 1.91 N·m.

That misses the 199/200 reliability bar and gives up about 3.6% speed for about 1.8% RMS and about 11% relative saturation. It is not recommended and was not copied over `params/reliable.npy`. The vector is only `results/load_screen_candidate.npy`.

## Heading feedback

This is not `Gait.turn`. Hip yaw is `command_sign * (kp * heading_error - kd * yaw_rate)`, clipped to ±7°. A nominal +0.08 rad bias changed yaw by -10.0°, so `command_sign` is -1. Gyro axis aligns with yaw rate (`damp_align` +1). Gains were chosen on 21000–21023 for a +20° slew from 3.0 s to 5.5 s: highest survival, then lowest heading RMS, then smaller kp. **kp 0.6, kd 0.02** was 24/24 with RMS 5.03°.

| Trial | Seeds | Survival | Speed m/s | Heading RMS ° | Final error ° | Yaw change ° | In band after slew | Cross-track vs initial heading m |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| +20° feedback | 200 | 195 | 0.206 | 5.83 | 3.48 | 16.52 | 58% | 0.195 |
| −20° feedback | 40 | 40 | 0.208 | 9.99 | -5.38 | -14.62 | 24% | 0.137 |
| +10° feedback | 40 | 40 | 0.207 | 4.47 | 1.48 | 8.52 | 81% | 0.183 |
| hold 0° feedback | 40 | 40 | 0.209 | 4.90 | -0.42 | 0.42 | 66% | 0.160 |
| open loop, same 40 seeds | 40 | 40 | 0.206 | — | — | 13.42 | — | 0.224 |
| open-loop bias +0.05 rad | 40 | 40 | 0.212 | — | — | -11.70 | — | — |
| open-loop bias −0.05 rad | 40 | 38 | 0.189 | — | — | 36.57 | — | — |

+20° held-out is seeds 26000–26199: falls [26077, 26139, 26140, 26145, 26155]. Mean yaw change is +16.5° of the +20° command. About 5.7% of hip-yaw commands sit on the ±7° clip, so the miss is not a saturated yaw stop. After the slew, mean time to enter ±5° is 0.73 s among the 90% of survivors who enter it. Cross-track versus the commanded heading after the slew averages 0.097 m.

−20° on the first 40 of those seeds survives 40/40 but tracks worse (RMS 10.0°, final −5.4°, achieved −14.6°, in band 24%). The plant is not symmetric. +10° on those 40 seeds is 40/40, RMS 4.5°, final +1.5°, in band 81%.

Heading hold on 26000–26039 keeps final error at −0.4° and straight cross-track at 0.160 m. The same seeds with no yaw command drift +13.4° and 0.224 m cross-track, both 40/40. Feedback reduces drift. It does not make the path straight.

The ±0.05 rad rows are fixed `Gait.turn` biases. Positive bias yaws about −12° with no falls. Negative bias yaws about +37° and falls on 26032 and 26037. Those are not heading-tracking scores.

## Stop and start

Double-support is `sin(2π f t) = 0`, where both swing lifts are zero. The phase schedule used here hits that edge to 1e-15. The original 1 s ramp is unchanged when no schedule is attached.

Phase-aware start hold (command at 0.6 s, edge at 0.68 s) plus a stop at 6 s, seeds 23000–23019: **10/20**. Falls are at 2.8–5.5 s, before the stop edge, and the abrupt cut falls on the same seeds at the same times. The start hold is what fails. Survivors are already stopped: speed in the last settled window 0.59 mm/s (phase) and 1.70 mm/s (abrupt).

Same seeds with the original start ramp, then a stop: phase-aware stop **20/20**, speed before the stop 0.247 m/s, after settle 0.36 mm/s, travel after the edge 52 mm. Abrupt cut **20/20**, before 0.243 m/s, after 1.65 mm/s, travel after the cut 18 mm. The phase stop is slower to finish because amplitude takes one gait cycle to reach zero. Torque RMS on these episodes includes the stand and is not a walking-load improvement.

## Terrain

Fixtures are added in memory. The AC XML on disk is unchanged. Feet meet the new boxes only through the existing sole, trunk, and head collision boxes. Visual meshes do not collide.

| Fixture | Seeds 24000–24039 | Speed of survivors |
|---|---:|---:|
| flat control | 40/40 | 0.208 m/s |
| 4 mm bumps | 22/40 | 0.189 m/s |
| 6 mm ridge | 2/40 | 0.177 m/s |
| 2° grade, top edge on the floor, +30 mm over 0.85 m | 35/40 | 0.030 m/s |

An earlier grade left a curb about one box-thickness high. That run is discarded. The reported grade has its top front edge at z = 0 and the underside below the floor. Nominal unrandomized speed is 0.030 m/s against 0.211 m/s on flat ground. Main RMS on the grade survivors is 1.08 N·m, higher than flat, so the slowdown is not a load saving. This is sole-box contact on a rotated box, not a claim about the physical soles on a real slope. The 6 mm ridge survives 2/40. Two survivors are not a load result. The 4 mm bumps survive 22/40.

## Walking with head and arms

Leg targets stay on the reliable gait. Head and arm targets are added, then the existing soft clip runs. Seeds 25000–25039.

| Command | Survival | Speed |
|---|---:|---:|
| walk, head and arms at the stance default | 40/40 | 0.207 m/s |
| predeclared mild nod and arm wave | 5/40 | 0.173 m/s |
| standing head/arm script composed onto the walk | 0/40 | — m/s |
| post-hoc smaller wave, seeds 29000–29019 | 15/20 | 0.190 m/s |

The mild command falls on 35/40 around 2.3–3.0 s. The standing script falls on 40/40 around 1.6–2.0 s. Standing balance tests do not transfer. The smaller wave was chosen after that failure, so 29000–29019 is not a predeclared held-out. It still falls 5/20. Seeds 29020–29199 were not used. No walking head/arm command here is reliable enough to prefer.

On the five mild survivors, command-to-measured RMS is about 1.9° at the head pitch, 1.6° at head yaw, and 3.4° at the shoulders. That is tracking of the servos on the trials that stayed up, not evidence the motion is safe.

## Dynamic clearance

Joint angles are the simulated radians, converted to degrees, and applied with the scene forward kinematics. Samples are 25 Hz plus one linear joint midpoint. That is not a continuous swept volume. Link meshes are a 4500-face subset after quadric decimation failed to hit the cap. Dropped faces can hide a thin contact, so zero contacts is not a proof.

Scene source string: `body-v3.35d (hair v3.52 v400; Step D torso) | body-v3.35c (neck raise R 45.0 DX 0.0 rake 1.0) | body-v3.35 (scene_v334_wig344 + blender/out/asm swaps) | body-v3.34-body scene_for('v334_current') + wig print/mods/Twiglet/wig_v3.44/FINAL_WIG_model_frame.stl (40000 faces)`

Mesh names do not include F4, G3, D9, or wig v6b0. The head link is `head3_*` parts plus `head3_fringe`. The source string points the fringe at a v3.44 wig export and hair v3.52, not at a confirmed v6b0 wig. AC inertials are the XML (head assembly mass 0.81392 kg). Simulator STL visuals are the legacy set and were not used for this clearance. Fourteen `sim_*` visual copies embedded in the scene were excluded by name, and the 19 kinematic neighbor pairs were excluded because those parts meet at the joints. Both lists are in `results/clearance_dynamic.json`. No priority pair was already colliding on the first recorded pose.

Three trajectories, each 8 s: nominal walk, one randomized mild survivor, and the nominal post-hoc wave. New contacts after the exclusions: **none** in all three. Closest non-neighbor approach is about **6.6–6.8 mm**, right hip roll link versus the trunk. Head versus trunk stays about 58–64 mm. Head versus upper arms stays about 48 mm on the mild survivor and 56–65 mm on the walks with smaller arm motion. A centroid check of `head3_fringe` at head yaw 0° and 20° matches the AC XML body frame to 0.0 mm. That checks this mesh and this joint, not the locked face plates.

## Seeds

Burned, reproduction only: 5000, 6000, 7000, 8000, 9000, 11000–15000, 16000, 17000, 18000, 19000, each as a 200-seed block where a trial was run.

| Block | Role |
|---|---|
| 21000–21023 | heading gain tune |
| 22000–22019 | load-screen tune |
| 23000–23019 | stop/start tests, no fit |
| 24000–24039 | terrain, no fit |
| 25000–25039 | predeclared head/arm |
| 26000–26199 | heading held-out; paired variants use the first 40 |
| 27000–27199 | load held-out |
| 28000–28199 | fresh flat reliable |
| 29000–29019 | post-hoc smaller head/arm, after 25000 failed |
| 29020–29199 | reserved, not used |

## How to run

```
ROOT=<this package>
cd $ROOT/sim
export TWIGLET_XML=$ROOT/sim/models/twiglet_v3_v335ac.xml
export TWIGLET_PARAMS=$ROOT/params/reliable.npy
export TWIGLET_PARAMS_EFF=$ROOT/params/efficient.npy
export TWIGLET_SCENE=$ROOT/geometry/scene_v335ac.npz
export TWIGLET_OUT=$ROOT/results
python walk_eval.py v3
python run_capabilities.py
python run_followup.py
```

Python packages used: numpy 2.5.3, mujoco 3.14.0, trimesh 5.1.0, shapely 2.1.2, scipy 1.18.1, python-fcl 0.7.0.11, fast-simplification 0.2.0, matplotlib. `run_capabilities.py` reproduces the flat study. `run_followup.py` repeats the corrected grade, the baseline-start stops, the open-loop path metric, the post-hoc wave, and the clearance. Geometry helpers resolve `sim/` and `geometry/scene_v335ac.npz` instead of the old absolute machine paths. If a legacy v334 XML is actually present, those helpers still prefer it.

## What remains unsupported

- No self-collision in the MuJoCo plant. Floor contact is boxes, not the AC meshes.
- Heading tracking at ±20° is partial, and the two directions do not match.
- A phase-aware start from a stance hold is less reliable than the original ramp.
- Uneven terrain at these heights is not a solved gait.
- Walking head and arm motion is not reliable.
- Dynamic clearance does not verify F4, G3, D9, or wig v6b0, and it is not a continuous sweep.
- No thermal resistance, winding temperature, battery capacity, voltage sag, or BMS limit was available. None is inferred.
- The supported physical checklist in `reports/LOAD_REPORT.md` was not performed. This study does not command the robot.


## Improvement pass

Controllers are overlays. `params/reliable.npy` and the AC XML were not edited. The default flat path still matches `walk_search.evaluate` on seeds 0 and 5000. A fresh flat batch, seeds 36000–36199, is 199/200 at 0.2102 m/s (fall 36115).

### Walking head and arms

The previous mild wave, re-run on the same fresh seeds 33000–33039, survives 4/40. The new controller locks the arms and a small head motion to the gait phase and scales that motion with trunk tilt, never below 55% of the command. It was chosen on 30000–30031 only: highest survival, then, within one fall, the largest measured shoulder and head-yaw travel among commands that still move. The winner is `phase_imu_softpitch` (shoulders ±10°, head yaw ±8°, head pitch ±1.5° about −4°, IMU scale gain 3).

| Set | Survival | Speed | Shoulder peak-to-peak | Head yaw peak-to-peak | Main RMS | Yaw change |
|---|---:|---:|---:|---:|---:|---:|
| Train 30000–30031 | 22/32 | 0.165 m/s | 17.6° | 15.1° | 0.981 N·m | −31° |
| Fresh 33000–33039 | 26/40 | 0.177 m/s | 17.5° | 15.0° | 0.973 N·m | −30° |
| Reserved 29020–29059 | 31/40 | 0.175 m/s | 17.6° | 15.1° | 0.984 N·m | −31° |
| Old mild, same fresh seeds | 4/40 | 0.146 m/s | 14.4° | 35.9° | 0.979 N·m | +4° |
| Walk, arms still, same fresh seeds | 39/40 | 0.211 m/s | — | — | 0.973 N·m | +8° |

Measured travel matches the command at the observed gain of 0.87, so the motion is not a command the servos ignore. Main-joint RMS matches walking with the arms still. The current proxy rises from 10.1 A to 11.5 A because the arm and head channels are moving. Speed is about 0.18 m/s instead of 0.21 m/s. The gait also yaws about −30° in 10 s. Putting the heading integrator on top of this motion, seeds 38000–38019, survives 7/20 and still yaws −11°. That composition is worse and is not the candidate. A 2 N, 0.1 s lateral push at 4 s on 37000–37019 is survived 16/20 with the arms moving and 20/20 with the arms still. This is not a disturbance-recovery improvement.

### Start and stop

The motionless wait for double support is not a candidate. The replacement rises with a raised cosine from t = 0 over 1.2 s, with the gait phase shifted so a double-support edge is at mid-rise, then stops on the next double-support edge after 6 s. Train seeds 31000–31019 were 20/20 for 1.0, 1.2, and 1.5 s, so the predeclared tie break keeps 1.2 s. Held-out 34000–34039 is 36/40. Survivors are walking at 0.244 m/s before the stop and at 0.6 mm/s after it, and they coast 57 mm. Four falls remain. That is better than 10/20 for the wait, and it is not flat-walk reliability.

### Heading

An integral term was chosen on 32000–32023 for both +20° and −20°. ki = 0.4 won because it was the only gain at 24/24 on both signs. On fresh seeds 35000–35039, against ki = 0 on those same seeds:

| | +20° with ki | +20° without | −20° with ki | −20° without |
|---|---:|---:|---:|---:|
| Survival | 40/40 | 40/40 | 39/40 | 40/40 |
| Final error | −0.4° | +3.5° | +0.1° | −3.6° |
| Yaw change | +20.4° | +16.5° | −20.1° | −16.4° |
| RMS error | 5.8° | 5.6° | 7.8° | 8.6° |
| Fraction inside ±5° after the slew | 65% | 58% | 47% | 30% |

The integrator reaches the commanded angle on both signs. RMS during the slew is still larger for the negative turn (7.8° versus 5.8°), and that turn loses one seed (35020). Speed stays near 0.21 m/s and main RMS near 0.98 N·m.

### v6b0

The AC XML head mass is 0.81392 kg, which matches the mass cited for the v6b0 retune in `reports/VALIDATION.json`. The scene file’s own source string names hair v3.52 and a v3.44 wig path, not v6b0, F4, G3, or D9. Mesh identity of the locked face is not established. The keeper assembly was not simplified.

## Lateral tips and the 20 s yaw split

The five held-out falls on 53000–53199, and three confirmation falls, were replayed only to read the mechanism. They were not used to set a gain. Onset is about 2.5–3.0 s, with roll rate about 1–2 rad/s and then 3 rad/s. A later contact replay (below) shows that one sole at zero force is ordinary single support, not a stance foot that has unloaded. The abnormal part is the roll or pitch rate during that single-support interval. A pelvis shift toward the stance foot, tried in both directions on fresh train seeds, did not beat the current controller: 78/80 for the current mix on 57000–57079, 72–77/80 for the load shift, and 76–77/80 for the opposite sign on 57200–57279. The arm wave was held at the same size in every case.

The two 20 s averages are not two different behaviors. On seeds 55000–55039 the hip-yaw command is pinned at ±0.02 rad for a median 66% of the trial, the integral sits at the output limit, the median yaw is +18°, and 60% of trials exceed ±15° (range −24° to +65°). On seeds 56200–56239 the median yaw is −2°, but 38% of trials still exceed ±15° (range −47° to +76°) and the command is pinned for a median 72% of the trial. Raising the limit to 0.05 rad on that second block does not pull the average in. The ±1.1° hip-yaw trim spends most of a long walk saturated, so a block mean can look calm while a large share of the block has already yawed past 15°.

The current controller, frozen before these new blocks, was then run on two fresh 200-seed sets. Seeds 58000–58199 are 188/200, all-seed progress 0.172 m/s, survivor speed 0.182 m/s, path 0.199 m/s, yaw −1.2°, shoulder peak-to-peak 18.0°, head yaw 15.6°, main saturation 5.93%, main RMS 0.996 N·m. The same wave on the original legs is 130/200. Arms free are 200/200 at 0.210 m/s with yaw +8.4°. Seeds 59000–59199 are 194/200, yaw about 0°, survivor speed 0.182 m/s, against arms free at 200/200 and 0.211 m/s. Together with 195/200 and 194/200 on the earlier blocks, the 10 s rate is 188–195 per 200, not a stable 199. Seeds 61000–61199 with no overlay are 198/200 at 0.210 m/s (falls 61047 and 61073). Seed 5000 still matches the original evaluator, so that miss is the gait’s own rate, not a change to the no-overlay path.

Ankle samples at or above 1.91 N·m were about 8–9% in the earlier 20-seed load sample. That is stall occupancy in the model. It is not a safe continuous torque, and it is not by itself why the hip-roll load shift failed: hip roll was not the saturated joint.

## Lateral step and pelvis roll

Two arms-forward falls on seeds 51500–51523, a probe that was not used to score the controller, both had roll about −43° at 2.6–2.8 s. Positive `k_lat` places the swing foot toward that side. A wider stance by itself was worse on the train set. The chosen mix is that lateral step plus a larger pelvis roll, on top of the sagittal placement, stance hip, −0.02 rad lean, and the slow yaw trim. The arm command is unchanged.

Flat walking with no overlay on seeds 56000–56199 is 200/200 at 0.210 m/s. Seed 5000 still matches the original evaluator.

| Walk | Seeds | Survival | Progress, all | Survivor speed | Path, survivors | Yaw, all | Shoulder mean | Shoulder pp | Head yaw pp | Main sat |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lateral step + pelvis | 53000–53199 | 195/200 | 0.178 m/s | 0.182 m/s | 0.199 m/s | +1.8° | 20.9° | 17.9° | 15.6° | 5.58% |
| Sagittal legs only | 53000–53199 | 188/200 | 0.175 m/s | 0.185 m/s | 0.205 m/s | +3.5° | 20.9° | 17.8° | 15.5° | 5.56% |
| Same wave, original legs | 53000–53199 | 144/200 | 0.134 m/s | 0.178 m/s | 0.198 m/s | −7.6° | 20.9° | 17.7° | 15.5° | 5.40% |
| Arms free | 53000–53199 | 199/200 | 0.208 m/s | 0.209 m/s | 0.230 m/s | +11.3° | — | — | — | 5.64% |
| Lateral step + pelvis, confirmation | 54000–54199 | 194/200 | 0.177 m/s | 0.182 m/s | 0.199 m/s | +1.0° | 20.9° | 18.1° | 15.7° | 5.60% |
| Arms free, confirmation | 54000–54199 | 200/200 | 0.210 m/s | 0.210 m/s | 0.231 m/s | +11.6° | — | — | — | 5.69% |

The five held-out falls still tip, at a median 3.0 s, with about 35° of roll and 26° of pitch. Main RMS is 0.984 N·m against 0.973 N·m with the arms free. On a 20-seed load sample, 56300–56319, the ankles are the saturated main joints (about 7.6% and 9.3% of samples at or above 1.90 N·m) and the shoulders touch their 0.441 N·m stall on about 0.1% of samples. That sample is not a survival result.

Over 20 s on the predeclared seeds 55000–55039 the same controller survives 38/40 and yaws +23°. A second fresh 40, seeds 56200–56239, survives 40/40 and yaws only +2° at the same hip-yaw limit, and raising that limit to 0.035 or 0.05 rad does not change it. Twenty-second heading is not stable across seed blocks. A 2 N, 0.1 s sideways push on seeds 55100–55139 is 39/40, against 40/40 with the arms free, with yaw +0.4°.

The gap to the free walk on the two 200-seed tests is 4 falls and 6 falls. Survivor speed is 0.182 m/s against 0.209 m/s. The lateral step is worth about 7 survivals in 200 over the sagittal controller (195 against 188 on the same seeds) and about 51 over the original legs.

## Stance and swing-foot balance

The arm command is unchanged: shoulders commanded around 22°, measured mean 20.9° and peak-to-peak 18.0°, head yaw peak-to-peak 15.6°. What changed is the legs. While a leg is in swing it places the foot forward when pitch is positive, the sign measured when an arms-forward walk tips. The stance leg takes a hip-and-ankle correction of the same shape as the crouch lean, from the pitch error, and the −0.02 rad lean still rises with the arms. A slow hip-yaw integral, limited to ±0.02 rad, trims heading. It is not the step-frequency wiggle that yawed +42° in 20 s. The no-overlay gait is untouched: seed 5000 still matches the original evaluator, and seeds 50200–50399 are 200/200 at 0.211 m/s.

Forward progress below is the change in x divided by the trial length, averaged over every seed, including falls. Survivor speed is labeled. Yaw is the mean over every seed.

| Walk | Seeds | Survival | Progress, all | Survivor speed | Path, survivors | Yaw, all | Shoulder pp | Main RMS | Main sat |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Place + stance + lean + slow yaw | 47000–47199 | 188/200 | 0.173 m/s | 0.184 m/s | 0.205 m/s | +3.4° | 18.0° | 0.993 N·m | 5.92% |
| Place + stance + lean, no yaw trim | 47000–47199 | 186/200 | 0.171 m/s | 0.182 m/s | 0.205 m/s | +6.7° | 18.0° | 0.995 N·m | 6.01% |
| Same wave, original legs | 47000–47199 | 136/200 | 0.127 m/s | 0.177 m/s | 0.198 m/s | −10.3° | 17.7° | 0.981 N·m | 5.62% |
| Arms held forward, no wave | 47000–47199 | 127/200 | 0.125 m/s | 0.184 m/s | 0.207 m/s | 0.0° | 0.3° | 0.978 N·m | 5.62% |
| Arms free | 47000–47199 | 200/200 | 0.210 m/s | 0.210 m/s | 0.231 m/s | +10.2° | — | 0.983 N·m | 5.96% |

The same wave without the new legs survives 136/200. Holding the arms forward and not waving survives 127/200. The wave is not the dominant fall source on this 200, and the leg response is what moves the count from 136 to 188. Twelve falls remain. On a fresh 100, seeds 50900–50999, the yaw trim and the version without it both survive 96/100; yaw is +3.3° with the trim and +8.4° without. Over 20 s, seeds 50800–50839, the trim survives 37/40 with yaw +13°, and the version without it survives 36/40 with yaw +23°. Heading is improved and still not fixed over 20 s. A 2 N, 0.1 s sideways push on the version without the trim was 37/40, against 40/40 with the arms free. Main-joint saturation stays near 6%.

Foot placement alone, on the train seeds 50000–50063, was 59/64. Stance-hip feedback alone was 28/64 and is not usable by itself. The constant lean alone was 54/64. The combination is the one that was held out.

## Why the walks fall

On 16 diagnostic seeds (44000–44015), not used to choose a controller: arms held at 22° with the swing turned off fell 5/16, while the same ±10° shoulder and ±8° head wave about an 8° mean fell 0/16. The constant forward pose, not the size of the wave, is the fall source. Antiphase shoulders are a real forward/back counterswing (each hand moves about 20 mm in x for 10°). The shoulder axes are mirrored and both include a yaw component, so that counterswing also yaws the trunk. A phase shift only retimes that yaw. It does not hold the arms up.

Forward speed below is the change in x over 10 s, survivors only. Path speed is the integrated horizontal speed, also survivors only. Yaw “all” includes trials that fell, using the yaw at the fall. Torque samples are every 0.01 s. The leg phase, the 45° fall test, and the randomization are the original ones. The arm wave is an extra smoothstep from 0.4 s to 1.8 s. `reliable.npy` is not modified.

## Compensation that keeps the wave

A flat-footed crouch lean of −0.02 rad, rising with the arms, was compared with the forward pose on fresh seeds. The swing command stays ±10° at the shoulder and ±8° at the head.

| Walk | Seeds | Survival | Forward | Path | Yaw, all trials | Shoulder mean | Shoulder pp | Head yaw pp | Main RMS | Main sat |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lean −0.02 rad | 48000–48199 | 164/200 | 0.181 m/s | 0.201 m/s | +3.2° | 20.9° | 17.9° | 15.5° | 0.987 N·m | 5.80% |
| Same arms, no lean | 48000–48199 | 145/200 | 0.174 m/s | 0.196 m/s | −7.7° | 20.9° | 17.7° | 15.5° | 0.988 N·m | 5.74% |
| Arms still | 48000–48199 | 200/200 | 0.209 m/s | 0.230 m/s | +9.4° | — | — | — | 0.985 N·m | 5.96% |
| Lean −0.02 rad, repeat | 49100–49199 | 91/100 | 0.181 m/s | 0.202 m/s | +1.6° | 20.9° | 18.0° | 15.5° | 0.980 N·m | 5.52% |
| Lean plus pitch feedback | 49100–49199 | 84/100 | 0.184 m/s | 0.203 m/s | −1.2° | 20.9° | 18.0° | 15.5° | 0.975 N·m | 5.20% |
| Tucked mean 8°, same swing | 48000–48199 | 169/200 | 0.185 m/s | 0.203 m/s | −2.6° | 7.2° | 17.8° | 15.5° | 0.986 N·m | 5.82% |

The lean keeps the arms at 21° and the measured wave, cuts the fresh-set falls from 55 to 36, and leaves the yaw near +3° instead of the gait’s own +9°. Pitch feedback on that lean did not add survivals (84/100 against 91/100). Dropping the arm mean to 8° adds 5 survivals in 200 and gives up the forward pose. A hip-yaw wiggle that scored 191/200 on a different block (43000–43199) yaws +19° in 10 s and +42° in 20 s (39/40 still up at 20 s). That survival is not a controlled heading. A 2 N push was survived 38/40 by that wiggle and 39/40 with the arms still.

The flat gait on 42000–42199 is 200/200 at 0.209 m/s, and on 48000–48199 it is 200/200 at 0.209 m/s. The arm wave with the lean is 164/200 on the second of those. The remaining falls are still mixed roll and pitch tips. This is the ceiling found after separating the pose, the wave, the phase, a hip-yaw trim, and a pitch feedback: the reliable leg feedback does not carry this arm motion at the flat-walk rate. Seeds 47000–47199 were not used.

## Coupled phase, same motion size

The −30° yaw in 10 s is a moment from the arm and head sine, not a slower step that only looks slow because the robot is turned. Shifting that sine by 1.2 rad, with the amplitudes held at shoulders ±10° and head yaw ±8°, was chosen on seeds 39000–39031 because it had the smallest yaw among commands that still measured at least 14° of shoulder travel and 12° of head-yaw travel. A proportional shoulder and head bias from heading error made the yaw larger and was not chosen. Hip-yaw heading stacked on the motion was not retried.

| Set | Survival | Forward speed | Path speed | Yaw in 10 s | Shoulder pp | Head yaw pp | Main sat |
|---|---:|---:|---:|---:|---:|---:|---:|
| Phase 1.2 rad, fresh 40000–40039 | 27/40 | 0.178 m/s | 0.197 m/s | −10.3° | 17.7° | 15.5° | 5.33% |
| Same amplitudes, phase 0, same seeds | 24/40 | 0.178 m/s | 0.203 m/s | −31.8° | 17.5° | 15.1° | 5.79% |
| Arms still, same seeds | 40/40 | 0.211 m/s | 0.231 m/s | +7.4° | — | — | 5.84% |
| Phase 1.2 rad, confirm 41000–41019 | 14/20 | 0.177 m/s | 0.196 m/s | −12.3° | 17.2° | 15.4° | 5.19% |

Main RMS stays 0.97–0.98 N·m. Falls are tips in both roll and pitch, about 30° at the last sample, not a pure yaw exit. The phase shift cuts the drift by about three times and adds 3 survivals in 40. It does not bring the walk back to 40/40 or to 0.21 m/s. Seeds 42000–42199 with no overlay are 200/200 at 0.209 m/s. Seeds 43000–43199 were not used.

## Contact, swing timing, and hip-yaw authority

Nothing in this section is promoted. The frozen arms-forward controller remains the one scored 195/200, 194/200, 188/200, and 194/200 (771/800, 96.375%). A binomial standard error is about 0.66 percentage points and is not a confidence interval. The 95% Wilson interval for 771/800 is 94.8% to 97.5%. The 199/200 figure is a target rate, not a demonstration that the underlying rate is 99.5%, and 99.5% is outside that Wilson interval. The arm command is unchanged: measured shoulder mean about 20.9°, shoulder peak-to-peak about 18°, head yaw peak-to-peak about 15.5–15.8°. Survivor forward speed stays about 0.18 m/s against about 0.21 m/s with the arms free. That speed gap is real; it is not only heading.

Seed 5000 still matches `walk_search.evaluate` (dx 2.082264 m). Fresh no-overlay seeds 67000–67199 are 200/200 at 0.2095 m/s. Seeds 61000–61199 remain 198/200. One clean block does not make the no-overlay gait perfectly reliable.

### What the two no-overlay falls actually do

Seeds 61047 and 61073 were replayed and not used to pick a gain.

| Seed | Fall time | What crosses 10° first | Sole forces at that sample | Ankle torque | Hip-roll command minus achieved |
|---|---:|---|---|---|---|
| 61047 | 3.97 s | Pitch +10.3° at 3.07 s, roll still −2.7°. Roll reaches −10° at 3.43 s with pitch already +12.7°. | Left sole 0.79 then 0.95 body weights. Right sole 0. | Right ankle −0.81 N·m at the pitch sample, then −1.91 N·m (stall) while that foot is still off the ground. | About +0.05 rad at the pitch sample, about −0.07 rad at the roll sample. |
| 61073 | 3.43 s | Pitch −10.2° at 2.68 s. Roll is −1.5° and never reaches 10° before the fall. | Left sole 0.93 body weights. Right sole 0. | Right ankle already +1.91 N·m. Left ankle +1.07 N·m. | About +0.09 to +0.11 rad. |

Both are pitch falls during ordinary single support. The ankle that is at the stall stop is the airborne foot, so more ankle offset on that joint cannot put a force on the floor. The two stalls have opposite signs.

### Loaded-foot hip roll, then a swing-phase lead

On a healthy walk the gait already spends each step on one sole at about 0.8 body weights with the other sole at zero, and roll rate routinely passes 0.8 rad/s while |roll| stays under about 6°. Treating “one sole unloaded” as a fault therefore fires on the normal step.

A hip-roll offset on the loaded foot, `q += k * roll_rate * (that foot’s share of normal force)`, clipped at ±0.08 rad, was trained on fresh seeds 63000–63079. The current controller was 80/80 there, all-seed progress 0.182 m/s, yaw mean +0.4°, and 26% of trials already past ±15° in 10 s. Adding the offset made it worse:

| Law | Survival | Progress, all | Yaw, all | Share past ±15° in 10 s | Shoulder mean | Shoulder pp | Head yaw pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| Current | 80/80 | 0.182 m/s | +0.4° | 26% | 20.9° | 18.3° | 15.8° |
| Loaded-foot hip roll, k = 0.12 | 70/80 | 0.160 m/s | −15.4° | 48% | 20.9° | 18.1° | 15.7° |
| Same, k = 0.24 | 72/80 | 0.161 m/s | −15.0° | 48% | 20.9° | 18.1° | 15.6° |
| k = 0.16 and the extra pelvis roll removed | 65/80 | 0.151 m/s | −2.1° | 29% | 20.9° | 17.8° | 15.3° |

The gate required +3 survivals, the pose floors, |yaw mean| ≤ 8°, and progress within 0.01 m/s. None passed, so there is no held-out of this law.

A swing-phase lead was the other channel. While |roll| > 0.10 rad, |roll rate| > 0.8 rad/s, and one sole held under 12% of the loaded sole, phase advanced at 2 or 4 rad/s, capped at 0.6 rad, and decayed afterward. On fresh seeds 68000–68079 the current controller and both leads are 76/80 with the same falls (68011, 68013, 68017, 68077), progress 0.173 m/s, survivor speed 0.181 m/s, path 0.198 m/s, yaw mean −1.1°, 19% past ±15° in 10 s, shoulder mean 20.9°, shoulder peak-to-peak 17.9°, head yaw 15.5°. The lead did not engage early enough to be a different controller. It was not held out. The second block was reserved for the case of fewer than four current falls and was not needed.

### Hip-yaw sign, achieved motion, and windup

Unrandomized seed 0, no arms, 6 s. Body yaw with no hip-yaw command is +13.5°. A constant +0.02 rad command is achieved at about +0.014 rad on both halves of the step and cuts that yaw to +5.3°. A constant −0.02 rad command is achieved at about −0.026 rad and changes the yaw only to +12.5°. The negative direction barely turns the body on this walk. Gating +0.02 rad to the half where `sin(phase) ≤ 0` is not achieved (the joint averages near +0.005 rad) and the yaw stays at +13.8°. Gating it to `sin > 0` produces +5.1°, almost the whole effect of the constant command, again with the joint averaging near +0.005 rad. Scaling the strong half by 0.15 leaves the yaw at +5.8°. A stance-flipped sign is not supported: both halves respond to a positive command with less positive body yaw, and one half does almost all of the work. A half-cycle target is not what the position servo holds.

On fresh 20 s seeds 63400–63439 the current trim (ki 0.12, command sign −1, |u| ≤ 0.02 rad) is 38/40. The median yaw is +6.2°, the 10th to 90th is −25° to +53°, the range is −50° to +64°, and 60% of trials exceed ±15°. The hip-yaw command sits at ±0.02 rad for a median 66% of the trial (max 89%). Output anti-windup, which stops the integrator once that clip is active and the error still points the same way, is also 38/40, with the same extremes and a worse share past ±15° (70%, median +8.5°, time at the clip 72%). Scaling the strong half of the step drops the median to about 0° and the mean to +3.9°, and raises the share past ±15° to 78% (range −61° to +85°). That is a calmer center with a worse tail. A smaller clip of 0.008 rad plus anti-windup is 39/40 and 80% past ±15° (range −59° to +82°). Less authority does not hold the heading. None of these cleared the predeclared gate (the share past ±15° down by at least 0.15, survival within 2, |median| not worse by more than 2°), so none was held out.

### What would have to be different

The failed laws are not a proof that the robot cannot walk with this arm motion. They bound the actuators this controller can already use.

The falls that remain are a moment during single support. The airborne ankle is the joint at the 1.91 N·m stall, and the hip-roll command is already late by about 0.05–0.11 rad, so another hip-roll or ankle offset on those joints does not land. A recovery that would be different from the ones tested is a swing-foot target issued at the start of swing from lateral center-of-mass velocity, with the hip actually reaching it before the stance interval ends. Contact force at mid-stance does not add that information: one sole at zero is the normal step. The sim also randomizes 0–10 ms of latency. A faster hip than that model, or a measured torque-rate limit rather than the stall torque alone, is the data this loop does not have.

Heading needs a yaw moment in the direction a modest command can actually produce on randomized walks. The single unrandomized trajectory is not that measurement. The paired identification below replaces it.

## Swing-start foot target and paired yaw authority

No controller was frozen. The 771/800 aggregate is the benchmark, not a new success. Seed 5000 still matches the evaluator (dx 2.082264 m). Single support, one sole loaded and the other at zero, is the normal step and is not counted as a contact failure.

### Coordinated-wave falls, separate from the two no-overlay falls

Every fall in three already-scored blocks of the frozen arms-forward controller was replayed only to read the order of the angles. These seeds were not used to choose a gain. Pitch reached 10° before roll did on all 12 falls in 58000–58199, all 6 in 59000–59199, and all 4 in 68000–68079. At the pitch crossing, |roll| was still about 1° to 7°. One of the 22, seed 58131, pitched the other way (−10° at 2.49 s). The other 21 pitched forward. This is not inferred from the no-overlay seeds 61047 and 61073. Those two remain pitch falls of the arms-free gait, with the airborne ankle at opposite stall stops, and they were not used to explain the wave.

On the airborne part of each swing, hip-roll command minus achieved angle has median about 0 and a 90th percentile of 0.053 rad, on the fall replays and on fresh nominal seeds 71400–71405 alike. The hip is reaching the roll command it is given. What differs at swing start is pitch (median absolute 4.8° on the fall replays, 0.9° on the nominal seeds) and lateral COM speed (median absolute 0.066 m/s versus 0.021 m/s). Hip-pitch command is also achieved at the median (error about 0). The 90th percentile of that pitch miss is 0.28 rad on the fall replays and 0.15 rad on the nominal seeds, so the bad tail of sagittal tracking is wider, not the typical step.

### What a swing-start target can actually reach

On fresh seeds 71200–71205 a constant hip-roll offset was latched onto the swing leg at the sine zero crossing and held for that half step. Paired against the same seed with no latch, over airborne intervals of at least 0.08 s:

| Latch | Swings | Command seen | Achieved | Fraction reached | Foot y | Hip-roll torque, 90th |
|---|---:|---:|---:|---:|---:|---:|
| +0.10 rad | 69 | +0.095 rad | +0.084 rad | 94% | −9.9 mm | 1.30 N·m |
| +0.16 rad | 53 | +0.154 rad | +0.133 rad | 93% | −13.0 mm | 1.59 N·m |

Positive hip roll moves the foot toward −y. The servo reaches this target inside one swing, and the torque stays under the 1.91 N·m stall. The step it buys is about 10 mm. The existing sagittal placement is already clipped at 0.10 rad, and hip pitch is the joint that occupies the 1.91 N·m stall on the earlier load sample (about 4.5% of samples). A larger fore-aft step, which is the direction these pitch-first falls would need, is not inside that actuator’s demonstrated margin. A 10 mm lateral step does not address a fall whose pitch has already passed 10°. No swing-foot law was trained, and no fresh 200-seed block was run on an unchanged controller.

### Heading authority on paired randomized seeds

Each row is the change in body yaw relative to the same seed’s frozen controller, over 6 s. Seeds 71600–71607 unless noted. All of these kept the arm wave.

| Command | Still up | Median yaw change | Range | Seeds past +1° | Seeds past −1° | Speed |
|---|---:|---:|---|---:|---:|---:|
| Both hips +0.03 rad | 8/8 | −7.0° | −25° to +6° | 1 | 7 | 0.176 m/s |
| Both hips −0.03 rad | 6/8 | +9.9° | +3° to +43° | 8 | 0 | 0.173 m/s |
| Stance hip only +0.03 rad | 8/8 | +19.0° | +1° to +43° | 8 | 0 | 0.167 m/s |
| Stance hip only −0.03 rad | 8/8 | −23.7° | −67° to −11° | 0 | 8 | 0.173 m/s |
| Stance hip ±0.008 and ±0.015 rad, seeds 71700–71707 | 8/8 | −1° to −3.5° for every sign | both signs inside each set | — | — | 0.173–0.175 m/s |
| Both hip pitches +0.04 rad | 8/8 | −64° | −100° to −34° | 0 | 8 | 0.148 m/s |
| Both hip pitches −0.04 rad | 8/8 | +60° | +41° to +97° | 8 | 0 | 0.112 m/s |
| Both hip pitches +0.008 rad, seeds 71800–71807 | 8/8 | −7.9° | −17° to +4° | 1 | 7 | 0.175 m/s |
| Both hip pitches −0.008 rad, seeds 71800–71807 | 8/8 | +19.2° | −7° to +24° | 6 | 1 | 0.167 m/s |

Stance-only hip yaw at 0.03 rad does turn every seed in the commanded direction and does not drop these 6 s walks. The spread across eight seeds is already tens of degrees, so closing a feedback loop at that amplitude would write tails, not remove them. At 0.008 and 0.015 rad the sign is not consistent from seed to seed. Differential hip pitch is bidirectional, and at 0.04 rad it cuts speed from about 0.175 m/s to 0.112–0.148 m/s. At 0.008 rad the speed holds, but one sign yaws about −8° and the other about +19°, and neither sign carries every seed. A loop on that channel would improve a median in one direction and worsen the tail in the other. It was not trained.

The swing hip can reach a foot target of about 0.10–0.16 rad issued at toe-off, and that target is worth about 10–13 mm. The coordinated-wave misses are pitch-first, so that lateral step is the wrong axis. The open-loop yaw trials show that the particular commands tested there are not yet a qualified heading controller. They do not show that feedback on some other law is impossible. Heading stays a separate unmet requirement. Walking was tested next, without treating speed as a gate.

## Lower step demand and earlier placement

Pitch reaching 10° before roll does supersedes the earlier reading that these falls were mostly lateral. This pass did not add another lateral offset. `reliable.npy` was not modified. The no-overlay evaluator still matches seed 5000 (dx 2.082264 m). Speed is reported and was not a requirement: a slower walk that actually stayed up would have been acceptable.

Two scratch changes were trained on fresh seeds 75000–75079, 80 walks, with the same arm command. `demand` multiplies both gait frequency and stride, so the step gets shorter and slower together. `pre_toe` starts the existing 0.10 rad fore-aft placement during the last part of stance. The clip is not raised and the actuator model is not strengthened.

| Candidate | Survival | Progress, all | Survivor speed | Toe-off \|pitch\| median | Share of toe-offs past 8° | Placement clip | Hip-pitch stall, survivors | Shoulder mean | Shoulder pp | Head yaw pp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | 78/80 | 0.179 m/s | 0.183 m/s | 0.98° | 0.5% | 0.5% | 3.68% | 20.9° | 17.9° | 15.6° |
| Frequency and stride ×0.90 | 66/80 | 0.132 m/s | 0.156 m/s | 1.19° | 1.7% | 1.4% | 2.05% | 20.9° | 18.0° | 15.8° |
| Frequency and stride ×0.80 | 0/80 | 0.000 m/s | — | 1.63° | 19.7% | 19.2% | — | — | — | — |
| Same placement, started before toe-off | 79/80 | 0.181 m/s | 0.183 m/s | 0.98° | 0.2% | 0.2% | 3.57% | 20.9° | 17.9° | 15.6° |

The gate required the arm wave, at least 4 more survivals than current, toe-off pitch down by at least 1°, and either hip-pitch stall down by 0.5 percentage points or placement clipping down by 1 point, without clipping getting worse. None passed, so there was no held-out and no 20 s block.

×0.90 did lower hip-pitch stall, from 3.68% to 2.05%, and it lost 12 walks. Toe-off pitch and the share past 8° both rose. ×0.80 did not walk. Stall occupancy and the pitch that leads the falls are not the same knob: cutting the step reduced the stall and made the pitch tail worse. Starting the same placement earlier left the median toe-off pitch at 0.98° and added one survival in 80, inside the noise of this block.

On the frozen controller, six of the pitch-first falls were sampled again at the first +6° and +10° of pitch. This was not a training set. At +6°, the stance ankle was already at −1.91 N·m on 58035 and 59026. On 58028, 59067, and 68011 the stance ankle still had about 0.6–1.3 N·m left and a hip pitch was the joint at −1.91 N·m. At +10° the loaded foot and the saturated joint had often swapped. Seed 58131, the backward pitch, reached −10° with the loaded ankle at +0.73 N·m. There is no single joint that still has torque on every one of these rises.

## Where this workstream stops

The best scratch candidate that keeps the arms is the frozen one already scored 195/200, 194/200, 188/200, and 194/200. That is 771/800. The 95% Wilson interval is 94.8% to 97.5%. It is not promoted over `reliable.npy`, and it is not a 199/200 walk. Measured shoulder mean is about 20.9°, shoulder travel about 18°, head yaw about 15.6°. Survivor forward speed is about 0.182 m/s against about 0.21 m/s with the arms free. That slower speed is an honest property of this candidate. It was not treated as a reason to reject a slower reliable walk; the slower walks that were tried were less reliable.

Unmet, in order:

- Arms-forward survival is still short of a 199/200 target. The target is a rate to aim at, not a rate this sample has shown.
- Heading over 20 s, as the share of trials exceeding ±15°, is unmet. The open-loop commands tried on eight seeds were not qualified. That does not close the door on a different feedback law.
- The no-overlay gait is 198/200 on 61000–61199 and 200/200 on 67000–67199. Its own Wilson interval on 198/200 is 96.4% to 99.7%. One block neither proves nor excludes 99.5%.

Shortening the step is not a pitch correction: it freed hip-pitch stall and lost walks. The stance-ankle law below is the correction that uses the residual that is sometimes still there.

## Stance-ankle pitch feedback

The command is added only to an ankle that has sole force. Share follows the two sole forces, so double support blends and an airborne ankle gets nothing. The addition scales from full below 1.20 N·m to zero at 1.80 N·m, short of the 1.91 N·m stall, and the position change is limited to 0.05 rad. `reliable.npy` is untouched. Seed 5000 still matches the evaluator (dx 2.082264 m).

Sign, on fresh seeds, before any selection. A constant ±0.04 rad on the loaded ankle, seeds 79000–79011, raised the pitch peak for both signs (median peak from 3.8° to 11.0° and 6.2°) and added falls. Proportional feedback on 79100–79111 did separate. With `u = -0.40 * pitch` the block went from 10/12 to 12/12 and the time past 8° fell from 0.070 to 0.005. With the opposite sign it stayed 10/12. The restoring sign is negative. The integral, when used, stops growing once that command is saturated in the correcting direction or both loaded ankles have no residual left.

On a clean fresh block, 79200–79279, the frozen controller was already 80/80. Always-on `u = -0.40 * pitch` fell to 73/80 and raised the time past 8°. Adding a pitch-rate term, an integral, or the earlier hip placement on top of it did not recover that. The command was firing on the ordinary few degrees of pitch, not only on a rise. A 4° deadzone leaves it off inside that band.

Seeds 79300–79379, deadzone 4°, `k = 0.40`. Current 76/80, falls 79323, 79333, 79355, 79356. The ankle law 78/80, falls 79323 and 79355 only. It removed two falls and added none. Time past 8° went from 0.022 to 0.014, time past 10° from 0.017 to 0.011, and the number of trials that touched 10° stayed 9. Ankle stall stayed 9.3%. Shoulder mean 20.9°, shoulder travel 18.2°, head yaw 15.7°. Survivor speed 0.178 m/s against 0.181 m/s. A 6° deadzone was 77/80. The old requirement of four extra survivals and a 1° drop in mean toe-off pitch was not used. A gain of two walks with no new fall is real on this block and still small, so it was taken to fresh held-outs rather than treated as either qualified or disproven.

| Block | Ankle law | Frozen controller | Arms free | Ankle-law speed | Frozen speed | Time past 8° , ankle vs frozen | Ankle stall |
|---|---:|---:|---:|---:|---:|---|---:|
| 80000–80199 | 194/200 | 197/200 | 200/200 at 0.211 m/s | 0.182 m/s | 0.181 m/s | 0.012 vs 0.009 | 8.6% vs 8.6% |
| 81000–81199 | 198/200 | 193/200 | 200/200 at 0.210 m/s | 0.181 m/s | 0.182 m/s | 0.008 vs 0.018 | 9.1% vs 9.1% |

Together that is 392/400 against 390/400. The 95% Wilson intervals are 96.1% to 99.0% and 95.5% to 98.6%. They overlap. On 80000 the ankle law added falls 80076, 80137, and 80176. On 81000 it removed five falls, including 81161, which ended at 42° of pitch and 9° of roll, and it added none. About 10% of control steps had no residual, so the command was off, and the 0.05 rad clip was active on under 1% of steps. Shoulder mean stayed 20.9° and shoulder travel about 18°, head yaw 15.5° and 15.7°. A 20 s heading block was not run: the candidate was not ahead on both held-outs. Heading remains separate. The eight-seed open-loop yaw test still does not show that feedback is impossible.

The frozen arms-forward controller stays the scratch candidate. Its benchmark is still 771/800, Wilson 94.8% to 97.5%, not a promotion and not a 199/200 walk. These two new blocks of that same controller are 197/200 and 193/200. Survivor speed remains about 0.182 m/s against about 0.21 m/s with the arms free.

What this mechanism can and cannot do: when pitch is already past about 4° and the loaded ankle is below 1.80 N·m, a negative ankle offset is achievable and, on some seeds, removes a fall. Across the paired held-outs the net is two survivals in 400, with the blocks reversed. The exact comparison is in the final section. Geometry, the XML, the scene, the fall test, and the perturbation distribution were not changed.

## Final consolidation

No further gain sweep and no further batch of the unchanged controller. Nothing is promoted. `params/reliable.npy`, `sim/models/twiglet_v3_v335ac.xml`, and `geometry/scene_v335ac.npz` were not edited.

Hashes, sha256:

- `params/reliable.npy` `d18f884ff5146eb0ed09cb8ab7562337482dd42c669649b4acd90c24ac083754`
- `params/fast.npy` `aeb2c4ba3cd4dbbd0d382272292d09c63d7620422f05b671ac6297fc659c3cad`
- `params/efficient.npy` `4f32549810c671d72c40719e1d19af53f83e8d2ededbe9460db668b891e39093`
- `sim/models/twiglet_v3_v335ac.xml` `5e62e84b4fbc20270d8331274b33190f4e83dfc6a422a95bad45c19afdf6503b`
- `geometry/scene_v335ac.npz` `e2d3009f6c35cfdfcefabf7ec9013ee9193547d5c4d16de37db78f0d07a60aba`

The frozen scratch candidate is one config. It is `step_pelvis` from the lateral train and the `current` control in every later comparison: balance on, body lean −0.02 rad, swing-foot placement `k_place` 0.6 and `d_place` 0.05, stance hip `k_hip` −0.25, lateral step `k_lat` 0.45 and `d_lat` 0.05, pelvis roll `k_roll_extra` 0.30 and `d_roll_extra` 0.04, slow hip-yaw `ki` 0.12 with command sign −1 and limit ±0.02 rad. Arms are commanded at shoulder mean 22°, swing ±10°, head yaw ±8°, phase 1.2 rad. Measured on the held-outs: shoulder mean about 20.9°, shoulder peak-to-peak about 18°, head yaw peak-to-peak about 15.6°. Gait vector is `params/reliable.npy`. Episode is 10 s, the same randomization as `walk_search.evaluate`, and a fall is 45° of roll or pitch or COM height under 0.6 of the start height. `python reproduce_frozen.py --spec` prints that dict. `python reproduce_frozen.py --identity` checks seed 5000 against `walk_search.evaluate`. The last match is dx 2.082264 m.

Six disjoint 200-seed held-outs of that config use that same success rule: 53000–53199 is 195/200, 54000–54199 is 194/200, 58000–58199 is 188/200, 59000–59199 is 194/200, 80000–80199 is 197/200, 81000–81199 is 193/200. That is 771 + 390 = **1161/1200 = 96.75%**. The 95% Wilson interval for the pooled count is **95.6% to 97.6%**. Training and screening blocks of the same controller (52000, 57000, 63000, 68000, 75000, 79200, 79300) and the 20 s and push blocks are not in this pool. 199/200, which is 99.5%, is outside the pooled interval. The target is not met.

Against the original leg controller with the same arm wave, on the matched seeds 53000–53199, the frozen candidate is 195/200 and the original legs are 144/200. On 58000–58199 the same comparison is 188/200 against 130/200. Arms free on those blocks are 199/200 and 200/200. All-seed forward progress of the frozen candidate is about 0.17–0.18 m/s. Survivor speed is about 0.182 m/s. Path speed of survivors is about 0.199 m/s. Arms free are about 0.210 m/s forward and about 0.230 m/s along the path. The slower speed is part of the result.

The arms-forward falls that were replayed, all 12 on 58000, all 6 on 59000, and all 4 on 68000, reached 10° of pitch while roll was still about 1° to 7°. That replaces the earlier lateral reading. At the first +6° of pitch the loaded ankle is already at −1.91 N·m on some of those falls and still has about 0.6–1.3 N·m on others. Hip pitch is often the other joint at stall. Ankle samples at or above 1.90 N·m stay around 8–9% on survivor walks. That is stall occupancy in the model, not a safe continuous torque.

Heading over 20 s is unmet. On 55000–55039, 60% of trials exceed ±15° (median +18°, range −24° to +65°), and the hip-yaw command sits at ±0.02 rad for a median 66% of the trial. On 56200–56239, 38% exceed ±15° (median −2°, range −47° to +76°). The two medians are not one behavior. The eight-seed open-loop yaw commands were not a qualified feedback law. They do not show that feedback is impossible.

The no-overlay gait is not perfectly reliable. Published and rechecked blocks include 200/200 on 5000–5199, 199/200 on 16000–16199 and 19000–19199, 198/200 on 61000–61199 (falls 61047 and 61073), and 200/200 on 67000–67199. The Wilson interval for 198/200 alone is 96.4% to 99.7%.

Laws that were tried and not kept, and why:

- Waiting for double support before a start survived 10/20. The original one-second ramp then a phase stop survived 20/20.
- A hip-yaw wiggle that scored high survival yawed about +19° in 10 s and +42° in 20 s.
- A stance-foot load shift, both signs, lost walks on its train sets (78/80 for the frozen mix, 72–77 and 76–77 for the shifts).
- Extra hip roll on the loaded foot, proportional to roll rate, dropped a clean 80/80 block to 70/80, 72/80, and 65/80 and pulled yaw to about −15°.
- A swing-phase lead gated on large roll never separated from the frozen controller (76/80, same four falls).
- Hip-yaw anti-windup, scaling the strong half of the step, and cutting the yaw limit to 0.008 rad each raised the 20 s share exceeding ±15° (0.60 to 0.70, 0.78, and 0.80 on 63400–63439). The scaled law moved the median to about 0° and the max to +85°.
- Frequency and stride ×0.90 lowered hip-pitch stall from 3.68% to 2.05% and survival from 78/80 to 66/80, and the pitch tail grew. ×0.80 survived 0/80.
- Starting the existing 0.10 rad hip placement before toe-off was 79/80 against 78/80 on one block and 80/80 against 80/80 on another. Toe-off pitch did not move. That is too small to treat as qualified, and it is not a disproof.
- Always-on stance-ankle feedback `u = -0.40 * pitch` fell from 80/80 to 73/80 on 79200–79279 and increased the pitch tail. The rate term, the integral, and stacking the early hip placement were worse, and the rate term put 62% of trials past ±15° of yaw.
- The 4° deadzone on that ankle law was the one taken forward: 78/80 against 76/80 on 79300–79379, two specific falls removed, none added, ankle stall unchanged.

Paired held-out of that deadzone law against the frozen controller, same seeds, stored trial by trial. Of 400 seeds, 387 survived both, 5 fell both, 5 fell only on the frozen controller (81046, 81049, 81052, 81072, 81161), and 3 fell only on the ankle law (80076, 80137, 80176). The ankle law is ahead by 2 survivals. The exact two-sided McNemar probability of a split at least this uneven, given 8 discordant seeds, is 186/256 = 0.727. The 95% Clopper–Pearson interval on the share of those 8 that favor the ankle law, scaled back to the 400, is a survival difference of **−1.0 to +1.7 percentage points**. The point estimate is +0.5 points. That interval includes no difference and it also includes a difference of about a percentage point. Overlap of the separate Wilson intervals is not this test, and this test does not prove there is no effect. Neither 392/400 nor 390/400 meets a 199/200 target. The counts and the table are in `results/final_audit.json`.

The limit is the set of laws above, not a proof that no controller can do better and not a requirement to redesign the hardware. The next capability that is actually different is a fore-aft plan computed before toe-off, coordinated with the step, and kept inside the torque the stance ankle and hip pitch still have at that earlier moment. Body pitch after it has already passed 4°, and an ankle that is already near 1.80 N·m, is the signal these laws used. A torque-constrained trajectory for the upcoming step is not one of them. Calibrated thermal and battery data, a measured torque-rate beyond this servo model, and a mesh identity for the locked face are not in this snapshot. The scene source string names hair v3.52 and a v3.44 wig path, not v6b0, F4, G3, or D9. The XML head mass is 0.81392 kg, which matches the mass cited for the v6b0 retune. Visual meshes are the legacy ones. Scene contacts are the floor against the sole, trunk, and head boxes.

Reproduce from `sim/` with `TWIGLET_XML` pointed at `models/twiglet_v3_v335ac.xml` and `TWIGLET_PARAMS` pointed at `params/reliable.npy`. `python reproduce_frozen.py --spec` is the candidate. `python reproduce_frozen.py --identity` is the no-overlay check. `python reproduce_frozen.py --seeds 53000` is one frozen trial. The runnable archive is `twiglet-motion-dev-full.zip` and the source diff against the untouched snapshot is `twiglet-ac-motion.patch`.

## Anticipatory foot plan, after the freeze

The frozen 1161/1200 controller is unchanged and stays the control. This pass did not retune it. `reliable.npy`, the XML, and the scene were not edited. Seed 5000 still matches the evaluator at dx 2.082264 m.

The new law plans the next foot at the start of stance, about half a step before that foot’s toe-off, then ramps the hip-pitch offset through the second half of stance and holds it in the air. Hip pitch is scaled back when that joint is already near stall in the commanded direction. It is not a late ankle offset.

Three versions of the prediction were checked before any held-out.

Pitch plus pitch-rate over the half step, capped at 0.12 rad, on seeds 83000–83015: the step-frequency pitch rate saturated the cap almost every step (mean |command| 0.11 rad). Survival was 1/16 with the hip plan and 0/16 with a stance ankle added, against 16/16 for the frozen controller. A constant-rate forecast is the wrong predictor for a 2 Hz gait.

A 0.30 s average of pitch, ignoring anything inside ±0.05 rad, capped at 0.08 rad, on seeds 83016–83031: the average stays inside the deadzone, so the mean |command| was 0.003 rad. Survival 14/16 against 15/16. The slow pitch bias of a walk that is still up is only about a degree, which is the same fact as the 1° toe-off median. The dangerous pitch is a short rise, and this average does not see it in time.

The signal that exists before the pitch rise is the arm schedule itself, which runs from 0.4 s to 1.8 s. That schedule was mapped to a forward foot shift of 0.04 rad (about 4 mm, from the earlier measurement that 0.10 rad moves the foot about 10 mm) and added on top of the existing placement, not instead of it. The opposite sign, feet back, was the sign check. On seeds 83032–83047, all 16/16, feet forward cost speed (0.185 m/s to 0.168 m/s at 0.04 rad and 0.158 m/s at 0.06 rad) and did not create a pitch tail. Feet back started a pitch tail on one seed.

The 0.04 rad forward plan was then the only candidate trained, on fresh seeds 83200–83279.

| Walk | Survival | Progress, all | Survivor speed | Time past 8° | Trials past 10° | Yaw mean | Share past ±15° | Shoulder mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Frozen | 79/80 | 0.180 m/s | 0.182 m/s | 0.0077 | 7 | +3.0° | 24% | 20.9° |
| Feet forward 0.04 rad | 80/80 | 0.165 m/s | 0.165 m/s | 0.0027 | 3 | +19.7° | 60% | 20.9° |

It removed the one fall, 83277, and added none. Shoulder travel stayed 17.9° and head yaw 15.5°. Ankle stall went from 8.6% to 7.9%. The yaw share past ±15° in 10 s went from 24% to 60%. The existing ±0.02 rad hip-yaw trim was still on and did not hold it. A symmetric-looking hip-pitch shift is not a symmetric yaw moment on this gait. That is the same reason a high-survival hip-yaw wiggle was rejected earlier. No 200-seed held-out was run. A controller that puts 60% of a 10 s block past ±15° is not a step toward the survival target.

No geometry was changed. The forward-foot plan is not on the recommended path. `plan_fore_aft` runs only if a spec sets both `historical_fore_aft` and `k_plan`. The frozen spec sets neither. No sole was lengthened. Nothing in the approved blend, STL, `reliable.npy`, XML, or scene was edited by that experiment, so there was no keeper file to restore.

## Head and arm mass, hypothetical only

The XML stores one inertial for `head_assembly`: mass 0.81392 kg, COM at (−16.3, −1.6, +57.7) mm in that body’s frame. It does not split shell, wig, servo, eyes, or PCB. The visual meshes on that body are wood, grey, servo, dark, yellow, glass, eye-orange, and PCB, with no per-mesh mass. The neck yaw body is a separate 0.07151 kg and the head-pitch link is 0.01151 kg. The only documented head-mass change in the validation note is 0.8097 kg to 0.8139 kg. The 186.09 g figure is a stated wig print estimate, not a body in the model, and it is not established that those grams sit inside the 0.81392 kg lump. The scene source string names hair v3.52 and a v3.44 wig path. It does not identify locked F4, G3, D9, or a v6b0 wig mesh. Both forearms are about 0.094 kg each and their visuals include an STS3032 mesh, so scaling the link would scale the motor. Both grippers are 0.0043 kg each, 0.0086 kg together. Total modeled mass is 2.7525 kg. Earlier boot-lightening trials are not used: they were non-watertight and thin, and they did not leave a verified safe gram saving.

These edits are applied in memory, after the canonical file is loaded and before the usual ±10% mass randomization, on the frozen controller. Inertia `with_mass` scales the body’s principal moments by the mass ratio, which is a uniform-density assumption, not a constant-wall shell. `fixed` removes mass at the existing COM and leaves the inertia tensor alone. Neither is a printable design, and neither was drawn in Blender.

Fresh seeds 87000–87079. The unedited frozen controller was 80/80 on this draw, so a lighter part could not show extra survivals here. It could, and did, create falls.

| Hypothetical edit | Survival | Progress, all | Survivor speed | Trials past 10° pitch | Yaw mean | Share past ±15° | Shoulder mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| None | 80/80 | 0.181 m/s | 0.181 m/s | 4 | +2.7° | 34% | 20.9° |
| Head −50 g, inertia with mass | 80/80 | 0.184 m/s | 0.184 m/s | 1 | +6.5° | 36% | 20.9° |
| Head −100 g, inertia with mass | 79/80 | 0.181 m/s | 0.183 m/s | 3 | +11.6° | 43% | 20.9° |
| Head −186.09 g, inertia with mass | 74/80 | 0.165 m/s | 0.173 m/s | 7 | +24.4° | 69% | 20.9° |
| Head −186.09 g, inertia fixed | 74/80 | 0.162 m/s | 0.169 m/s | 8 | +21.4° | 68% | 20.9° |
| Head COM 10 mm toward the neck, mass unchanged | 79/80 | 0.169 m/s | 0.171 m/s | 1 | +43.9° | 94% | 20.9° |

Head yaw travel stayed about 15.1–15.5° and shoulder travel about 18°. Taking the whole stated wig mass out of the lumped head, under either inertia assumption, lost six walks and roughly doubled the share of trials past ±15° of yaw. Moving the same head mass 10 mm back toward the neck, without removing any grams, put 94% of trials past ±15°. A 50 g uniform reduction did not change the 80/80 survival and moved the yaw share from 34% to 36%. None of these is a reason to cut a keeper part, and none was taken to a 200-seed block. The head’s inertia is currently part of what limits how far the arm wave yaws the trunk. Removing it, in this model, makes that yaw larger.

No forearm was scaled, because the link mass includes the servo visual and the plastic portion is not measured. Both grippers together are 8.6 g. Deleting them would be a small fraction of the 186 g head cut that already made the walk worse, and that deletion was not run as a design.

What has to be weighed before any Blender edit: the wig print, the head shell, and the eye, PCB, and servo hardware as separate masses and COMs; and the forearm shell separately from the STS3032. Until those exist, a smaller head is a hypothesis that this lumped-mass trial does not support. The frozen controller on the old face remains 1161/1200. That number is not a validation of the approved face, and it is not 99.5%.

## Corrected approved-face head

The walking XML head, 0.81392 kg, is the old v3.30 face at the simulator’s rule masses. Solid-density face deltas are not used. The approved D9, F4, G3, and v6b0 parts were sliced with the saved PETG/PLA profiles. Part-only grams, excluding support and brim: D9 71.74 g, F4 187.94 g, each G3 collar 3.94 g, v6b0 wig 179.51 g. The 25 g ballast is already inside the corrected inertial and is not added again. Fixed motors, the bearing, and mounts are unchanged. The exterior silhouette is unchanged. The inertias are shape weights scaled to those slice grams, not a weighed tensor. The old head-lower “134 g” figure is not used; its own G-code is 188 g.

The isolated nominal model is `sim/models/twiglet_v3_v335ac_head852.xml`. Low and high scenario files are `twiglet_v3_v335ac_head833.xml` (0.83258 kg) and `twiglet_v3_v335ac_head895.xml` (0.89458 kg). The canonical XML, `reliable.npy`, and the scene were not edited. Loaded back into MuJoCo, the nominal mass is 0.85258 kg, the COM is (−11.62, −1.26, 56.43) mm in the head frame, and the inertia tensor matches the supplied full inertia. All three tensors are positive definite, and the principal moments satisfy the triangle inequalities. Relative to 0.81392 kg at (−16.28, −1.59, 57.67) mm, that is +38.7 g and +4.7 mm forward. Seed 5000 on the canonical model still matches the evaluator at dx 2.082264 m. The historical forward-foot plan stays off unless both `historical_fore_aft` and `k_plan` are set. No sole was extended.

On fresh seeds 91000–91039 the frozen controller, unchanged, is 38/40 on the old head and 36/40 on the corrected head. All-seed progress falls from 0.172 m/s to 0.146 m/s. Survivor speed falls from 0.180 m/s to 0.161 m/s. The yaw mean goes from −0.7° to −21.8°, and the share past ±15° goes from 22% to 72%. Trials whose pitch exceeds 10° go from 5 to 12. Shoulder mean stays about 20.9°, shoulder travel about 18°, head yaw about 15.7°. The 1161/1200 result does not carry over.

The retune is one posture change on the corrected model only: torso lean from −0.02 rad to −0.04 rad, about the angle of a 4.7 mm forward shift over a quarter-metre height. Lean −0.06 rad was the neighbor and was not kept. On fresh seeds 91200–91279, lean −0.02 is 64/80, yaw mean −15.7°, 69% past ±15°. Lean −0.04 is 71/80, yaw mean +0.8°, 30% past ±15°, and it saves nine falls while adding two. Lean −0.06 is 69/80 with yaw mean +24.8° and 72% past ±15°. Arms stay at a shoulder mean of about 20.9°, shoulder travel about 18°, and head yaw about 15.6–16.0°.

Held-outs of that −0.04 rad lean against the frozen −0.02 rad lean, both on the nominal corrected head:

| Block | Lean −0.04 | Frozen lean −0.02 | Arms free on the corrected head |
|---|---:|---:|---:|
| 92000–92199 | 183/200, progress 0.149 m/s, survivor 0.160 m/s | 175/200, progress 0.143 m/s, survivor 0.160 m/s | 197/200, progress 0.197 m/s, survivor 0.199 m/s |
| 93000–93199 | 176/200, progress 0.144 m/s, survivor 0.162 m/s | 172/200, progress 0.140 m/s, survivor 0.160 m/s | 192/200, progress 0.193 m/s, survivor 0.200 m/s |

Together the retune is 359/400 and the frozen corrected-head controller is 347/400. The 95% Wilson intervals are 86.4% to 92.4% and 83.1% to 89.7%. Across both blocks the retune saves 28 falls and adds 16 (net +12). The exact two-sided McNemar probability of a split at least that uneven, given 44 discordant seeds, is 0.096. The point estimate is +3 percentage points. That is not proof of no effect, and it is not 99.5%. A 199/200 count would not prove an underlying 99.5% either. Shoulder mean is 20.9°, shoulder travel about 18°, head yaw 15.7–16.0°. Main-joint saturation stays about 6.5%. Ankle stall on the first block is about 8.4%.

Over 20 s on seeds 95000–95039 the retune survives 36/40. The yaw median is +4.5°, the 10th to 90th is −40° to +53°, the range is −60° to +65°, and 68% exceed ±15°. The frozen lean on the same seeds survives 32/40 with median −48° and 78% past ±15°. Heading is not held.

The low and high head bounds are scenario bounds, not confidence intervals, and they were not used to choose the lean. On seeds 94000–94039 the −0.04 rad lean is 33/40 at 0.83258 kg, 33/40 at 0.85258 kg, and 24/40 at 0.89458 kg. The heavy, more-forward bound is a real extra loss. No D9 internal lightening and no ballast move was simulated. A later Blender change, not made here, could remove up to about 12 g inside D9 without changing the exterior, or move about 22 g of electronics rearward so some of the existing 25 g ballast is unnecessary. Mounting for that move is not checked. Those savings are not assumed. The corrected model with this retune still needs that design work if the goal remains an observed 99.5% with this arm motion. The exterior stays the large head.

## Eye-driver removal, model correction only

The generator `gen_mjcf_v3.py` adds a 10 g box named `eye_driver`, 20 by 40 by 25 mm, centred on the display bounds mean plus (−35, 0, −5) mm. The BOM and the digital-eyes note say each Waveshare display has its own ESP32-S3 and that no separate eye controller is used. Removing that box is a correction of the model, not a lighter part. The 12 g ODM board stays, because its presence is still marked unknown. The 25 g ballast is still counted once. LW-A is rejected (slice 74.32 g against 71.74 g). LW-B is not accepted and its predicted 2–3 g is not used.

The box centre in the head frame, using the display centroid already in the 0.85258 kg pipeline (29.6, 0, 64.7) mm plus that offset, is (−5.4, 0, 59.7) mm. A note in the design study quotes an approximate centre near (2, 0, 62) mm. That is about 7 mm forward of the generator formula, so the formula was used and the difference is recorded. The box’s own inertia is `m/12` of a uniform 20×40×25 mm brick, taken as aligned with the head frame. Subtracting it once by the parallel-axis theorem from each 852-series tensor gives:

| Scenario | Was | Now | COM x in the head frame |
|---|---:|---:|---:|
| Nominal | 0.85258 kg | 0.84258 kg | −11.70 mm (was −11.62 mm) |
| Low | 0.83258 kg | 0.82258 kg | −12.70 mm |
| High | 0.89458 kg | 0.88458 kg | −10.63 mm |

The COM moves about 0.07 mm rearward, not the half-millimetre guessed from the pitch-axis lever, because the box sits close to the existing head COM in x. All three tensors stay positive definite and the principal moments still satisfy the triangle inequalities. New files, leaving the 0.85258 kg models in place: `twiglet_v3_v335ac_head843.xml`, `twiglet_v3_v335ac_head823.xml`, `twiglet_v3_v335ac_head885.xml`. The canonical XML is unchanged. Held-outs of the 0.85258 kg head, including 359/400, are that older model only.

On the 0.84258 kg head, lean still −0.04 rad, fresh seeds 97200–97279: the frozen pose is 75/80. That draw is exploratory. It is not a qualified rate. A planted-foot ankle offset of −0.03 rad, which had been 39/40 on the 0.85258 kg head (seeds 96000–96039, that older model only), is 77/80 here but the yaw mean rises to +17.2° and 59% of trials pass ±15°. A zero-mean hip-yaw term of +0.025 rad at the arm phase is 73/80. A 5% shorter stride on seeds 97300–97339 is 34/40 against 35/40. Those isolated changes were not held out.

## Joint gait search on the 0.84258 kg head

The inherited 12-parameter gait was fit to the old head. A cross-entropy search on `twiglet_v3_v335ac_head843.xml` moved those parameters together, then, with the arms on, also moved the support gains, a zero-mean arm-phase hip yaw, and a planted-ankle feedforward. Five generations of 12 candidates, 12 fresh train seeds each, for each stage. The vector is `params/head843_search.npy`. `reliable.npy` was not written. Validation seeds 100400–100479 were not in the search: the searched walk with arms is 79/80, all-seed progress 0.156 m/s, 20% past ±15° of yaw, shoulder mean 20.92°, shoulder travel 18.04°, head yaw 15.74°. The inherited gait with the same −0.04 rad lean on those seeds is 68/80, progress 0.143 m/s, 34% past ±15°. Arms-free on that validation block is 77/80 for the inherited gait (progress 0.195 m/s) and 75/80 for the searched gait without the arm wave (progress 0.177 m/s). The search improved the armed walk. It did not produce a better arms-free gait, and the arms-free number is not the armed result.

What moved, inherited to searched: step rate 2.215 to 2.174 Hz, stride 0.173 to 0.160 rad, lift 0.367 to 0.388 rad, gait lean −0.134 to −0.148 rad, ankle-pitch gain −1.20 to −1.32. Support: torso lean −0.042 rad, foot-placement gain 0.52, lateral gain 0.53, arm-phase hip yaw −0.016 rad, planted ankle feedforward −0.018 rad. The arm wave amplitudes were not reduced.

Held-outs, both on the 0.84258 kg head, searched against the inherited gait with lean −0.04 rad:

| Block | Searched | Inherited | All-seed progress | Survivor speed | Shoulder mean / travel | Head yaw | Time past 8° pitch |
|---|---:|---:|---|---|---|---|---|
| 100600–100799 | 197/200 | 185/200 | 0.156 vs 0.152 m/s | 0.158 vs 0.163 m/s | 20.93° / 18.1° | 15.9° | 0.010 vs 0.041 |
| 100800–100999 | 193/200 | 178/200 | 0.152 vs 0.146 m/s | 0.157 vs 0.162 m/s | 20.93° / 18.0° | 15.8° | 0.016 vs 0.053 |

Together 390/400 against 363/400. The 95% Wilson interval for 390/400 is 95.5% to 98.6%. The target 99.5% is above that interval. A count of 199/200 would not prove an underlying 99.5% either. Across the 400 seeds the searched gait saves 32 falls and adds 5 (5 seeds fall on both). The exact two-sided McNemar probability is 7.4×10⁻⁶. The point estimate is +6.8 percentage points. Survivor speed is lower, about 0.158 m/s against 0.162 m/s for the inherited gait on this head. That slower speed is the walk that was measured.

Over 20 s on seeds 101000–101039 the searched gait survives 40/40. The yaw median is −18.5°, the 10th to 90th is −43° to +27°, the range is −50° to +63°, and 78% exceed ±15°. The inherited gait on the same seeds survives 37/40 with 68% past ±15°. Ten-second yaw means near 0° do not describe this 20 s tail.

On seeds 101100–101139 the same searched controller is 40/40 at 0.82258 kg, 40/40 at 0.84258 kg, and 37/40 at 0.88458 kg, where 52% exceed ±15° of yaw. Those bounds were not used to choose the gait. A 16-seed load sample, 101200–101215, all still up: ankle stall 7.7%, hip-pitch stall 1.9%, main-joint stall 4.7%. That sample is not a survival result.

The heavy head bound and the 20 s yaw tail are the remaining gap. No D9 lightening and no ballast change was applied. LW-B is not an accepted part.

## Support-phase heading on the frozen searched gait

`params/head843_search.npy` is unchanged (sha256 `9e8b2caa13bd09a883515bdf7cfca6458480fc0eecdfed0a6977d381f7a5b40c`). The gait vector and the searched support gains stay that file. The new term is a proportional yaw correction on the foot that is carrying the weight. Airborne share is zero when the two soles together are under 20% of weight. The command on the loaded foot is clipped, default ±0.04 rad, and it does not integrate. A sign check on seeds 102000–102007, 16 s, put the useful sign at negative: gain −0.25 cut the yaw median from −25° to −13° and the share past ±15° from 75% to 38%, while +0.25 flipped the median to +48°.

The first search scored 20 s survival, all-seed progress, and the share past ±15° together, four nominal seeds plus two heavy-bound seeds per candidate, generations on seeds 102200 and 102500. It was not allowed to shrink the arm wave, and a walk under 0.10 m/s was penalized. The point it kept is `params/head843_heading.npy`: support gain −0.290, slow-yaw limit 0.0197 rad, arm-phase yaw −0.0124, planted ankle −0.0181. On validation seeds 102800–102839, 20 s, that point is 39/40 with 2.5% past ±15°, against 40/40 and 72% for the frozen search with the support gain at zero. Shoulder mean 20.92°, shoulder travel 18.2°, head yaw 16.0°.

Held out, that stronger gain costs balance. Seeds 103000–103199 are 195/200 on both sides (saves 4, adds 4, McNemar p = 1). Seeds 103200–103399 are 189/200 against 196/200 (saves 1, adds 8, exact two-sided McNemar p = 0.039). Together 384/400 against 391/400 on those seeds. The 95% Wilson interval for 384/400 is 93.6% to 97.5%. Over 20 s on 103500–103539 it is 38/40 with 7.5% past ±15° (median +0.7°, 10th to 90th −5° to +13°), against 40/40 and 60% for the frozen search (median −12°, 10th to 90th −38° to +26°). On the heavy file, seeds 103600–103639, it is 35/40 against 38/40 (saves 1, adds 4). Twelve falls that this gain added and the frozen search walked through were replayed: ten drop the COM through the height limit with roll already 40–44°, two cross the 45° roll line. Yaw at those falls is as large as +87°. The stance-yaw command is saturating and spinning the body. This gain is a Pareto point. It is not a qualified controller. It is not pooled with 390/400.

A fresh screen then walked the gain down, seeds 104000–104031 at 20 s, 104200–104279 at 10 s, and 104400–104415 on the heavy file. The frozen search on that screen is 31/32, 75/80, and 14/16, with 81% of the 20 s trials past ±15°. Gain −0.08, −0.14, and −0.20 keep that 31/32. Gain −0.20 is 80/80 on the 10 s slice and 15/16 on the heavy file, with 22% of the 20 s trials past ±15°. A ±0.015 rad cap on the −0.20 gain lowers that 20 s share to 16% and drops one extra 20 s trial (30/32). The screen selected −0.20 with the default ±0.04 rad clip, the searched slow-yaw limit 0.02 rad, arm-phase yaw −0.0155, and planted ankle −0.0178. That vector is `params/head843_support020.npy`. It does not replace `head843_search.npy`.

Confirmation uses seeds that were not in the search, the screen, or any earlier held-out. The control on every seed is the frozen searched gait with the support gain at zero.

| Block | Support gain −0.20 | Frozen search | All-seed progress | Survivor speed | Past ±15° yaw | Shoulder mean / travel | Head yaw |
|---|---:|---:|---|---|---|---|---|
| 105000–105199, 10 s | 196/200 | 195/200 | 0.156 vs 0.154 m/s | 0.159 vs 0.157 m/s | 6.5% vs 30% | 20.93° / 17.9° | 15.7° |
| 105200–105399, 10 s | 195/200 | 197/200 | 0.155 vs 0.155 m/s | 0.159 vs 0.157 m/s | 8.0% vs 26% | 20.93° / 18.0° | 15.8° |
| 105500–105539, 20 s | 38/40 | 38/40 | 0.157 vs 0.151 m/s | 0.164 vs 0.158 m/s | 15% vs 72% | 20.92° / 18.0° | 15.7° |

Together the 10 s blocks are 391/400 and 392/400. The 95% Wilson intervals are 95.8% to 98.8% and 96.1% to 99.0%. The 99.5% target is above both. These counts are not a population rate. Across the 400 seeds the support term saves 6 falls and adds 7 (net −1). The exact two-sided McNemar probability is 1. Block A is net +1 (p = 1). Block B is net −2 (p = 0.625). The 20 s block is net 0 (one each way). The 20 s yaw median moves from −16.0° to −3.9°, the 10th percentile from −43.5° to −15.1°, and the range from −50° to +47° to −25° to +17°. The yaw mean on that block is −3.5° against −13.1°. The mean is not the tail.

The seven 10 s falls added by the −0.20 gain were replayed. Five hit the height limit with roll already 41–44°, one crosses 45° of roll, and one (105203, at 3.72 s) crosses −45° of pitch. Yaw at those falls stays inside −26° to +26°. Ankle stall on the samples up to the fall is 2–6%. This is the same roll-into-height ending the frozen search already has, plus one backward pitch. It is not the spin seen at gain −0.29.

Scenario bounds, seeds 105600–105639, same seeds both ways. Nominal: 38/40 against 40/40 (net −2, p = 0.5), progress 0.155 vs 0.157 m/s, none past ±15° against 25%. Low, 0.82258 kg: 38/40 against 40/40 (net −2, p = 0.5), 7.5% past ±15° against 35%. High, 0.88458 kg: 37/40 against 34/40 (net +3, p = 0.45), progress 0.144 vs 0.131 m/s, 15% past ±15° against 32%. Heading improves on all three. Survival on 40 seeds does not show a heavy-bound loss for this gain. It also does not show a survival gain.

Load on the two 200-seed blocks, every seed: ankle stall 7.7–7.9% on both controllers, hip-pitch stall 3.1%, main-joint stall 5.4%. The support term does not move stall. Actuator limits, the 45° / 0.6-height fall rule, and the randomization are the ones used throughout. No sole was extended. No mass was invented. LW-B remains unvalidated. The arm wave was not reduced: the measured shoulder mean stays 20.93° and head yaw 15.7–15.8°. Shoulder travel on block A is 17.94° against 17.98° for the frozen search on the same seeds.

The 391/400 figure is this support term on seeds 105000 and 105200. The 390/400 figure is the searched gait with the support gain at zero, on seeds 100600 and 100800. They are different controllers and different seeds.

What is still open: observed survival remains below 99.5%, about 15% of fresh 20 s trials still pass ±15° of yaw, and the heavy bound is a 40-seed check. A larger support gain buys a tighter heading and gives the balance back. That trade is the frontier above.

## State-gated stance yaw

`params/head843_search.npy` and `params/head843_support020.npy` were not overwritten. Support gain −0.20 stays the comparison that cut the heading tail with paired net −1 on seeds 105000–105399 (391/400 against a frozen-search 392/400). It is not promoted. The 390/400 searched-gait count is seeds 100600 and 100800 and is a different controller.

The mechanism measurement is on fresh seeds, not those held-outs. On 106000–106011 the stance foot does reach the extra yaw command: the achieved change is most of the commanded change, and hip-yaw torque stays near 0.02 N·m. Force-share double support (both soles above 30% of the load) almost never occurs, so a double-support-only law would have nothing to act on. On 106100–106111 a constant −0.03 rad stance yaw spins the median heading to +39°, and the same offset on the swing foot spins it to −41°. Splitting a constant between stance and swing still leaves 83% of trials past ±15°. The useful channel is the error-proportional stance command. A roll fade (authority reaches zero by 0.12 rad of roll, and the command is zeroed when roll is past 0.08 rad and still growing) held every trial inside ±15° on that 12-seed slice, with roll peak no higher than the frozen search. That slice is identification, not a rate.

The search that followed keeps the correction on the loaded foot only. Swing weight is zero. The command is `clip(k * yaw_error, ±lim)`, multiplied by `max(0, 1 - |roll| / roll_fade)`, and set to zero when roll is worsening past `roll_hold`. `sway_ph`, `k_lat`, `k_roll_extra`, and `k_place` move inside a tight box around the frozen searched gait. Five generations, eight candidates, each scored on four nominal, two heavy, and two low 20 s episodes (seeds 107000–107019, 107040–107049, 107060–107069). The objective is all-seed progress, minus 0.70 times the share past ±15°, minus 3.5 times the fall fraction, minus a small penalty for time past 8° of roll. A walk under 0.10 m/s or a shrunk arm wave is rejected. Selection seeds 107200, 107300, and 107400 were not in the search. The gate required a 15-point drop in the 20 s share past ±15°, survival within one fall of the frozen search, and the arm wave kept. It passed. The vector is `params/head843_yawstate.npy`: k −0.184, roll fade 0.108 rad, roll hold 0.063 rad, limit 0.037 rad, sway phase 0.708 (frozen 0.681), k_lat 0.519, k_roll_extra 0.262, k_place 0.511.

Held-outs are seeds 108000 and 108200. The control is the frozen searched gait with the support gain at zero. Support −0.20 is reported on the 20 s batch only, as a reference, and was not used to choose this vector.

| Block | Yaw-state | Frozen search | Paired net | All-seed progress | Past ±15° yaw | Shoulder mean / travel | Head yaw |
|---|---:|---:|---|---|---|---|---|
| 108000–108199, 10 s | 194/200 | 195/200 | −1, p = 1 | 0.156 vs 0.155 m/s | 2.5% vs 28% | 20.92° / 18.1° | 15.8° |
| 108200–108399, 10 s | 195/200 | 196/200 | −1, p = 1 | 0.156 vs 0.154 m/s | 2.0% vs 28% | 20.92° / 18.1° | 15.8° |
| 108500–108539, 20 s | 38/40 | 38/40 | 0, p = 1 | 0.159 vs 0.152 m/s | 0/40 vs 65% | 20.92° / 18.2° | 15.9° |

Together the 10 s blocks are 389/400 and 391/400. Wilson 95% intervals are 95.1% to 98.5% and 95.8% to 98.8%. The 99.5% target is above both. The paired count saves 4 and adds 6, net −2, exact two-sided McNemar p = 0.75. That is not a measured survival gain, and it is not a measured survival loss. Survivor speed is 0.159 m/s on both 10 s blocks. The 20 s yaw median moves from −13.5° to +2.6°, the 10th to 90th from −42°…+23° to −0.9°…+5.5°, and the range from −58°…+42° to −6.5°…+11.5°. Zero of 40 trials past ±15° has a Wilson upper end of 8.8%. It does not prove the tail rate is zero. On the same 20 s seeds, support −0.20 is 37/40 with 12.5% past ±15° and a 10th percentile of −14.8°. The fade is tighter than that reference on this batch. Ankle stall on the 20 s batch is 8.6% against 8.8% for the frozen search, hip-pitch stall 3.2% against 3.4%, main-joint stall 5.8% against 6.0%.

The six 10 s falls this law adds are four height drops with roll already 41–44° and two crossings of the 45° roll line. Yaw at those falls is −32° to +25°, not the +87° spin of the saturated −0.29 gain. Seed 108615 on the light file is the exception: pitch −42° with roll only 0.4° and almost no forward travel.

Bounds, seeds 108600–108639. Nominal 39/40 against 39/40, 2.5% past ±15° against 28%. Low 38/40 against 40/40, net −2, p = 0.5. High 36/40 against 39/40, net −3, p = 0.25, progress 0.140 against 0.148 m/s, 5% past ±15° against 32%. Heading improves on the heavy file. Survival there does not. The heavy fall 108605 reaches yaw +56° before the height drop, so on that head the yaw still runs away before roll is large enough for the fade to remove it.

A second search started from that vector, lowered the command cap, and scored three heavy 20 s episodes in every six-seed batch (seeds 109000–109207). Selection on 109400–109623 preferred it to the parent on the heavy slice (23/24 against 21/24) with the 20 s share past ±15° still at 0/24. The vector is `params/head843_yawstate_b.npy`: k −0.181, fade 0.107, hold 0.064, limit 0.029, sway phase 0.772. Held-outs 110000 and 110200, which were not in that search, are 386/400 against 393/400 for the frozen search. Wilson intervals are 94.2% to 97.9% and 96.4% to 99.1%. Paired net −7 (saves 5, adds 12), McNemar p = 0.14. Block A is 190/200 against 194/200. Block B is 196/200 against 199/200. The 20 s batch 110500–110539 is 39/40 against 38/40, median +1.6° against −13.5°, 1/40 past ±15° against 68%, progress 0.163 against 0.152 m/s. Shoulder travel on that batch is 17.9° on both controllers. The heavy bound 110600–110639 is 37/40 against 36/40, net +1, p = 1, with 2.5% past ±15° against 45%. This second vector buys the heavy-file heading and gives nominal walks back. It is a Pareto point. It is not a qualified controller and it is not pooled with 389/400.

The hypothesis consistent with both held-outs: the stance-foot correction removes the slow yaw tail while the trunk is upright, and a persistent command still twists the footprint once the heading error is already large. Fading with roll stops the +87° spin. It does not remove the ordinary roll-into-height fall, and a larger sway-phase move aimed at the heavy head is the suspect for the nominal debit on seeds 110000. Those two changes moved together, so the debit is not pinned on one of them.

No sole was extended. No mass was invented. LW-B is still a local trial, not a validated saving. Actuator limits, the 45° / 0.6-height fall rule, and the randomization are unchanged. The arm wave was not reduced.

## Pitch-window recovery

The yaw-state law stays an unpromoted heading result. This round did not sweep heading gains. It replayed frozen-search falls, then tested one recovery.

On the frozen searched gait, every nominal fall in the replay (12 seeds from 108000 and 110000) and every heavy fall (5 seeds) reaches 8° of forward pitch before 8° of roll. At 0.3 s before the height drop the pitch is still about +10° to +22°, the height is still about 0.93 to 0.96 of the start, the COM is about 30 to 40 mm off the stance foot, and the swing foot is about 90 to 150 mm from the COM. The stance ankle is often past 1.0 N·m and on several seeds is already at −1.91 N·m. Survivors in the same blocks keep their worst roll near 5° to 6° and their height near the start height. The first touch of +6° pitch, around 1.5 s while the arms are rising, is not the fall: some survivors do that and their pitch rate has reversed 0.4 s later, and several falls reverse then fall later anyway.

The cruise placement is already on its clip in that late window. `k_place` is clipped at 0.10 rad and `k_lat` at 0.08 rad. The recovery adds swing-foot placement only after pitch or roll leaves the band survivors occupy: forward extra while pitch is above `pitch_on` and pitch rate is positive, lateral extra while roll is past `roll_on` and still growing. Arms, actuator limits, and the yaw-state heading gains stay fixed. The search is four generations on seeds 112000–112011, 112100–112107, and 112150–112157, mixing nominal, heavy, and low 20 s episodes. The kept caps are 0.070 rad of extra forward placement and 0.042 rad of extra lateral placement.

Selection is seeds 113000–113039, 113100–113123, and 113200–113219. It was not a held-out, and the gate did not open one. Against the yaw-state parent the nominal 10 s block and the 20 s block have no discordant seeds: 38/40 and 24/24 on both. Against the frozen search the nominal block saves 1 and adds 2 (38/40 against 39/40, McNemar p = 1). Heavy is 17/20 against 16/20 for the frozen search (saves 1, p = 1) and 17/20 against the parent. Low is 20/20 against 20/20 frozen and 19/20 parent. All-seed progress on the nominal 10 s block is 0.153 m/s against 0.151 m/s. The 20 s share past ±15° is 0/24, median +2.8°, the same as the yaw-state parent; the frozen search on those seeds is 12/24. Shoulder mean is 20.92°, shoulder travel 18.1° on the 10 s block and 17.8° on the 20 s block for both the recovery and the frozen search, head yaw 15.7°. Ankle stall is 8.0% against 8.1% frozen. On the heavy slice hip-pitch stall is 5.1% against 5.5%.

An extra 0.07 rad at the hip is about 14 mm of foot travel on a 0.2 m leg. The swing foot is about 100 mm from the COM in the pre-fall window, and the hip range cannot close that gap in the remaining part of the step. The recovery therefore does not move the fall count. The saturated stance ankle is still the joint holding the forward pitch, and this family does not give it a new action. No candidate file was promoted. `head843_recover.npy` was not written.

## Early transfer, before the gap opens

A second look at the same frozen-search falls timed the lateral gap. At the pitch-rate burst that precedes the drop, the swing foot is often still 10–30 mm from the COM, and the swing hip still has about 15–40° of room toward its forward stop. Within the next 0.45 s the gap runs out to about 180 mm. The earlier +6° touch, near 1.5 s, is a different event: survivors that reach it peak near 11° and the gap stays under about 50 mm. Several survivors never reach +6° at all.

Shortening the swing once pitch is past that 11° peak, with the pitch rate still positive, is the timing law. It lowers the swing knee and advances the thigh by the same amount a smaller lift would, and it can also shift up to 0.06 rad of the pitch moment onto the stance hip while moving the ankle command off the negative stop. Stall torque is not raised. On the ten already-known nominal falls this is a mechanism check, not a rate: foot-down alone saved 2/10, and foot-down plus the 0.06 rad hip share saved 5/10. The same settings left 10/10 survivors up, at 0.154 m/s against 0.155 m/s, and the gate did not fire on those survivors. Heavy replays went from 0/5 to 1/5.

That does not carry to fresh seeds. The search on seeds 116000, 116100, and 116140, with the yaw-state heading gains held fixed, kept pitch onset 0.187 rad, rate onset 0.15 rad/s, lift reduction 0.145 rad, and hip share 0.061 rad. Selection seeds 117000–117047 were not in that search. The candidate and the yaw-state parent both go 48/48, with the same yaw median and no discordant seeds. The frozen search is also 48/48 on that draw, so the paired net against the best survival baseline is 0. Progress is 0.161 m/s against 0.159 m/s for the frozen search; that difference is the yaw-state gait, because the early law matches the parent. Over 20 s, seeds 117100–117123, the candidate is 22/24 and so is the parent, while the frozen search is 24/24. The share past ±15° is 2/24 against 13/24 for the frozen search. Shoulder mean is 20.9°, 20 s shoulder travel 18.2°, head yaw 15.8°. One of the two falls, seed 117113 at 2.73 s, reached 23° of pitch with the early law already on and still fell. The other, 117115, never exceeded 8.4° of pitch, so a pitch gate cannot see it. Heavy and low slices of 16 seeds were 16/16 for the candidate, the parent, and the frozen search. The selection gate required a paired gain of at least 3 walks and did not open a held-out. No `head843_early.npy` was written.

The phrase “paired net 0” in that paragraph is only the 10 s block, seeds 117000–117047, where the candidate, the yaw-state parent, and the frozen search are each 48/48 and there are no discordant seeds. It does not describe the 20 s block. Seeds 117100–117123, horizon 20 s, are a separate comparison: the candidate and the parent are each 22/24, and the frozen search is 24/24. The candidate adds falls 117113 and 117115 and saves none, paired net −2, McNemar p = 0.5. Those two horizons are not one result.

## Why the early gate did not travel

The 5/10 figure is a replay of frozen-gait walks that had already fallen and that do enter a pitch band above about 12° with the pitch rate still positive. The fresh yaw-state walks mostly never enter that band, so the gate stays idle and the candidate copies the parent. On the 20 s selection the copy is exact, including the two falls. Seed 117113 does enter the band: pitch reaches 23° and the pitch rate peaks near 70°/s, once mid right-swing with the arm sine near −0.83 and once near step transfer with the arm sine near +0.88. The gate is on, and the walk still falls at 2.73 s. Seed 117115 falls at 3.36 s with pitch never above 8.4°, so a pitch gate has nothing to act on. Survivors in that same 20 s block have no pitch-rate peak above 40°/s while pitch is above 6°. The gate is a rescue for one frozen-gait pattern. It is not a prevention, and it is not tuned further here.

## Joint arm phase and step timing

The search that followed leaves the early gate off. It keeps the yaw-state heading gains and the arm and head amplitudes, and it moves step rate, stride, lift, sway phase, arm phase (head phase locked to it), torso lean, foot placement, and hip response together. The objective on every seed is forward progress, minus 5 times the fall fraction, minus a heading-tail term, minus time spent past 10° of pitch, minus a small main-joint stall term. Each generation mixes four nominal 10 s seeds, two nominal 20 s seeds, and two heavy-bound 10 s seeds, starting at 119000. The kept point is step rate 2.196 Hz, stride 0.158 rad, lift 0.395 rad, sway phase 0.681, arm phase 1.16 rad against the current 1.20, lean −0.043 rad, placement gain 0.44, hip gain −0.18.

Selection is seeds 120000–120079 at 10 s, 120300–120331 at 20 s, and 120400–120419 on the low and heavy files. These are not held-outs. A short block with no falls is not a qualification. The gate asked for a paired gain of at least 4 walks against the frozen search on the 80-seed block. The result is the opposite.

| Block | Horizon | Coordinated | Yaw-state parent | Frozen search | Paired vs frozen |
|---|---|---:|---:|---:|---|
| 120000–120079 | 10 s | 77/80 | 77/80 | 79/80 | saves 0, adds 2 (120005, 120041), net −2, p = 0.5 |
| 120300–120331 | 20 s | 32/32, 0 past ±15° | 32/32, 0 past ±15° | 32/32, 72% past ±15° | net 0, no discordant seeds |
| 120400 heavy | 10 s | 19/20 | 18/20 | 20/20 | one added fall |
| 120400 low | 10 s | 20/20 | 20/20 | 20/20 | net 0 |

All-seed progress on the 10 s block is 0.153 m/s against 0.156 m/s for the frozen search and 0.156 m/s for the parent. Survivor speed is 0.159 m/s against 0.158 m/s. On the separate 20 s block, progress is 0.166 m/s against 0.157 m/s frozen and 0.168 m/s parent, and the yaw median is −5.0° against −18.4° and +0.6°. Time with pitch past 10° is 1.1% of the 10 s block against 0.8% frozen, and on the heavy file it is 2.3% against 0.4% frozen and 3.7% for the parent. Main-joint stall on the 10 s block is 5.6% against 5.6%, ankle stall 7.6% against 7.9%. Shoulder mean is 20.92°, shoulder travel about 18.0°, head yaw 15.7°. The 20 s shoulder travel is 17.9° for the candidate and 17.9° for the frozen search.

The search did not move the arm phase far from 1.2 rad, and it did not remove pitch time relative to the frozen gait. Survival on the 80-seed block is worse by two walks. The gate did not open a 400-seed held-out. No `head843_coord.npy` was written. The 32/32 block is a 20 s heading comparison on 32 seeds, not a survival qualification.

## The four-survivor gate was impossible

The gate in `run_head843_coord.py` required `pf["net"] >= 4`. `pf` is the candidate against the frozen search on seeds 120000–120079, horizon 10 s. The frozen search on that block is 79/80, so it fell once. The largest paired net that block can show is +1, if the candidate had gone 80/80 and saved that one fall. A requirement of +4 was arithmetically impossible. The yaw-state parent on the same block is 77/80. Against the parent the largest possible net is +3, and the gate was not written against the parent. The candidate itself is 77/80, paired net −2 versus the frozen search (adds 120005 and 120041, saves none, both fall on 120065). An honest gate, which cannot ask for more saves than the baseline falls, would also have rejected it. The 77/80 candidate is not promoted.

## Rate capture, and why it was rejected

At swing onset on fresh frozen walks, seeds 122000–122015, the swing hip is about 34° short of its forward stop (10th to 90th is 33.7° to 34.2°). Pitch at that instant is near 0°. The median pitch rate is −18°/s. The stance ankle torque, which is MuJoCo `actuator_force` and is a privileged stand-in for servo current, has median 1.91 N·m and 10th percentile 1.45 N·m. On the onsets where the pitch rate is already past 25°/s, that torque’s median is 1.49 N·m and its 90th percentile is 1.91 N·m. The hip has room. The ankle is already on the stall stop. The controller that follows does not read that torque and does not read sole force or the COM. It reads IMU pitch rate and the gait phase, which the controller itself generates.

The law adds a swing-hip offset only while pitch rate is forward, with its own cap, so the existing angle clip cannot eat it. It does not add a stance-ankle command. Training on seeds 123000, 123040, and 123080 kept k 0.217, cap 0.060 rad, and rate onset 0.264 rad/s. That cap is about 3° of the 34° of room.

Selection against the frozen search, horizons kept apart:

| Block | Horizon | Capture | Frozen search | Paired |
|---|---|---:|---:|---|
| 123500–123599 | 10 s | 93/100 | 97/100 | |
| 123600–123699 | 10 s | 95/100 | 100/100 | |
| Combined, 10 s only | 10 s | 188/200 | 197/200 | net −9, p = 0.035 |
| 123800–123831 | 20 s | 29/32 | 31/32 | net −2 |
| 123900 heavy | 10 s | 20/20 | 19/20 | net +1 |
| 123900 low | 10 s | 18/20 | 20/20 | net −2 |

Wilson 95% intervals on the combined 10 s selection, which is not a held-out, are 89.8% to 96.5% for 188/200 and 95.7% to 99.5% for 197/200. The frozen gait fell 3 times on those 200 seeds, so a gain of 3 was possible and a gain of 4 was not. The result is a loss of 9. All-seed progress on the two 10 s blocks is 0.147 and 0.149 m/s against 0.154 and 0.157 m/s. On the 20 s block it is 0.129 m/s against 0.154 m/s, and the yaw median is −49° against −22°. Shoulder mean stays 20.93°, shoulder travel about 18.1°, head yaw about 15.7°. Heavy survival is 20/20 against 19/20, and the yaw share past ±15° on that file is 90% against 50%. The heading constraint is not met there. The gate did not open a held-out. No `head843_capture.npy` was written.

The unused hip travel is real, and spending it on forward pitch rate makes the walk slower, yaws it, and drops more trials. That family stops here. The cap is not being raised.

## What the 1.91 N·m figure is

The ankle actuator is a MuJoCo motor with gear 1 and `ctrlrange` −1.91 to 1.91. On loaded-stance samples from seeds 122100–122107, `ctrl` and `actuator_force` differ by 0. The 1.91 N·m value is the commanded servo torque about the joint axis after the position loop and the speed line, not a separate contact moment and not a sum of hip, knee, and ankle.

The servo law is `tau = clip(stall * u − (stall / w0) * w, ±stall)` with stall 1.91 N·m and no-load speed 5.45 rad/s. On the samples already at the rail, the median joint speed is 9°/s and only 11% exceed 1 rad/s. The motoring headroom left by back-EMF is still 1.91 N·m. Saturation is the stall clip, not the speed-torque slope.

Over 1986 loaded-stance samples (normal force above 8 N, no falls in that draw) the torque median is −0.11 N·m, the 10th to 90th is −1.76 to +0.62, 5.6% of samples are on the −1.91 rail, and none are on the +1.91 rail. The swing-onset sample is a different cut. On seeds 122000–122015, at the kinematic phase switch, the foot that is not the one just labeled as swinging has median torque +1.85 N·m and 40% of those instants are on the +1.91 rail. A later check on seeds 125000–125005 found 99% of those onset samples have normal force under 2 N, so that foot is in the air, and the command is about 10° more positive than the joint. The positive rail is an airborne ankle at the phase switch. The negative rail is a loaded foot. They are not the same event.

On the negative rail the ankle command is 16° more negative than the joint. The position loop, gain 12 N·m/rad, computes about 3.3 N·m and the clip leaves about 1.4 N·m of that command unsatisfied. That 1.4 N·m is unmet position-loop command. It is not, by itself, a measured external moment the ground requires. The contact moment about the ankle axis, a privileged contact calculation and not an inverse-dynamics solution, has median +0.24 N·m and correlates with servo torque at −0.25. A static shift of the head COM is only an analogy for a constant bias. It is not a proof that no controller can remove the tracking error. The 170 mm figure is withdrawn.

## Stance hip and knee, same fresh seeds

The redistribution does not add an ankle command. When an ankle command is already more than 0.10 rad negative of the joint, the hip and knee of that leg move by the same amount so the flat-sole sum is unchanged. On seeds 122300–122323 the frozen search is 23/24, progress 0.152 m/s, ankle stall 7.7%. The crouch direction fires on a median of 407 steps and is 22/24, progress 0.137 m/s, ankle stall 7.4%, and it saves 122320 while adding 122308 and 122313. Pulling the ankle command toward the joint as well, which lowers duty and does not add torque, drops ankle stall to 5.1% and survival to 20/24, progress 0.127 m/s. On that small block, backing the command off the rail coincided with more falls. That is not proof the clipped command was a necessary ground moment. Neither direction was taken to a held-out. No geometry was changed. The 10 g eye-driver box was not removed again.

The large negative error is not a pitch spike. On seeds 125000–125005, samples with ankle error below −0.12 rad have median body pitch 0.2°. Only 39% of them are on a foot with normal force above 8 N, and almost none are at transfer. On loaded feet with body pitch between −5° and +2°, the median error is +5° and 28% are still below −0.12 rad. The ankle target disagrees with the joint while the body is nearly level.

## Trackable leg trajectory

The search changes the commanded leg shape: step rate, stride, lift, crouch, lean, the ankle-pitch gain, and the ankle offset, plus torso lean and the hip response. Ankle offset is allowed from −0.40 to +0.30 rad, inside the ankle soft limit and outside the old ±0.15 box. No ankle command is eased after the error appears, and no swing-hip offset is added. Each generation scores fresh nominal 10 s, nominal 20 s, heavy, and low seeds together. A fall is penalized apart from average progress. A large negative ankle error is penalized as impossible tracking, not as a known ground moment. Training seeds start at 125200.

The kept gait is step rate 2.301 Hz, stride 0.103 rad against 0.160, lift 0.358, crouch 0.172, lean −0.130, ankle-pitch gain −1.01 against −1.32, ankle offset −0.130, torso lean −0.029, hip gain −0.169. The vector is `params/head843_traj.npy`. The script also required progress within 0.03 m/s of the frozen gait, so it printed the gate closed. This gait walks at 0.110 m/s. The 200-seed 10 s selection, seeds 126000–126199, was 200/200 against 197/200, and the separate 20 s block 126400–126439 was 40/40 against 40/40. That selection is not the result below.

Held-out, seeds 127000–127199 and 127200–127399, horizon 10 s:

| Block | Trackable gait | Frozen search | Paired |
|---|---:|---:|---|
| 127000–127199 | 199/200 | 193/200 | saves 6, adds 0, both fall on 127035, p = 0.031 |
| 127200–127399 | 200/200 | 193/200 | saves 7, adds 0, p = 0.016 |
| Combined | 399/400 | 386/400 | saves 13, adds 0, p = 2.4×10⁻⁴ |

Wilson 95% intervals are 98.6% to 99.96% for 399/400 and 94.2% to 97.9% for 386/400. The 399/400 interval includes 99.5% and its lower end is 98.6%. One miss in 400 does not establish a 99.5% floor. All-seed progress is 0.110 m/s against 0.154 m/s. Survivor speed is 0.110 m/s against 0.158 m/s. The shorter stride is the speed tradeoff. It is not a stand: the robot still travels about 1.1 m in 10 s. Shoulder mean is 20.9° on both. Measured shoulder travel is 17.9° against 18.1°. Head yaw is 15.9° against 15.7°. The sine amplitudes were not reduced. Ankle stall is 3.6% against 7.8%. The fraction of steps with an ankle command more than 0.12 rad negative of the joint is 0.58 against 0.65. Time with body pitch past 10° is under 0.1% against about 0.9%.

The 20 s block 127500–127539 is a separate horizon: 40/40 against 39/40, net +1, p = 1. Progress 0.113 m/s against 0.155 m/s. Yaw median −2.6° against −12.5°. The share past ±15° is 32% against 62%, and the 90th percentile is still +38°. Bounds on seeds 127600–127639, also not pooled with the 400: nominal 40/40 against 40/40, low 40/40 against 38/40, heavy 40/40 against 38/40.

LW-B was checked independently and rejected: the mesh has non-manifold seam fragments, and the diagnostic slice is 72.04 g against the D9 slice of 71.74 g. It is not an accepted saving and it is not in the model. The 10 g eye-driver box is already absent from the 842.58 g files and was not removed again. The 25 g ballast remains counted once. The 12 g board remains.

## Preregistered qualification of the frozen trajectory

`params/head843_traj.npy` was hashed before any of these trials and was not changed. sha256 `1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc`. The evaluator hashes are in `results/head843_traj_qual_prereg.json`, written before the run. Seeds 130000–133999 (4000, nominal 10 s), 134000–134399 (400, nominal 20 s), 135000–135199 (200, 0.82258 kg, 10 s), and 136000–136199 (200, 0.88458 kg, 10 s) were unused. Both the candidate and the frozen search were run on every one of those seeds. Nothing stopped early. The 399/400 result on seeds 127000–127399 is not included.

The declared support criterion is a two-sided 95% Wilson lower bound of at least 99.5% on the candidate’s nominal 10 s trials only. It says nothing about physical safety, the 20 s horizon, or the mass bounds.

The candidate is 3978/4000, rate 99.45%. The Wilson interval is 99.17% to 99.64%. The Clopper–Pearson interval is 99.17% to 99.66%. The lower bound is below 99.5%, so the criterion is not met. The frozen search on the same 4000 seeds is 3889/4000. The candidate saves 107 of those falls and adds 18, net +89, McNemar p = 1.3×10⁻¹⁶. All-seed progress is 0.110 m/s against 0.154 m/s. Survivor speed is 0.110 m/s against 0.158 m/s. That slower speed is the accepted tradeoff. Shoulder mean is 20.90° against 20.93°. Measured shoulder travel is 17.85° against 18.02°. Head yaw is 15.82° against 15.72°. Ankle stall is 3.5% against 7.6%. The fraction of steps with the ankle command more than 0.12 rad negative of the joint is 0.58 against 0.65. Yaw median is −0.2° against −3.3°. The share past ±15° in 10 s is 7.8% against 30%. The 22 candidate falls are seeds 130025, 130164, 130191, 130241, 130614, 131055, 131319, 131321, 131338, 131567, 131569, 131753, 131803, 131847, 131993, 132261, 132334, 132441, 132599, 132671, 132773, and 133950. Fall times run from 3.43 s to 8.17 s, median 4.05 s. Median distance at the fall is 0.34 m. None fall before 3 s. Fourteen of the 22 have yaw past ±15° at the fall.

The 20 s block is separate: 398/400 against 390/400, saves 10, adds 2, net +8, p = 0.039. Progress 0.113 m/s against 0.157 m/s. The share past ±15° is 31% against 60%. The 10th to 90th is −16° to +28°, and the range is −36° to +86°. The 32% tail on the earlier 40-seed block is the same limitation at this larger count. It was not retuned. The low head is 199/200 against 198/200, net +1, p = 1. The heavy head is 200/200 against 190/200, net +10, p = 0.002. Those bounds are not a 99.5% test and are not pooled with the 4000.

## Backward pitch, then a heading trim on the short step

The 22 misses on seeds 130000–133999 were read after that qualification. `params/head843_traj.npy` was not changed. Sixteen of the 22 reach −8° of pitch before ±15° of yaw or ±8° of roll. Yaw past ±15° leads those body-angle events by 0.3 s or more in 5 of the 22. At 0.4 s before the fall, the pitch median is −16.1° (range −17.2° to −15.4°), the pitch-rate median is −27.6°/s, and the roll median is −0.8°. Twenty-two survivors that finish past ±15° of yaw, sampled from 297 such trials in the 4,000, all cross 15° of yaw and none reach ±8° of pitch or roll. Their late pitch stays between −4.0° and −0.4°. A yaw past 15° at the fall is associated with the miss. The state that separates the misses is backward pitch with the pitch rate still negative.

The trim was trained on the frozen short-step gait. The long-stride yaw gain was left behind. On fresh 20 s seeds 140100–140115, a yaw gain of −0.12 leaves 14 of 16 trials past ±15°, median yaw +74°, progress 0.073 m/s. A gain of +0.12 leaves 0 of 16 past ±15°, median −3.4°, progress 0.114 m/s. On the 22 known misses, a mechanism check and not a selection set, the forward stance-thigh sign survives 16/22 and the opposite sign survives 3/22. The kept law is `short_step_balance`, called after the slow-yaw integral and the arm-phase yaw. While pitch is below −0.087 rad and the pitch rate is negative, the stance thigh moves forward and the swing foot moves less forward, clipped at 0.06 rad. Heading error at gain 0.125 is added on the phase-stance hip, the added command clipped at 0.03 rad and the hip command at 0.07 rad. There is no sole-force term. The vector is `params/head843_shortbal.npy`, sha256 `52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5`.

Training seeds are 140200–140607. Selection 141000–141199 is 200/200 against 199/200, and 141300–141339 is 40/40 with 0% past ±15° against 37.5%. The fresh screen 142000–142399 is 400/400 against 399/400, and 142500–142539 is 40/40 with 0% past ±15° against 35%. That screen is not the qualification below.

## Preregistered qualification of the short-step trim

`results/head843_shortbal_qual_prereg.json` was written at 2026-11-08T02:17:09Z, before these trials. The `sim/manoeuvre.py` sha256 in that file is `48ae37b20460568eff53ae8a625c3a848ca016f1e684f667d3ffc7e9d8e8d4cd`. Seeds 150000–153999 (4000, nominal 10 s), 154000–154399 (400, 20 s), 155000–155199 (200, 0.82258 kg), and 156000–156199 (200, 0.88458 kg) were unused. The paired baseline is the frozen short-step gait with this trim absent. The 3978/4000 count on 130000–133999 is unchanged and is not included. All eight blocks finished. Nothing stopped because an interval had already cleared or missed.

The declared support criterion is a two-sided 95% Wilson lower bound of at least 99.5% on the candidate’s nominal 10 s trials only.

The candidate is 3996/4000, rate 99.90%. The Wilson interval is 99.74% to 99.96%. The Clopper–Pearson interval is 99.74% to 99.97%. The lower bound is above 99.5%, so the declared criterion is met for seeds 150000–153999 at 10 s on the 0.84258 kg head. The short-step gait without the trim, on these same seeds, is 3994/4000, Wilson 99.67% to 99.93%. The trim saves 150272, 152339, 152805, and 153782, and adds 150216 and 150258. Both fall on 151246 and 152541. Net +2, McNemar p = 0.69. Survival on this block moves by two trials. Heading moves by a large amount: 2 of 4000 trials finish past ±15° (0.05%) against 7.43%. The yaw median is −2.9° against −0.5°, and the 10th to 90th is −6.3° to +1.0° against −8.6° to +12.2°. All-seed progress is 0.112 m/s against 0.110 m/s. Survivor speed is 0.112 m/s against 0.110 m/s. Shoulder mean is 20.90° on both. Measured shoulder travel is 17.85° on both. Head yaw is 15.79° against 15.83°. Ankle stall is 3.52% of samples against 3.53%. Ankle stall is the share of samples with |torque| ≥ 1.90 N·m. The 7.6 figure for the long-stride frozen search is 7.6% of samples, on that definition.

The four candidate falls are 150216 at 3.85 s (yaw 1.5°), 150258 at 4.09 s (yaw 36.5°), 151246 at 3.65 s (yaw 26.9°), and 152541 at 4.83 s (yaw 10.9°). At 0.4 s before each fall, pitch is between −16.3° and −15.3°, the pitch rate is still negative, and roll is a few degrees. The two falls the untrimmed gait does not have, 150216 and 150258, are that same pitch state. On 150216 the yaw stays inside ±15°. At the measured pitch and pitch rate, the trained gains already ask for more than the 0.06 rad clip, so the catch is on its limit while the pitch is still growing. A larger clip was not tested.

The 20 s block is a separate horizon: 399/400 against 399/400, net 0, p = 1. Its Wilson lower bound is 98.60%, so the 99.5% statement does not cover 20 s. Progress is 0.117 m/s against 0.113 m/s. The share past ±15° is 0% against 38.8%. Candidate yaw on that block runs from −14.1° to +14.6°. The one candidate fall, 154186 at 4.66 s, is pitch −15.6° and roll −5.2° at 0.4 s before the fall. The low head is 199/200 against 199/200 on the shared fall 155188, Wilson lower bound 97.22%. The heavy head is 200/200 against 200/200, Wilson lower bound 98.12%. Those bounds stay separate from the 4,000.

The 3978/4000 qualification of the untrimmed short step remains the count for seeds 130000–133999, where the Wilson lower bound is 99.17%. The two 4,000-seed draws are separate.

## Validation of the frozen trim

This run does not change the trim. `params/head843_shortbal.npy` remains sha256 `52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5`, gains pitch onset 0.08724 rad, pitch gain 0.93511, rate gain 0.22824, yaw gain 0.12509, pitch sign +1, clip 0.06 rad. `params/head843_traj.npy` remains `1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc`. `sim/manoeuvre.py` remains `48ae37b20460568eff53ae8a625c3a848ca016f1e684f667d3ffc7e9d8e8d4cd`, `sim/simlib.py` `b0e853b8fb70ad4b31ab38115be887cf8235c6ed53747223aab5b9562d40a3a7`, `sim/episode.py` `4293019ded11063a1d597e7216e2134ce24a0f255b857298bc337e84f2ecccad`. The canonical XML and the scene hashes are unchanged. Physics, stall clip, contact, fall rule, and randomization are the same ones named in the preregistration. The head files stay 0.84258 kg, 0.82258 kg, and 0.88458 kg. The 25 g ballast is still counted once and the 12 g board is still in the head. No larger clip was run.

Provenance of the 150000 qualification, from file times before this validation started. The trajectory file was frozen at 2026-11-08T01:47:34Z. Its own qualification was preregistered at 2026-11-08T01:52:02Z on seeds 130000–136199 and remains 3978/4000. The miss timeline is 2026-11-08T02:08:29Z. The balance law in `manoeuvre.py` dates from 2026-11-08T02:10:25Z. Training, four generations, used seeds 140200–140215, 140400–140407, 140500–140507, and 140600–140607. The sign check on 140100–140115 and on the 22 known misses is not a selection set. Selection was 141000–141199, 141300–141339, and 141400–141423, checkpoint 2026-11-08T02:11:57Z. The trim file was written at 2026-11-08T02:12:48Z. The 400-seed screen, 142000–142619, was written at 2026-11-08T02:14:08Z after that save and is not a qualification. The 150000 preregistration is 2026-11-08T02:17:09Z and the result file finished at 2026-11-08T02:30:21Z.

The raw block `nom20_cand` in `head843_shortbal_qual.json` has 400 rows and 399 survivors. The one fall is seed 154186 at 4.664 s, terminal yaw 14.6°. So 399/400 is that exact count. The raw block `lo10_cand` has 200 rows and 199 survivors. The one fall is seed 155188 at 3.476 s, terminal yaw 20.7°. A replay of 154186 for the logger left the fall time and the terminal yaw where they were, and the largest |yaw| along that one trajectory was 20.8°. The 0% past ±15° on that 400 is the yaw at the end of each trial. It is not a statement that yaw stayed inside ±15° the whole time. Peak yaw was not stored for those 400.

`results/head843_shortbal_val_prereg.json` was written at 2026-11-08T02:37:53Z, before the trials below. Seeds 180000–183999 (4000, nominal 20 s), 184000–187999 (4000, nominal 10 s), 188000–188999 (1000, 0.82258 kg, 10 s), and 189000–189999 (1000, 0.88458 kg, 10 s) were unused. The candidate was run alone. All four blocks finished. Nothing stopped because an interval had already cleared or missed. Each horizon and each head mass has its own two-sided 95% Wilson criterion. They are not pooled with each other or with 3996/4000, 399/400, or 3978/4000. This is a simulated distribution, not a hardware certification.

| Block | Seeds | Count | Wilson 95% | Clopper–Pearson | Criterion |
|---|---|---:|---|---|---|
| Nominal 20 s | 180000–183999 | 3990/4000 | 99.54% to 99.86% | 99.54% to 99.88% | met |
| Nominal 10 s, replication | 184000–187999 | 3997/4000 | 99.78% to 99.97% | 99.78% to 99.98% | met |
| 0.82258 kg, 10 s | 188000–188999 | 996/1000 | 98.98% to 99.84% | 98.98% to 99.89% | not met |
| 0.88458 kg, 10 s | 189000–189999 | 1000/1000 | 99.62% to 100% | 99.63% to 100% | met |

On the 20 s block, all-seed progress is 0.116 m/s and survivor speed is 0.117 m/s. Shoulder mean is 20.90°, shoulder travel 17.85°, head yaw 15.79°. Ankle stall is 3.63% of samples. On the 10 s replication, progress is 0.112 m/s, survivor speed 0.112 m/s, shoulder mean 20.90°, shoulder travel 17.85°, head yaw 15.79°, ankle stall 3.53%. The low head walks at 0.114 m/s with shoulder 20.89°, travel 17.85°, head 15.68°, ankle stall 3.36%. The heavy head walks at 0.109 m/s with shoulder 20.91°, travel 17.87°, head 15.98°, ankle stall 3.82%. Ankle stall remains the share of samples with |torque| ≥ 1.90 N·m.

Heading has three denominators. Terminal yaw of every trial, including the yaw at the fall, is 10/4000 past ±15° on the 20 s block, 1/4000 on the 10 s replication, 5/1000 on the low head, and 2/1000 on the heavy head. Terminal yaw of survivors only is 3/3990, 0/3997, 1/996, and 2/1000. The largest |yaw| at any logged sample is a third count: 30/4000, 17/4000, 15/1000, and 2/1000. Twenty of the 20 s trials finish inside ±15° after having been outside it, and 16 of the 10 s replication trials do the same. The median peak |yaw| on the 20 s block is 8.7°, the 90th percentile is 11.2°, and the extreme is 49.2°. Three survivors finish past ±15°: 181655 at −15.1°, 182545 at −15.3°, and 183492 at −19.1°. A trial that is still upright is not a trial that stayed on heading.

Every fall in these four blocks meets the predeclared backward-pitch rule: pitch below −8° and pitch rate still negative at the sample nearest 0.4 s before the fall. The 20 s falls are 180357, 180524, 180734, 181242, 181875, 181928, 182113, 182309, 182624, and 182712. Pitch at that sample is −14.9° to −15.7°, and roll is a few degrees. Two of them, 181875 and 181928, finish at −3.7° and +1.5° of yaw. The 10 s replication falls are 185499, 186970, and 187386, the same pitch state. The low-head falls are 188153, 188453, 188721, and 188743, pitch −15.9° to −16.4°. The heavy head has no fall. The clip stayed at 0.06 rad.

## Low head, one fixed 4000

The 1000-seed low block, seeds 188000–188999, is 996/1000. The point estimate is 99.6% and the Wilson lower bound is 98.98%, so that block does not meet 99.5% and does not rule it out. It stays inconclusive. A second sample is a new experiment with its own seeds and its own interval. It does not repair the first interval, and running samples until one of them clears the bar would not be a qualification. This 4000 is that one predeclared experiment. There is no third extension.

`results/head843_shortbal_low4000_prereg.json` was written at 2026-11-08T02:57:55Z, before these trials. The trim hash was still `52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5`. The low file is `twiglet_v3_v335ac_head823.xml`, 0.82258 kg, sha256 `cc443192e694413eb1ce627017a9a67c25588d47b84668894c015db53e74f182`. Seeds 190000–193999 were unused. All 4000 finished. Nothing stopped early.

The count is 3961/4000, rate 99.025%. The Wilson interval is 98.67% to 99.29%. The Clopper–Pearson interval is 98.67% to 99.31%. The Wilson lower bound is below 99.5%, so the criterion is not met. This block is not pooled with 996/1000 or with the nominal and heavy blocks. All-seed progress is 0.113 m/s. Survivor speed is 0.114 m/s. Shoulder mean is 20.89°, shoulder travel 17.88°, head yaw 15.71°. Ankle stall is 3.46% of samples with |torque| ≥ 1.90 N·m.

Finish yaw past ±15° is 27/4000 of all trials and 3/3961 of survivors (190902 at +38.1°, 192423 at +18.6°, 193838 at +16.2°). Peak |yaw| along the walk is past ±15° in 75/4000 trials. Forty-eight of those finish back inside the band. Median peak |yaw| is 8.6°.

All 39 falls are the predeclared backward-pitch class. At 0.4 s before the fall, pitch is between −16.3° and −15.0°, the pitch rate is still negative, and roll is between −6.1° and +5.3°. Fifteen of the 39 finish inside ±15° of yaw. The seeds are 190007, 190039, 190107, 190295, 190313, 190321, 190325, 190495, 190533, 190659, 190688, 191425, 191441, 191580, 191614, 192012, 192036, 192076, 192173, 192386, 192558, 192623, 192641, 192730, 192806, 192937, 192939, 192978, 193079, 193364, 193369, 193489, 193526, 193553, 193645, 193750, 193969, 193975, and 193999.

The nominal 10 s replication of this same trim fell 3 times in 4000. The low head fell 39 times in 4000. The event is the same −16° pitch with the catch already on its 0.06 rad clip in the earlier nominal falls. The low-head question for this controller is closed. Another 4000 of the same law would be a sample-size search. A later design, if there is one, has to change the backward-pitch response on the 0.82258 kg head and then face a new preregistered test. The nominal 10 s, nominal 20 s, and heavy 10 s qualifications of this trim stay as they are.

## Qualification manifest

The checkpoint is `results/head843_shortbal_manifest.json`. Scopes that meet the Wilson bar, each on its own seeds:

| Scope | Seeds | Count | Wilson 95% |
|---|---|---:|---|
| Nominal 10 s, 0.84258 kg | 150000–153999 | 3996/4000 | 99.74% to 99.96% |
| Nominal 20 s, 0.84258 kg | 180000–183999 | 3990/4000 | 99.54% to 99.86% |
| Nominal 10 s replication, 0.84258 kg | 184000–187999 | 3997/4000 | 99.78% to 99.97% |
| Heavy 10 s, 0.88458 kg | 189000–189999 | 1000/1000 | 99.62% to 100% |

The 17 falls inside the 180000 validation are all backward pitch: 10 on the 20 s block, 3 on the 10 s replication, and 4 on the low 1000. Survival on those blocks is not the heading result. On the 20 s block, 10/4000 finish past ±15°, 3/3990 survivors do, and 30/4000 reach that peak during the walk.

Scopes that are not qualified:

- Low 10 s, seeds 190000–193999: 3961/4000, Wilson lower 98.67%. Closed for this controller.
- Low 10 s, seeds 188000–188999: 996/1000, Wilson lower 98.98%. Inconclusive, and not pooled with the 4000.
- Untrimmed short step, seeds 130000–133999: 3978/4000, Wilson lower 99.17%.
- Low head at 20 s: not run.
- Heavy head at 20 s: not run.
- Any horizon past 20 s: not run.
- Real hardware: not tested.
- Canonical `reliable.npy`, the canonical XML, and the scene: unchanged. This trim does not replace them.

## Earlier pitch-rate branch

The frozen trim stays `params/head843_shortbal.npy`, sha256 `52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5`. Its qualifications are not this candidate’s. On the 39 low-head falls from seeds 190000–193999, replayed with that trim, the low head falls 39/39, the 0.84258 kg head falls 12/39, and the 0.88458 kg head falls 1/39. Sixteen low-head survivors on nearby seeds never reach −5°. At −3°, where the frozen law is still off, the fall seeds already have pitch rate about −13.5°/s on every head. From −3° to −5° the low head’s rate grows to −16.3°/s, the nominal head’s rate eases to −12.4°/s, and most heavy trials never reach −5°. The head’s own pitch inertia differs by about 0.6% across the three files. The lighter head, whose COM sits about 1 mm further back, keeps gaining backward rate while the controller is silent.

At the −5° onset the applied hip offset is about 0.05 rad, the 0.06 rad cap is not what limits it, the forward soft stop is about 22° away, and the hip torque median in that band is 1.12 N·m with 5% of samples at the 1.91 N·m rail. A larger clip was not the measured shortage. The shortage is the wait until −5°.

The new file is `params/head843_earlyrate.npy`, sha256 `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`. It keeps the frozen late gains and the 0.06 rad cap. If pitch is already below 0.0267 rad and pitch rate is more backward than 0.194 rad/s, the rate term alone moves the stance thigh forward and the swing foot less forward, using IMU pitch, IMU pitch rate, and the gait phase. It does not read mass or sole force. `results/head843_earlyrate_qual_prereg.json` was written at 2026-11-08T03:17:15Z. The evaluator sha256 is `96d026643c0bb50131d9b02b7d49eaee8daa549fee5a774063d4061d094b3a74`. Seeds 210000–213999, 214000–217999, 218000–221999, and 222000–222999 were unused. All four blocks finished, candidate and frozen trim, with no early stop.

| Block | Seeds | Early-rate | Frozen trim | Wilson 95% on the early-rate count | Criterion |
|---|---|---:|---:|---|---|
| Low 10 s, 0.82258 kg | 210000–213999 | 3999/4000 | 3976/4000 | 99.86% to 99.996% | met |
| Nominal 10 s, 0.84258 kg | 214000–217999 | 4000/4000 | 3994/4000 | 99.90% to 100% | met |
| Nominal 20 s, 0.84258 kg | 218000–221999 | 4000/4000 | 3994/4000 | 99.90% to 100% | met |
| Heavy 10 s, 0.88458 kg | 222000–222999 | 1000/1000 | 1000/1000 | 99.62% to 100% | met |

Clopper–Pearson intervals are 99.86% to 99.999% on the low block, 99.91% to 100% on both nominal blocks, and 99.63% to 100% on the heavy block. They are not a second gate. The low block saves 23 frozen-trim falls and adds none, net +23. The nominal 10 s and 20 s blocks each save 6 and add none. These intervals are not pooled with each other or with any shortbal block, including 3961/4000 and 3996/4000.

On the low block, progress is 0.112 m/s against 0.114 m/s and survivor speed is 0.112 m/s against 0.114 m/s. Shoulder mean is 20.90°, shoulder travel 17.88°, head yaw 15.75°. Ankle stall is 3.29% of samples against 3.41%. On nominal 10 s, progress is 0.110 m/s against 0.112 m/s, shoulder mean 20.90°, travel 17.86°, head yaw 15.81°, ankle stall 3.43%. On nominal 20 s, progress is 0.115 m/s against 0.117 m/s, shoulder 20.90°, travel 17.85°, head 15.82°. On the heavy head, progress is 0.108 m/s against 0.109 m/s, shoulder 20.91°, travel 17.74°, head 15.88°.

Finish yaw and peak yaw still differ. On the low block, 1/4000 trials finish past ±15° and 0/3999 survivors do. Peak |yaw| exceeds ±15° in 37/4000 trials, and 36 of those finish back inside the band. On nominal 10 s the finish count is 0/4000 and the peak count is 10/4000. On nominal 20 s the finish count is 2/4000, both survivors (218302 at −15.5°, 219112 at −15.3°), and the peak count is 17/4000. On the heavy head the finish count is 1/1000, seed 222409 at −15.9°.

The one low-head miss is seed 212558 at 3.70 s. Pitch 0.4 s earlier is −15.8° with the pitch rate still negative, and the finish yaw is +38.2°. The frozen trim also falls on that seed. The other 23 low-head falls of the frozen trim on these seeds are the same backward-pitch class.

Low head at 20 s is still not run. Heavy head at 20 s is still not run. Hardware is not tested. The canonical model and `reliable.npy` are unchanged. The 400-seed screen that preceded this preregistration, 400/400 against 397/400 on seeds 202000–202399, is not part of these intervals.

## Manoeuvre test of the frozen early-rate gait

This is a test of `params/head843_earlyrate.npy` (`d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`). The file was not changed. The commands and the pass rules were written to `results/head843_earlyrate_manoeuvre_protocol.json` at 2026-11-08T06:08:31Z, before the trials. Nominal head first. A mass-file check ran only where that protocol’s nominal screen was a perfect task success. None of these samples is a 99.5% claim: a perfect 20-seed block has a Wilson 95% lower bound of 83.9%.

The qualified gait holds the yaw it had at reset. The slow-yaw integral and the stance hip-yaw trim both use that yaw, and they replace the hip-yaw command after `Gait.turn` and after the old single-slew writer. A commanded turn was the existing slew: kp 0.6, kd 0.02, hip-yaw limit 0.07 rad, command sign −1. Gentle arcs were ±20° from 3 s to 8 s (4°/s). The larger commands were ±45° from 3 s to 6 s (15°/s), ±90° from 3 s to 7.5 s (20°/s), and ±180° from 3 s to 9 s (30°/s). A task success had to be upright, finish within 15° of the command, carry the command’s sign, and cover at least half the commanded angle. Upright alone was not a success.

Every slew screen was 6/6 upright and 0/6 on that task. Final yaw stayed near the straight-walk drift, whose own 8-seed median is −3.1°. The final heading error was about the commanded angle: about +23° and −18° for the 20° arcs, about ±45° for the 45° commands, about +93° and −88° for the 90° commands, and about 180° for both 180° commands. Constant `Gait.turn` biases of ±0.03 rad and ±0.08 rad also left the yaw inside that straight-walk band. Those biases are erased. In-place turning, sidestepping, a waypoint slalom, and a restart after a stop are not commands in this harness. They were not imitated by rotating the world or by editing the initial yaw.

Stride scale 0.7 and 1.3, against a 0.11 m/s reference, were 8/8 on the screen and 20/20 on the predeclared held-out (seeds 231100–231119 and 231140–231159). Median progress was 0.076 m/s and 0.138 m/s. Wilson 95% on each 20-seed held-out is 83.9% to 100%. The same scales were 8/8 on both the 0.82258 kg and the 0.88458 kg files. Scaling step rate and stride together by 0.85 and by 1.15 was 8/8 on the nominal screen, progress 0.090 m/s and 0.122 m/s. The 0.85 scale was 6/8 on the low head and 7/8 on the heavy head. Ankle stall on the faster scales is about 5% to 6% of samples, against about 3% on the straight screen.

A negative stride, the gait’s own sign, walked backward on 6/6 seeds at about −0.096 m/s. Yaw on those six runs ran from −13° to +25°. That is a screen of a sign flip, not a qualified reverse gear and not a held heading.

The phase-aware stop (start after 0.5 s, stop at 6 s, one-cycle ramps) was 5/8. The three falls are 230401 at 2.31 s, 230402 at 2.28 s, and 230407 at 3.13 s, all during the start and before the stop. At 0.3 s before the fall, roll is already 13° to 16° and still growing, and the fall ends near the 45° roll limit. Pitch is not the −16° backward-pitch event. The abrupt cut uses the same start and falls once, 230412 at 2.74 s, the same roll. The trials that stay up do stop: speed before the cut is about 0.13 m/s, speed after the ramp is about 0.005 m/s, and travel after the stop is about 0.03 m. One abrupt survivor, 230410, finishes the stop at +38° of yaw. The stop rule did not require a heading, so that trial met the speed rule and missed a hold of the initial yaw. The held-out for the phase stop was not run.

Contacts in these trials are the MuJoCo sole boxes. Soft limits clip commands. Nothing here is a material, fatigue, or hardware test, and a finished trial is not evidence that a part will not break.

## Heading schedule on the early-rate gait

The early-rate file was not edited. Its sha256 is still `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`. The new behaviour is in the evaluator, sha256 `d78d48ac80c63525dc1959b099815d2fea83a42332697fb1a1ee8863554fc5bc`, and in `params/head843_manoeuvre_cfg.json`, sha256 `db8f607660376f2713e24d199347b48a559d77e92a2086cff9fe037a9abedca4`. With no heading schedule the hold still uses the yaw at reset. Two straight seeds, 214000 and 214001, kept the same final position and yaw as before this change, to 0.001 m and 0.1°. When a schedule is present, the slow-yaw integral and the stance hip-yaw trim track that schedule instead of the reset yaw. A feedforward of 0.20 rad of hip yaw per rad/s of commanded yaw rate, clipped at 0.08 rad and kept inside a 0.10 rad hip-yaw total, is applied only then. It is zero on a straight walk.

The phase-aware start that waited motionless and then rose in one cycle was the roll failure. Those falls were at 2.3–3.1 s, with roll already past 13°, and the stop at 6 s had not been reached. Starts in this candidate use the baseline 1 s ramp. The stop is still the next double-support edge. A restart is a second cycle of that same ramp. A route is a list of heading offsets from the reset yaw. In-place turns and sidesteps are still not commands.

`results/head843_manoeuvre_fix_prereg.json` was written at 2026-11-08T06:17:56Z. Task success requires staying upright and meeting the heading or stop rule. A perfect 40-seed block has a Wilson 95% lower bound of 91.2%, so none of these blocks is a 99.5% claim. Positive 180° was left out: at 15, 10 and 6°/s it missed the 15° band on fresh seeds, and feedforward 0.35 still left one of those misses 45° short.

| Command | Seeds | Task | Wilson 95% |
|---|---|---:|---|
| +20° arc, 4°/s, settle by 10 s | 233000–233039 | 38/40 | 83.5% to 98.6% |
| −20° arc, same rate | 233100–233139 | 40/40 | 91.2% to 100% |
| +45° at 15°/s, settle by 10 s | 233200–233239 | 39/40 | 87.1% to 99.6% |
| −45° at 15°/s | 233300–233339 | 39/40 | 87.1% to 99.6% |
| +90° at 15°/s, settle by 12 s | 233400–233439 | 35/40 | 73.9% to 94.5% |
| −90° at 15°/s | 233500–233539 | 37/40 | 80.1% to 97.4% |
| −180° at 10°/s, settle by 24 s | 233600–233639 | 21/40 | 37.5% to 67.1% |
| ±20° slalom at 4°/s | 234100–234139 | 39/40 | 87.1% to 99.6% |
| Stop at 6 s, baseline start | 233700–233739 | 40/40 | 91.2% to 100% |
| Restart, walks 0–4.5 s and 8–12 s | 233800–233839 | 40/40 | 91.2% to 100% |
| Stride ×0.7 | 233900–233939 | 40/40 | 91.2% to 100% |
| Stride ×1.3 | 234000–234039 | 40/40 | 91.2% to 100% |
| Straight 10 s, no schedule | 234200–234239 | 40/40 | 91.2% to 100% |
| Straight 20 s, no schedule | 234300–234319 | 20/20 | 83.9% to 100% |

The two missed +20° arcs turned 7.8° and 9.2° and finished 12° and 11° off the command. They failed the rule that at least half the command must be covered. The missed ±45° trials finished about 25° short. The missed ±90° trials finished 21° to 52° short. None of those walks fell, and pitch stayed near −3°. Post-slew cross-track on the misses was 0.10–0.18 m, inside the 0.40 m cap, so the miss is heading lag, not a path limit. Median final error on the −20° arc is 0.6°, and on the ±45° blocks it is 2.6° and 1.6°.

The −180° count is 21/40 under the written sign rule. Sixteen of the nineteen misses have a heading error of 0.6° to 5.1° and a wrapped yaw of about +176° to +180°, which is the same half-turn, with cross-track under 0.04 m. The sign clause rejects that wrap. Three are real shortfalls, with errors −18°, −30° and −40°. The written count is not replaced by a wrapped-angle recount.

The slalom miss, seed 234111, was at 15.3° when the command had returned to 0 at 12 s, 0.3° outside the band. The other three waypoints on that seed were inside it.

The stop block settled at about 0.005 m/s with about 0.03 m of travel after the stop, and yaw median +1.0°. The gap in the restart block is the stop between the two walks. Stride ×0.7 and ×1.3 were also 8/8 on both head masses. The ±45° blocks were not perfect, so they were not taken to the mass files. Straight 10 s and 20 s yaw medians are −1.9° and −2.3°. Ankle stall is about 2% on the stop and the slow stride, and about 6% on the fast stride. Contacts remain sole-box proxies. This is not a claim that a part will not break.

The walking qualifications of the early-rate file and of the frozen trim are unchanged. This manoeuvre sample does not meet a 99.5% task bar on any command. The measured blocker for a larger turn is heading lag: at 15°/s a 90° command misses the 15° band on 5 of 40 and 3 of 40, and a positive 180° was already outside that band on the probe.

## Stance settle on the same early-rate gait

Run 32’s −180° score stays 21/40 under the sign rule written before that run. It is not recounted. This section is a later controller and a later metric, on seeds that start at 236000.

The hip-yaw servo was not the stall. On the missed 90° and 45° trials the hip-yaw torque median was about 0.17 N·m, none of the slew samples reached 1.85 N·m, and the joint sat about 0.03 rad from the command. The body yaw rate on those misses averaged a few degrees per second while the command asked for 15°/s. The slow integrator, clipped at ±0.02 rad, was opposing the one-sided feedforward. The change freezes that integrator while a heading schedule is active and adds a stance-hip term, gain 0.45, clipped at 0.08 rad, on top of the 0.20 rad per rad/s feedforward. Straight walks do not set the schedule. Seeds 214000 and the stop seed 233700 kept their previous final position and yaw.

`results/head843_manoeuvre_b_prereg.json` was written at 2026-11-08T06:27:18Z. The pass rule uses continuous unwrapped yaw. The final angle must lie within 15° of the command and carry its sign. During the slew the heading may not go more than 15° the wrong way. The 15° band must be entered after the slew and no later than the declared end. Post-slew cross-track RMS must be at most 0.40 m. A block of 1000 is the 99.5% sample. A perfect 1000 has a Wilson 95% lower bound of 99.62%.

| Command | Task | Wilson 95% | 99.5% bar |
|---|---:|---|---|
| Slalom ±20° at 4°/s, seeds 244000–244999 | 1000/1000 | 99.62% to 100% | met |
| Stop at 6 s, seeds 245000–245999 | 1000/1000 | 99.62% to 100% | met |
| Stride ×0.7, seeds 247000–247999 | 1000/1000 | 99.62% to 100% | met |
| +20° arc at 4°/s | 997/1000 | 99.12% to 99.90% | not met |
| −20° arc at 4°/s | 997/1000 | 99.12% to 99.90% | not met |
| +45° at 15°/s | 999/1000 | 99.44% to 99.98% | not met |
| −45° at 15°/s | 991/1000 | 98.30% to 99.53% | not met |
| +90° at 15°/s | 991/1000 | 98.30% to 99.53% | not met |
| −90° at 15°/s | 994/1000 | 98.70% to 99.73% | not met |
| +180° at 10°/s | 993/1000 | 98.56% to 99.66% | not met |
| −180° at 10°/s | 991/1000 | 98.30% to 99.53% | not met |
| Restart | 998/1000 | 99.27% to 99.95% | not met |
| Stride ×1.3 | 998/1000 | 99.27% to 99.95% | not met |
| Straight 10 s, 200 seeds | 200/200 | 98.12% to 100% | regression only |
| Straight 20 s, 80 seeds | 80/80 | 95.42% to 100% | regression only |

The config is `params/head843_manoeuvre_cfg_b.json`, sha256 `2f8ba5c261624f6c7526a7f12f9231687924070cc64bc2f1b6edc55d7cd936ab`. The evaluator sha256 is `50db0a024acbd66fc1bc6faac621ba126a5ab22823be64aee810f71c8d5cb898`. The early-rate npy is unchanged.

Most heading misses finish near the command and fail because the unwrapped yaw went about 15–21° the wrong way before the turn. A smaller set finish genuinely short, for example +90° seeds at 69° and 74°, and +180° seeds at 150° and 164°. A few fall near −43° of pitch: one on the +20° arc, two on −45°, one on −90°, three on +180°, two on −180°. The restart misses, seeds 246040 and 246208, stopped and started again and finished at −17° and −29° of yaw. The fast-stride misses, seeds 248518 and 248767, walked at about 0.13 m/s and finished at 20.5° and 21.0° of yaw, just outside the 20° cap.

The stop and the ×0.7 stride were also 100/100 on each head mass. Those 100-seed bounds have a Wilson lower bound of 96.3% and are not a 99.5% mass claim. The ±45° blocks were not perfect, so they were not taken to the mass files.

Contacts remain sole-box proxies. This is not a claim that a part will not break. Positive and negative 180° are now both measured. Neither clears 99.5%. The run 32 −180° score of 21/40 is a different test and stays as it was.

## Artifact files

These three files were copied together after this run:

- `/opt/cursor/artifacts/REPORT.md`
- `/opt/cursor/artifacts/twiglet-ac-motion.patch`
- `/opt/cursor/artifacts/twiglet-motion-dev-full.zip`

Inside the zip, this iteration adds:

- `pkg/params/head843_earlyrate.npy` (sha256 `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`)
- `pkg/sim/run_head843_earlyrate.py`
- `pkg/sim/run_head843_earlyrate_qual.py`
- `pkg/sim/run_head843_pitch_auth.py`
- `pkg/results/head843_pitch_auth.json`
- `pkg/results/head843_earlyrate.json`
- `pkg/results/head843_earlyrate_screen.json`
- `pkg/results/head843_earlyrate_qual_prereg.json` (written 2026-11-08T03:17:15Z)
- `pkg/results/head843_earlyrate_qual.json`
- `pkg/results/head843_earlyrate_manifest.json`
- `pkg/sim/run_head843_earlyrate_manoeuvre.py`
- `pkg/results/head843_earlyrate_manoeuvre_protocol.json` (written 2026-11-08T06:08:31Z)
- `pkg/results/head843_earlyrate_manoeuvre.json`
- `pkg/params/head843_manoeuvre_cfg.json` (sha256 `db8f607660376f2713e24d199347b48a559d77e92a2086cff9fe037a9abedca4`)
- `pkg/results/head843_manoeuvre_fix_prereg.json` (written 2026-11-08T06:17:56Z)
- `pkg/results/head843_manoeuvre_fix_val.json`
- `pkg/sim/run_head843_manoeuvre_fix_val.py`
- `pkg/params/head843_manoeuvre_cfg_b.json` (sha256 `2f8ba5c261624f6c7526a7f12f9231687924070cc64bc2f1b6edc55d7cd936ab`)
- `pkg/results/head843_manoeuvre_b_prereg.json` (written 2026-11-08T06:27:18Z)
- `pkg/results/head843_manoeuvre_b_val.json`
- `pkg/sim/run_head843_manoeuvre_b_val.py`
- `pkg/sim/run_head843_shortbal_low4000.py`
- `pkg/results/head843_shortbal_low4000_prereg.json` (written 2026-11-08T02:57:55Z)
- `pkg/results/head843_shortbal_low4000.json`
- `pkg/results/head843_shortbal_manifest.json`
- `pkg/sim/run_head843_shortbal_val.py`
- `pkg/results/head843_shortbal_val_prereg.json` (written 2026-11-08T02:37:53Z)
- `pkg/results/head843_shortbal_val.json`
- `pkg/params/head843_shortbal.npy` (sha256 `52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5`, unchanged)
- `pkg/sim/manoeuvre.py` (sha256 `48ae37b20460568eff53ae8a625c3a848ca016f1e684f667d3ffc7e9d8e8d4cd`)
- `pkg/sim/run_head843_shortbal.py`
- `pkg/sim/run_head843_shortbal_qual.py`
- `pkg/sim/run_head843_shortbal_falls.py`
- `pkg/params/head843_shortbal.npy` (sha256 `52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5`)
- `pkg/params/head843_traj.npy` (sha256 `1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc`, unchanged)
- `pkg/results/head843_miss_timeline.json`
- `pkg/results/head843_shortbal_sign.json`
- `pkg/results/head843_shortbal_ckpt.json`
- `pkg/results/head843_shortbal.json`
- `pkg/results/head843_shortbal_screen.json`
- `pkg/results/head843_shortbal_qual_prereg.json`
- `pkg/results/head843_shortbal_qual.json`
- `pkg/results/head843_shortbal_falls.json`
- `pkg/results/REPORT.md`

Earlier files still in the archive:

- `pkg/sim/manoeuvre.py`
- `pkg/sim/run_head843_yawstate.py`
- `pkg/params/head843_yawstate.npy` (sha256 `6c75825abfe9ace5279ab8478cd1a6ac1e60be2d478257175c1f963ec1149e1f`)
- `pkg/params/head843_yawstate_b.npy` (sha256 `ac93bf67e9afb8bc2e2f54b9673df106061bda955116c84fa7ba7e27d845f71d`)
- `pkg/results/head843_yawstate_id.json`
- `pkg/results/head843_yawstate_probe.json`
- `pkg/results/head843_yawstate_ckpt.json`
- `pkg/results/head843_yawstate.json`
- `pkg/results/head843_yawstate_held.json`
- `pkg/results/head843_yawstate_b.json`
- `pkg/results/head843_yawstate_b_held.json`
- `pkg/results/head843_fail_traj.json`
- `pkg/results/head843_recover_ckpt.json`
- `pkg/results/head843_recover.json`
- `pkg/sim/run_head843_recover.py`
- `pkg/results/head843_early_gap.json`
- `pkg/results/head843_early_probe.json`
- `pkg/results/head843_early_ckpt.json`
- `pkg/results/head843_early.json`
- `pkg/sim/run_head843_early.py`
- `pkg/results/head843_coord_ckpt.json`
- `pkg/results/head843_coord.json`
- `pkg/sim/run_head843_coord.py`
- `pkg/results/head843_capture_authority.json`
- `pkg/results/head843_capture_ckpt.json`
- `pkg/results/head843_capture.json`
- `pkg/sim/run_head843_capture.py`
- `pkg/results/head843_ankle_map.json`
- `pkg/results/head843_track_diag.json`
- `pkg/results/head843_traj_ckpt.json`
- `pkg/results/head843_traj.json`
- `pkg/results/head843_traj_held.json`
- `pkg/params/head843_traj.npy`
- `pkg/sim/run_head843_traj.py`
- `pkg/results/head843_traj_qual_prereg.json`
- `pkg/results/head843_traj_qual.json`
- `pkg/results/REPORT.md`

Left untouched: `pkg/params/reliable.npy` (`d18f884ff5146eb0ed09cb8ab7562337482dd42c669649b4acd90c24ac083754`), `pkg/params/head843_search.npy` (`9e8b2caa13bd09a883515bdf7cfca6458480fc0eecdfed0a6977d381f7a5b40c`), `pkg/params/head843_support020.npy` (`d8bacd5b212ffccff1083cdc4e1c83ecd9bcfa212f0182b3c75a18565a3c988e`), `pkg/sim/models/twiglet_v3_v335ac.xml` (`5e62e84b4fbc20270d8331274b33190f4e83dfc6a422a95bad45c19afdf6503b`), `pkg/geometry/scene_v335ac.npz` (`e2d3009f6c35cfdfcefabf7ec9013ee9193547d5c4d16de37db78f0d07a60aba`). The remaining misses, including the two the trim adds, are still the −16° backward-pitch event with the catch already on its 0.06 rad clip.

## Timed heading handoff (cfg_c)

Preregistered 2026-11-08T07:07:35Z, after a development screen and before these seeds. Nominal head only. The scorer is the same whole-trace rule as cfg_b: upright, final unwrapped yaw within 15° of the command and of that sign, the opposite unwrapped peak over the whole trace at most 15°, the 15° band entered by the declared end, and post-slew cross-track at most 0.40 m. The 15° opposite cap was left as it was. cfg_b’s file hash `2f8ba5c261624f6c7526a7f12f9231687924070cc64bc2f1b6edc55d7cd936ab` and its counts stay. This law’s `sim/manoeuvre.py` is `cf5fe2037cbcc2a94c40f3203b6c131248ddad50c7bb68cfd7f92894e1b20202`. cfg_b’s scores were produced by `50db0a024acbd66fc1bc6faac621ba126a5ab22823be64aee810f71c8d5cb898`. The early-rate file is still `d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892`.

The change is when the reset integrator runs. On cfg_b it was frozen for the whole scheduled episode, and the body yaw swung about 16° before the command moved. Here the integrator runs until the command rate exceeds 2°/s, stays frozen while the command is moving or the error is still past 6°, and then returns. The stance gain stays 0.45 with a 0.08 rad clip, and the one-sided feedforward stays 0.20. A later restart waits for the next double-support edge. The first rise stays on the requested clock.

The 180° command in this preregistration is 6°/s from 2 s to 32 s, episode 36 s. On the cfg_b 10°/s misses the body rate through the middle of the slew averaged about 7.3°/s, so the lag grew for the whole 18 s. Six degrees per second was written down before this sample. The 4 s after the slew is the same budget cfg_b used. The cfg_b 10°/s half-turn was not rerun.

A development screen on seeds 251000–251351 was clean (32/32 on ±20°, ±45°, ±90°, restart, slalom, and straight; 24/24 on both 6°/s half-turns). That screen is not a qualification. The 1% tail showed up only in the preregistered thousands.

| Command | Seeds | Task | Wilson 95% lower | Clopper–Pearson 95% | Bar |
|---|---|---:|---:|---|---|
| +20° at 4°/s, 3–8 s | 252000–252999 | 1000/1000 | 99.62% | 99.63–100% | met |
| +45° at 15°/s, 3–6 s | 254000–254999 | 1000/1000 | 99.62% | 99.63–100% | met |
| −20° at 4°/s | 253000–253999 | 984/1000 | 97.42% | 97.42–99.08% | not met |
| −45° at 15°/s | 255000–255999 | 990/1000 | 98.17% | 98.17–99.52% | not met |
| +90° at 15°/s | 256000–256999 | 998/1000 | 99.27% | 99.28–99.98% | not met |
| −90° at 15°/s | 257000–257999 | 989/1000 | 98.04% | 98.04–99.45% | not met |
| +180° at 6°/s | 258000–258999 | 999/1000 | 99.44% | 99.44–100.00% | not met |
| −180° at 6°/s | 259000–259999 | 996/1000 | 98.98% | 98.98–99.89% | not met |
| Restart | 260000–260999 | 998/1000 | 99.27% | 99.28–99.98% | not met |
| Slalom under this law | 261000–261999 | 997/1000 | 99.12% | 99.13–99.94% | not met |
| Straight 10 s, no schedule | 262000–262199 | 200/200 | 98.12% | 98.17–100% | regression only |

Directions are separate. A slalom pass is not a turn pass. cfg_b’s slalom, stop, and stride ×0.7 remain 1000/1000 on their own seeds and their own hash. This sample does not replace them. Stop and stride ×0.7 do not set a heading schedule, so this edit does not retune them. Straight fingerprints still match: seed 214000 finishes at 1.1157 m and +1.498°, seed 214001 at 1.0931 m and −2.934°, and the stop seed 233700 at +0.33° with 0.0048 m/s after the settle. On the 200 straight seeds the shoulder mean was 20.9°, shoulder travel 17.8°, and head yaw travel 15.8°. Progress median was 0.109 m/s and yaw median −2.6°.

### What the misses are

Negative arcs and the negative 45° and 90° commands mostly finish within a few degrees and fail the 15° opposite peak. Of the −20° misses, 15 are that peak (15.03–16.93°) and one is a pitch fall. All 10 of the −45° misses are that peak (15.23–17.58°). Of the −90° misses, 9 are that peak and 2 finish short (errors +27° and +17°).

The peak is the first step of the slew, not the walk before it. On seeds 253015, 255046, and 257005 the straight walk of the same seed peaks at +11.7°, +11.0°, and +12.9°. With the command attached, the opposite peak is +15.4°, +15.4°, and +15.1°, at 0.26–0.34 s after the slew starts. On seed 239186, replayed on this law, the loaded left hip at 0.10 rad took the yaw the commanded way, and the next step’s right hip at the same sign and the same 0.10 rad clip produced a large yaw rate the other way.

Two probes of that right hip were measured and left out of this law. Reversing its sign sent the turns the wrong way (a +20° command finished near 0°). Scaling it to 0.25 brought one 15.5° kick under 15° and dropped a 90° finish from about 80° to about 38°. The kick and the sustained rate come from the same right-hip command. The qualified law keeps the cfg_b sign and the full right-hip scale.

The other misses are pitch falls near −42° to −45°, plus one short +90° (final +58.7°) and one restart that walked and finished at −20.2° of yaw. The pitch fall on seed 242399, at 6°/s, drifted from about −5° to −16° of pitch while the hip-yaw commands stayed inside about 0.1 rad and the hip-pitch commands were already large. This sample’s pitch falls are seeds 253059 (6.18 s), 256025 (6.25 s), 258189 (21.39 s), 259026 (12.37 s), 259341 (21.62 s), 259556 (9.25 s), 259792 (11.24 s), 260029 (10.79 s), 261613 (4.63 s), and 261642 (5.33 s).

### Envelope

On this law, at the nominal head, the commands that clear a per-command Wilson 95% lower bound of 99.5% are the +20° arc at 4°/s and the +45° turn at 15°/s. cfg_b still holds the slalom at ±20° and 4°/s, the stop after a 1 s start, and stride ×0.7. Negative turns at the same rates miss the 15° opposite cap on the first slew step. The 90° turns and both 6°/s half-turns miss because of the pitch falls, and the +90° block also has one short finish. Restart and this law’s slalom miss for the same pitch falls, plus one restart yaw of −20° and one slalom that was still +13° at the 12 s waypoint. Stride ×1.3 was left unchanged and still fails the two cfg_b seeds at +20.5° and +21.0° of yaw. No mass block was preregistered here. Sole contacts are proxy boxes. These counts are not a hardware or strength result.

Files: `params/head843_manoeuvre_cfg_c.json` (`3ffcf307a64e1da47c61400d1faf5e96d3e7322c5408f6790389301c563d8fbe`), `results/head843_manoeuvre_c_prereg.json`, `results/head843_manoeuvre_c_val.json`, `results/head843_manoeuvre_c_screen.json`, `results/head843_manoeuvre_c_manifest.json`, `sim/run_head843_manoeuvre_c_val.py`, `sim/run_head843_manoeuvre_c_screen.py`.

## Onset right-stance flip (cfg_d)

Preregistered 2026-11-08T07:47:28Z, after the screens and before these seeds. Nominal head. The scorer is unchanged: whole-trace opposite peak at most 15°, final unwrapped yaw within 15° and of the commanded sign, band entered by the declared end, cross-track at most 0.40 m. cfg_b hash `2f8ba5c2…` and cfg_c hash `3ffcf307…` and their counts stay. This law’s `sim/manoeuvre.py` is `98facc7220b9fb69d51599943f2a818f65ace2ce5fa669366e98f468690e8bd5`. Config `params/head843_manoeuvre_cfg_d.json` is `4ce06836e4d0a68d39154f4e7370ab23b22c5286be90f6f0af16a09695e554a7`. The early-rate file is still `d308c5f0…`.

The phase-selected hip still receives the full 0.45 proportional term and the 0.20 feedforward. For the first 0.40 s after the command rate rises through 2°/s, if that hip is the right hip and the right sole has more than 55% of the sole load, the sign is flipped. After 0.40 s the sign matches cfg_c. The 0.40 s window is the measured time of the opposite peak (0.26–0.36 s into the slew). The swing right hip is not flipped. Gains were not reduced.

An always-on version of the same flip was measured on seeds 263000–263263 and dropped before this preregistration. It cleared the recorded kick seeds and then left fresh 90° finishes 20–30° short, because the loaded right hip was also carrying the sustained rate. Putting the whole command on the stance foot, with either sign, reversed the turn or cut a 90° finish from about 95° to about 54°.

On the recorded cfg_c misses, replayed only as a check of the changed law, the onset flip took 15 of 16 −20° misses and 9 of 10 −45° misses inside the rule. The remaining −45° seed, 255061, peaks at +15.62° at 2.88 s with or without a heading schedule: that peak is the straight walk, before the command. A fresh 200 straight walks (263400–263599, first 3 s) had a maximum positive peak of +12.4°.

Straight replays of the cfg_c pitch-fall seeds, same horizons, did not fall. That includes 36 s walks of 258189, 259026, and 259556. The −43° pitch falls are an interaction with the heading command. Under the onset law, 253059 and 256025 survive, and 258189, 259341, and 259556 still fall. Half-turns were therefore left out of this preregistration.

| Command | Seeds | Task | Wilson 95% lower | Clopper–Pearson 95% | Bar |
|---|---|---:|---:|---|---|
| +20° at 4°/s, 3–8 s | 265000–265999 | 1000/1000 | 99.62% | 99.63–100% | met |
| −20° at 4°/s, 3–8 s | 266000–266999 | 1000/1000 | 99.62% | 99.63–100% | met |
| +45° at 15°/s, 3–6 s | 267000–267999 | 1000/1000 | 99.62% | 99.63–100% | met |
| −45° at 15°/s, 3–6 s | 268000–268999 | 999/1000 | 99.44% | 99.44–100.00% | not met |
| +90° at 15°/s, 2.5–8.5 s | 269000–269999 | 998/1000 | 99.27% | 99.28–99.98% | not met |
| −90° at 15°/s, 2.5–8.5 s | 270000–270999 | 995/1000 | 98.84% | 98.84–99.84% | not met |
| Slalom on this law | 271000–271999 | 997/1000 | 99.12% | 99.13–99.94% | not met |
| Straight 10 s, no schedule | 272000–272199 | 200/200 | 98.12% | 98.17–100% | regression only |

These counts are not pooled with cfg_b or cfg_c. cfg_c’s +20° and +45° remain qualified on hash `cf5fe203…`. cfg_d re-earned those two on its own seeds and adds the −20° arc. cfg_b’s slalom, stop, and stride ×0.7 remain 1000/1000 on hash `50db0a02…`.

The −45° miss is a pitch fall, seed 268632 at 9.54 s, minimum pitch −44.4°. The +90° misses finish at +63° and +72° with opposite peaks of 0.6°. The −90° misses are three shorts (finals −74°, −72°, and −44°), one pitch fall at 3.81 s (minimum pitch −43.2°), and one opposite peak of 16.0° on a finish of −88°. The three slalom misses are pitch falls at 11.82 s, 4.14 s, and 5.41 s. None of those is a 15.1° yaw-threshold miss.

Straight fingerprints still match: seed 214000 at 1.1157 m and +1.498°, seed 214001 at 1.0931 m and −2.934°, stop seed 233700 at +0.33° and 0.0048 m/s after the settle. On the 200 straight seeds the shoulder mean was 20.9°, shoulder travel 17.7°, head yaw travel 15.8°, progress median 0.109 m/s, yaw median −2.1°.

Restart and stride ×1.3 do not set a heading schedule, so this alloc does not run. cfg_c restart stays 998/1000. Stride ×1.3 still fails seeds 248518 and 248767 at +20.5° and +21.0° of yaw. No mass block was preregistered. Sole contacts are proxy boxes. These counts are not a hardware or strength result.

Files: `results/head843_manoeuvre_d_prereg.json`, `results/head843_manoeuvre_d_val.json`, `results/head843_manoeuvre_d_manifest.json`, `results/head843_manoeuvre_d_screen.json`, `results/head843_manoeuvre_d_onset_screen.json`, `sim/run_head843_manoeuvre_d_val.py`, `sim/run_head843_manoeuvre_d_screen.py`.

## Pitch and yaw on the same law

No new qualification. The controller file is still `98facc72…`. The cfg_d counts above stay.

On the recorded falls the hip-pitch torque is already at the ±1.91 N·m rail while pitch is about −8° to −14°, and the hip-yaw command is either at its ±0.10 rad clip or, after the slew, back near ±0.03 rad. Straight walks of those seeds, including 36 s, do not fall. Dropping the yaw command on the same step the pitch catch is already on did not stop the falls. Seed 268632 fell earlier, at 7.89 s instead of 9.54 s, and the 90° shorts finished further behind (+55° and −35°). That change was reverted.

The onset flip and the plain handoff were compared on the same seeds. Without the flip, 268632 completes the −45° (final −40.6°, opposite peak 13.6°). With the flip it falls. Without the flip, 270581 finishes the −90° and fails the opposite-peak rule at 16.4°. With the flip the opposite peak is 12.0° and the finish is only −44°. Seed 253015, the −20° kick, fails at 15.4° without the flip and passes with it. The sign change that qualified the −20° arc is the same change that induces a pitch fall on a −45° the handoff otherwise completes.

The 15°/s shorts are a rate limit on seeds whose pitch stays near ±2°. The hip-yaw command sits at ±0.10 rad and the body yaw advances at about 8–10°/s. A 90° command at 8°/s was declared from that measurement before the trials: t0 2.5 s, t1 13.75 s, episode 17.25 s, the same 3.5 s after the slew. On the onset law the five recorded shorts then finish within 2° of ±90°. Seed 270260 still falls at 3.7 s, and seed 270924 still peaks 16.1° the wrong way. Fresh seeds 275000–275095 were 48/48 in each direction. That screen is not a qualification. The known fall and the known 16° peak are still in the mechanism, so no 1000-seed block was opened. The same 8°/s command without the onset flip brings the 16° opposite peaks back.

Restart seed 260842, which has no heading schedule, reaches −27° of yaw at 10.8 s during the second walk. The hip-yaw commands at that time are about ±0.03 rad, so the hold is applying and the second-start transient exceeds it. Fast-stride seed 248518 still ends at +20.3°. Its hip yaw is past 0.019 rad on 55% of samples, which is the ±0.02 rad straight-walk trim at its clip. Widening that trim would change the straight walk. Stop seed 233700 and straight seeds 214000 and 214001 still match the recorded fingerprints.

On hash `98facc72…`, nominal head, the qualified commands are the +20° arc, the −20° arc, and the +45° turn, each 1000/1000. The −45°, both 90° commands at 15°/s, and this law’s slalom are not. Half-turns were not given a new thousand. cfg_b still holds the slalom, the stop, and stride ×0.7 on its own hash. No mass block was added. Sole contacts are proxy boxes.

The 8°/s screen is `results/head843_manoeuvre_d_rate8_screen.json`.

## Earlier step guard and restart trim (cfg_e)

Preregistered 2026-11-09T00:21:51Z. Law `e13cd9c1ef2f529f3d4401626ef819b7e44df8c9358788879bacb48cf4228887`. Config `1bfda629203e31f8e82224fd4d6baa92df308949a872f205bd163f5d5985a93f`. The early-rate file is still `d308c5f0…`. cfg_d’s hash and its ±20° and +45° counts stay.

On the command-induced falls the touchdown step grows from about 0.040 m to 0.050 m while the same seed walked straight stays near 0.038–0.042 m, and pitch ratchets backward a degree or so per step. Seed 270260 is not in that class: it also falls when walked straight, at 4.33 s. The other recorded falls do not.

After a heading move, a touchdown longer than 0.045 m shortens the next swing, capped at 0.03 rad. Straight walks never set that flag. With it, seed 268632 completes the −45° (final −47.5°, opposite peak 11.4°) and slalom seeds 271339 and 271596 stay upright. Seed 271181 still falls at 13.9 s, after the return toward zero, with pitch already −4.5° at the 12 s waypoint. The 15°/s 90° shorts are unchanged, because their steps are not what limits them. A fresh screen, not a qualification: −45° 47/48 (one finish 17.5° short), slalom 48/48, ±20° and +45° 32/32, ±90° 32/32, straight 32/32. The known 90° shorts and the one slalom fall are still in the mechanism, so those commands were not given a new thousand.

The restart’s second walk was missing the ±0.02 rad trim. Seed 260842 reached −27° at 10.8 s with hip yaw near ±0.03 rad, after the 1 s rise. The later cycle, and only that cycle, now uses a 0.04 rad cap. The first walk and a straight walk stay at 0.02 rad. The four recorded restart misses then finish between −14° and +7°. Seeds 276256–276303 were 48/48. The preregistered block, seeds 277000–277999, is **999/1000**. Wilson 95% lower bound **99.44%**. It does not clear 99.5%. The miss is seed 277378, upright, stopped and restarted, final yaw **−15.27°**. No falls. Yaw on the thousand runs from −15.27° to +11.36°, median +0.4°. Straight regression seeds 278000–278199 are 200/200, Wilson lower 98.12%. Shoulder mean 20.9°, shoulder travel 17.9°, head yaw travel 15.8°. Straight fingerprints 214000 and 214001 and stop seed 233700 still match. No mass block was run, because the nominal restart block was not perfect.

Stride ×1.3 with the same 0.04 rad cap passes seeds 248518 and 248767 at +17.8° and +17.4°. Fresh seeds 276304–276351 are 47/48. Seed 276309 finishes at +26.1°. That command was not preregistered.

On this hash the restart is 999/1000 and is not a 99.5% claim. Nothing else was qualified here. cfg_d still holds ±20° and +45°. cfg_b still holds the slalom, the stop, and stride ×0.7.

Files: `results/head843_manoeuvre_e_prereg.json`, `results/head843_manoeuvre_e_val.json`, `results/head843_manoeuvre_e_screen.json`, `params/head843_manoeuvre_cfg_e.json`, `sim/run_head843_manoeuvre_e_val.py`.
