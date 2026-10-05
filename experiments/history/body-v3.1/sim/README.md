# body v3.1 sims (what changed vs v3)
- Model: `gen_mjcf_v3.py` builds `twiglet_v3.xml` from the v3.1 design (same file names as v3; this folder is v3.1). It weighs 2.213 kg, 40 g more than v3 (shin covers, longer forearm, bigger gripper housing).
- Arm joints: axes are tilted 18° (splayed arms). The right-side axes are the reflected pseudo-vectors, so a positive angle means the same motion on both sides.
- Soft limits (`episode.py`, v3.1):
  - hip roll 15° outward (conservative margin; the final collision check is clear to 20°);
  - shoulder −5..84°, elbow ≤ min(110, 105 − shoulder). The sims ran with the earlier rule, elbow ≤ max(70, 125 − shoulder), and only the wave test comes near the new cap (by 3°).
- Re-run: `run_tests.py v3 --video` (stand, push, weight shift, head+arm) and `arm_heat.py v3`.
- Walking: `walk_eval.py v3 [--eff]` re-evaluates the v3 gait parameters on the v3.1 model (nominal + 20 randomized 10 s trials, same seeds). There was no new gait search.
- `compare_v31.py` writes `compare_v3_v31.md/.json`. The v3 reference results are copied in `v3_ref/`.
- Videos: `v31_push_recovery_v3`, `v31_walk_v3`, `v31_walk_v3_eff`, `v31_head_arms_v3` (.mp4/.gif). The head+arm frames were flipped vertically to undo the offscreen renderer's upside-down readback.

| Metric | v3 | v3.1 |
|---|---|---|
| Total mass (kg) | 2.173 | 2.213 |
| Stands with no pre-lean | yes | yes |
| COM height (mm) | 233.0 | 231.1 |
| Support margin front / back / side (mm) | 51 / 51 / 70 | 53 / 49 / 70 |
| Tipping angle side / front (deg) | 16.7 / 12.3 | 16.9 / 13.0 |
| Static hip / knee / ankle N·m (x 0.49 rated) | 0.26 (0.53x) / 0.39 (0.80x) / 0.14 | 0.24 (0.49x) / 0.37 (0.76x) / 0.11 |
| Standing bus current (A) | 5.08 | 4.81 |
| Push survived, no controller F/B/L/R (N·s) | 0.94 / 0.94 / 1.29 / 1.31 | 1.01 / 0.91 / 1.31 / 1.34 |
| Push survived, IMU balance F/B/L/R (N·s) | 0.94 / 0.96 / 1.31 / 1.34 | 1.12 / 0.80 / 1.36 / 1.38 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad | 0.11 / 0.00 | 0.07 / 0.00 |
| Walk max-speed: success (20 rand.) / speed / current | 100% / 0.168 m/s / 12.34 A | 100% / 0.172 m/s / 12.37 A |
| Walk energy-aware: success / speed / current | 100% / 0.133 m/s / 11.04 A | 100% / 0.137 m/s / 10.87 A |
| Head+arm test: fell / min margin / neck peak | no / 33.7 mm / 0.84 N·m | no / 29.3 mm / 0.814 N·m |
| Arm wave worst RMS x rated 0.5 / 0.8 / 1.5 Hz | 0.74 / 0.99 / 1.63 | 0.76 / 1.01 / 1.66 |
| Arm wave max copper loss per servo W 0.5 / 0.8 / 1.5 Hz | 0.28 / 0.51 / 1.36 | 0.29 / 0.52 / 1.41 |
| Static shoulder gravity torque, straight arm, worst angle (N·m, x 0.147) | 0.046 (0.31x) | 0.063 (0.43x) |
| Fingertip payload continuous / brief (g), arm horizontal | 83 / 322 | 51 / 229 |
| Arm mass per side (g) | 86 | 97 |

v3.1 walks re-use the v3 gait parameters (walk_eval.py: nominal + 20 randomized 10 s trials); no new gait search.


---
(v3 notes below)

# Twiglet body v3: MuJoCo sims

This uses the same harness, tests and metrics as `body-v2/sim`, so the numbers compare directly. The stock and v2 columns are reused from `body-v2/sim/results_*.json` and `walk_*.json`; only v3 was re-simulated. The one exception is arm heat: v2 was re-run with `arm_heat.py` on the same motion as v3.

## Files
| File | What it does |
|---|---|
| `gen_mjcf_v3.py` | Builds `twiglet_v3.xml` and `mass_report_v3.json` from the v3 design cache (`../design_v3.py`). Meshes go in `meshes/`. |
| `simlib.py` | Servo model (DC motor behind a gearbox, per-actuator stall torque and speed). Covers STS3215 at 7.4 V (legs and neck) and STS3032 at 6 V (arms), plus current estimates, stance, balance feedback, metrics and video. |
| `episode.py` | Episode runner. It applies the v3 soft joint limits and the coupled arm rule from the collision check. |
| `run_tests.py v3` | (a) standing lean, margins, static torque and current; (b) push recovery with and without the IMU balance loop; (c) weight shift; (e) head and arm motion. Writes `results_v3.json`, `push_recovery_v3.gif/.mp4` and `head_arms_v3.gif/.mp4`. |
| `walk_search.py` / `walk_video.py` | Open-loop gait search (max-speed objective and energy-aware objective), each checked over 20 randomized episodes. Writes `walk_v3*.json/.npy/.npz/.gif/.mp4`. |
| `arm_heat.py` | Runs the same arm-wave motion on v2 (STS3215) and v3 (STS3032) at 0.5, 0.8 and 1.5 Hz. Output: RMS torque against rated torque, and copper loss. |
| `make_table.py` | Writes `compare_stock_v2_v3.md/.json` and `plot_compare.png`. |

## Model rules
- **Printed parts:** mass rules are the same as `body-v2/sim/gen_mjcf.py`: mesh volume, PLA at 1.24 g/cm³, and a shell-plus-infill fill factor.
- **Head (light print):** 0.8 mm skin (2 walls) with 8% infill. The printed head parts come to about 290 g. With the displays and driver they are 380 g, and the whole head link, including the head servos, is 493 g.
- **Servos:** STS3215 55 g. STS3032 20 g, plus 1 g for the horn.
- **Electronics:** two round displays at 40 g each, a 10 g display driver. The battery, IMU and controller are as in v2.
- **Total:** 2.173 kg (v2 2.42 kg, stock 2.10 kg).

### STS3032 servo model
From the Feetech datasheet:
- stall torque 0.441 N·m and no-load speed 111 rpm (11.6 rad/s) at 6 V;
- rated torque 0.147 N·m;
- stall current 1.2 A, idle current 0.15 A;
- Kt 0.343 N·m/A, winding resistance 2.8 Ω.

The arm ctrlrange is clipped to ±0.441 N·m. The arm armature (0.004) is an estimate.

### Soft limits (from `../collide_report.json`)
- **Hip yaw ±7°.** At 8° combined with roll, the hip bracket touches the torso frame and neck cradle.
- **Hip roll:** +20° outward, −13° inward.
- **Neck pitch:** −1..4°.
- **Head:** pitch −34..5°, roll ±5°.
- **Arms:**
  - shoulder −5..84°, elbow −2..124°;
  - coupled rule: elbow ≤ max(30, 98 − shoulder), and elbow ≥ 14 when shoulder < 8.
  - Because of the coupled rule, there is no overhead wave.

## Pre-lean
`BASE_LEAN` is a thigh offset that puts the COM over the centres of the soles in the crouched stance. It is 0.08 rad for v3 and 0.17 rad for v2. v3 also stands with no pre-lean at all: the standing test gives 51/51 mm front/back margin. The small offset only re-centres the COM for the 0.30 rad crouch used by the gait. It is half of v2's, because the hips moved 20 mm forward and the battery moved back.

## Results
See `compare_stock_v2_v3.md`, which is copied below, and `plot_compare.png`.
| Metric | stock ODM | v2 | v3 |
|---|---|---|---|
| Total mass (kg) | 2.1 | 2.42 | 2.17 |
| Height without hat (mm) | 518 straight legs (stock head + antennas) | 519 stance (528 straight) | 448 stance (454 straight) |
| Stance crouch / software pre-lean (rad) | 0.63 / 0.00 | 0.30 / 0.17 | 0.30 / 0.08 |
| Stands with NO pre-lean? | yes | no (falls at 0.74 s) | yes |
| COM height (mm) | 204.6 | 262.3 | 233.0 |
| Support margin front / back / side (mm) | 48 / 52 / 114 | 21 / 81 / 65 | 51 / 51 / 70 |
| Static forward sag from servo compliance (deg) | 4.52 | 10.42 | 4.36 |
| Tipping angle side / front (deg) | 29.1 / 13.3 | 13.9 / 4.6 | 16.7 / 12.3 |
| Open-loop COM window (mm) | -44.4 .. 19.2 | -35.4 .. 1.3 | -47.2 .. 19.1 |
| Static hip pitch torque N·m (x rated 0.49) / est. current A | 0.13 (0.26x) / 0.28 | 0.67 (1.37x) / 0.96 | 0.26 (0.53x) / 0.44 |
| Static knee torque N·m (x rated 0.49) / est. current A | 0.55 (1.13x) / 0.81 | 0.86 (1.76x) / 1.19 | 0.39 (0.80x) / 0.61 |
| Static ankle torque N·m (x rated 0.49) / est. current A | 0.14 (0.29x) / 0.29 | 0.52 (1.07x) / 0.77 | 0.14 (0.28x) / 0.29 |
| Static neck pitch torque (N·m) | 0.103 | 0.361 | 0.267 |
| Standing bus current, all servos (A, estimate) | 4.07 | 8.12 | 5.08 |
| Push survived, no controller F/B/L/R (N·s) | 1.08 / 1.15 / 2.56 / 2.56 | 0.26 / 1.52 / 0.84 / 0.87 | 0.94 / 0.94 / 1.29 / 1.31 |
| Push survived, IMU balance F/B/L/R (N·s) | 1.20 / 0.98 / 2.79 / 2.79 | 0.96 / 0.98 / 1.22 / 1.24 | 0.94 / 0.96 / 1.31 / 1.34 |
| Weight shift 0.4 Hz: min foot load at 0.15 / 0.20 rad; falls from | 0.34 / 0.17; never (<=0.30) | 0.00 / 0.00; 0.25 | 0.11 / 0.00; never (<=0.30) |
| Walk max-speed: success (20 randomized) / speed (m/s) / current (A) | 95% / 0.205 / 10.8 | 100% / 0.079 / 10.2 | 100% / 0.168 / 12.3 |
| Walk max-speed: peak/RMS torque hip pitch, knee, ankle (N·m) | 1.91/1.02, 1.91/1.00, 1.91/1.00 | 1.91/1.03, 1.91/0.82, 1.91/0.71 | 1.91/1.17, 1.91/0.96, 1.91/1.06 |
| Walk energy-aware: success (20 randomized) / speed (m/s) / current (A) | 95% / 0.194 / 10.5 | 95% / 0.050 / 7.7 | 100% / 0.133 / 11.0 |
| Walk energy-aware: peak/RMS torque hip pitch, knee, ankle (N·m) | 1.91/1.03, 1.91/0.95, 1.91/1.01 | 1.49/0.67, 1.26/0.56, 1.47/0.56 | 1.91/1.01, 1.91/0.79, 1.91/0.94 |
| Head+arm motion test: fell / min margin (mm) / neck peak (N·m) | no / 15.9 / 0.644 | no / 30.1 / 0.788 | no / 33.7 / 0.84 |
| Arm-wave heat 0.5 Hz (same motion v2/v3) | no arms | STS3215: worst RMS 0.172 N·m = 0.35x rated; 0.16 W max/servo | STS3032: worst RMS 0.108 N·m = 0.74x rated; 0.28 W max/servo |
| Arm-wave heat 0.8 Hz (same motion v2/v3) | no arms | STS3215: worst RMS 0.283 N·m = 0.58x rated; 0.44 W max/servo | STS3032: worst RMS 0.146 N·m = 0.99x rated; 0.51 W max/servo |
| Arm-wave heat 1.5 Hz (same motion v2/v3) | no arms | STS3215: worst RMS 0.682 N·m = 1.39x rated; 2.54 W max/servo | STS3032: worst RMS 0.239 N·m = 1.63x rated; 1.36 W max/servo |

## Videos
- `push_recovery_v3.gif/.mp4`: four pushes (forward, left, back, right), each at 85% of the tested maximum impulse. The last push may tip it over at the end: pushes are applied back to back, without full settling in between.
- `walk_v3.gif/.mp4` (max-speed gait) and `walk_v3_eff.gif/.mp4` (energy-aware gait).
- `head_arms_v3.gif/.mp4`: head motion and arm waving with the balance loop on. The frames were stored upside down by the offscreen renderer and were flipped vertically afterwards. The physics is unaffected.

## Caveats
- The gaits are open-loop, found by search. They are not an RL policy, and the real Open Duck policy must be retrained for v3.
- Current estimates come from the torque/current model, not from measurements.
- The walk peak torque of 1.91 N·m is the STS3215 stall clamp, and it is reached briefly in all three robots.
