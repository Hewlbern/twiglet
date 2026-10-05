# Twiglet body v2: MuJoCo simulation

This folder simulates three robots side by side:
- **v2**: the new photo-accurate body (option 2) with head A.
- **stock**: the unmodified ODM humanoid.
- **opt1**: option 1, which is the stock ODM plus the old Twiglet arms, bib and boots, plus head A.

Everything here is **open-loop gaits plus simple PD and IMU feedback, not an RL policy**. Treat the numbers as a relative comparison between designs, not as absolute predictions.

## Reproduce
Python: `$PYTHON` (mujoco 3.14, trimesh, imageio-ffmpeg, matplotlib). Videos need `MUJOCO_GL=glfw xvfb-run -a -s "-screen 0 1600x1600x24"`.
```
python gen_mjcf.py all              # twiglet_{v2,stock,opt1}.xml, mass_report_*.json, meshes/
python run_tests.py v2              # tests a,b,c,e -> results_v2.json (+ gifs); same for stock / opt1
python walk_search.py v2 800        # max-speed gait search -> walk_v2.json, walk_v2_best.npy
python walk_search.py v2 800 --eff  # energy-aware gait search -> walk_v2_eff.json
python walk_video.py v2 [--eff]     # walk_v2[_eff].gif/.mp4 + trace npz
python sensitivity.py               # sensitivity_v2.json (design what-ifs)
python make_plots.py                # plot_*.png
```
Heads-up: `twiglet_v2.xml` was generated before the last small trims to the shell and shoulder mounts, which differ by less than 10 g. Regenerating it will slightly change the results.

## Model
**Masses**
- Masses come from the meshes. Inertia comes from each mesh, scaled to the part's mass.
- STS3215 servo: 55 g. PLA printed parts: 1.24 g/cm³, modelled as a 0.9 mm solid skin plus 15% infill. TPU: 1.21 g/cm³. Steel parts: 7.85 × 0.8.
- Fixed electronics masses (g):

| Cell ×2 | Holder | BMS | Charger | Switch | Bus board | IMU | Misc wiring/screws |
|---|---|---|---|---|---|---|---|
| 47 each | 12 | 8 | 5 | 3 | 12 | 3 | 60 |

- Validation: the stock model comes out at 2.10 kg; the ODM's own MJCF says 2.06 kg.

**Totals**

| | Total mass | Notes |
|---|---|---|
| v2 | 2.42 kg | head assembly 481 g, trunk 746 g, arm ~140 g each, foot 76 g |
| opt1 | 2.73 kg | |
| stock | 2.10 kg | |

**Head A with digital eyes**
- The printed eye cups, rings and LEDs are removed.
- Added in their place: 2 × 30 g for two 2.1" round 480×480 displays with their PCBs, plus 10 g for an ESP32-S3/RP2040 driver.
- Head A's printed parts come to 308 g under the skin rule. If the head is printed with 3 walls and a denser infill it could weigh about 380–400 g. Print it light (2 walls, 5–10% infill); the sensitivity table below shows what each 100 g costs.
- The Pi Zero mesh is counted as PLA (4 g instead of about 11 g), which is a small error.

**Servo model** (`simlib.py`)
- A PWM DC motor: duty u = clip((Kp·e − Kd·ω)/1.91, ±1), torque = 1.91·u − 0.35·ω, clipped to ±1.91 N·m (stall at 7.4 V).
- Kp 12, Kd 0.25, 0.4° backlash deadband. Joints: armature 0.02, damping 0.05, frictionloss 0.05.
- Current estimate: 0.12 A idle + 2.5 A × |τ|/1.91 per servo.
- Rated continuous torque is taken as about 0.49 N·m. This current model is only an estimate.

**Soft limits** (`episode.py`) come from the collision study in `../collide_report.json`.

## Tests
| Test | What it does |
|---|---|
| a | Stand: support margins, tipping angles, static torques, compliance sag, the open-loop COM window |
| b | Push recovery: 0.1 s pulses in 4 directions, with no controller and with IMU balance |
| c | Weight shift: 0.4 Hz sine on hip roll, checking foot unloading and falls |
| d | Walking: random search + CEM gait optimisation, then 20 randomized trials (mass ±10%, friction, servo gain, latency, terrain) |
| e | Head and arm motion while standing |
| f | Bottleneck analysis: torque peak/RMS vs rating (`plot_walk_torque.png`) and a sensitivity study |

## Results
**Standing and push recovery**

| Metric | v2 (crouch 0.30, lean 0.17) | stock (crouch 0.63) | opt1 |
|---|---|---|---|
| Support margin front / back / side (mm) | 21 / 81 / 65 | 48 / 52 / 114 | 26 / – / 112 |
| COM height (mm) | 262 | 205 | 204 |
| Tipping angle side / front | 13.9° / 4.6° | 29.1° / 13.3° | 28.8° / 7.1° |
| Static forward sag from servo compliance | 10.4° | 4.5° | 11.4° |
| Static torque hip pitch / knee / ankle / neck (N·m) | 0.67 / 0.86 / 0.52 / 0.36 | 0.13 / 0.55 / 0.14 / 0.10 | 0.60 / 1.14 / 0.52 / 0.37 |
| Push survived, no controller, F/B/L/R (N·s) | 0.26 / 1.52 / 0.84 / 0.87 | 1.08 / 1.15 / 2.56 / 2.56 | 0.68 / 2.53 / 2.02 / 2.02 |
| Push survived, IMU balance, F/B/L/R (N·s) | 0.96 / 0.98 / 1.22 / 1.24 | 1.20 / 0.98 / 2.79 / 2.79 | 1.66 / 1.78 / 3.26 / 3.28 |
| Standing bus current (estimate) | 8.1 A | 4.1 A | – |

**Weight shift and walking**

| Metric | v2 | stock |
|---|---|---|
| Weight shift | Fully unloads a foot at 0.15–0.20 rad; falls at 0.25 rad and above | Never unloads below 10–17% |
| Walk, max-speed gait | 100% success, 0.079 m/s, ~10 A | 95% success, 0.205 m/s, ~11 A |
| Walk, energy-aware gait | 95% success, 0.050 m/s, 7.7 A | 95% success, 0.194 m/s, 10.5 A |
| Energy-aware peak/RMS torque, hip pitch / knee / ankle (N·m) | 1.43/0.72, 1.27/0.57, 1.45/0.62 | 1.91/1.10, 1.91/0.99, 1.91/1.10 |

- Head and arm test (e): v2 did not fall and kept at least 30 mm of margin.
  - Neck torque: 0.79 N·m peak, 0.27 N·m RMS.
  - The elbow and gripper hit stall during 1.5 Hz ±40° waving. Keep arm waving at or below 0.8 Hz.
- Stability of v2 without the forward lean:
  - The neutral stance falls forward at 0.74 s.
  - The cause is servo compliance plus a nose-heavy COM: the upper body's COM sits about 40 mm ahead of the hip-pitch axis.

**Sensitivity (v2)**

| Change | Static hip / knee torque (N·m) | Forward sag |
|---|---|---|
| Baseline | 0.64 / 0.72 | 9.2° |
| Head −100 g | 0.54 / 0.62 | 7.9° |
| Hips moved 25 mm forward | 0.37 / 0.53 | 6.6° |
| Both of the above | 0.29 / 0.46 | 5.5° |
| Servo Kp 20 | 0.52 / 0.56 | 4.4° |

Moving the arms back has negligible effect.

## Files
| Type | Files |
|---|---|
| Media | `walk_*.gif/.mp4`, `push_recovery_*.gif/.mp4`, `head_arms_*.gif` |
| Plots | `plot_*.png` |
| Raw results | `results_*.json`, `walk_*.json`, `sensitivity_v2.json`, `mass_report_*.json` |
