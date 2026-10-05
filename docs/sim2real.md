# Sim2real

> Upstream's training workflow is in [upstream/sim2real.md](upstream/sim2real.md) and the [Open_Duck_Playground](https://github.com/apirrone/Open_Duck_Playground) repo.

## Status

- There are no RL/ONNX policies yet. Upstream ships `BEST_WALK_ONNX*.onnx`. Ours are parametric gait vectors found by search in MuJoCo:
  - `BEST_WALK_PARAMS_v334r1.npy`: max-speed gait. 20/20 randomized trials at 0.208 m/s; held-out seeds 6000–6019: 19/20 at 0.207 m/s.
  - `BEST_WALK_EFF_PARAMS_v333r1.npy`: energy-aware gait. 20/20 at 0.156 m/s.
- Each file is 12 floats: `f, stride, lift, sway, sway_ph, crouch, lean, kp_pitch, kd_pitch, kp_roll, kd_roll, ank_off` (see `experiments/twiglet_sim/walk_search.py`).
- Nothing has run on hardware yet (TODO).

## Re-running the sims

```bash
pip install mujoco numpy
cd experiments/twiglet_sim
python run_tests.py v3            # static/push/head+arm tests -> out/results_v3.json
python walk_eval.py v3            # max-speed gait (walk_v3_best.npy = BEST_WALK_PARAMS_v334r1.npy)
python walk_eval.py v3 --eff      # energy-aware gait (walk_v3_eff_best.npy = BEST_WALK_EFF_PARAMS_v333r1.npy)
./run_all.sh twiglet_v3_v334.xml v334   # any model in models/, outputs in out/v334/
```

- The default model is `experiments/twiglet_sim/models/twiglet_v3_v334_wig344.xml` (body v3.34 + wig v3.44). Pick another with `TWIGLET_XML=<name in models/>`, or pass it to `run_all.sh`.
- Outputs go to `out/` (gitignored). Nothing writes into `models/`, `params/` or `results/`. The old `twiglet_v3.xml` symlink is gone, so `run_all.sh` can no longer overwrite `mini_bdx/robots/twiglet_v334/`.
- Reference results are in `experiments/twiglet_sim/results/`, and the index of every sim is [experiments/README.md](../experiments/README.md).

TODO:
- Train an ONNX walking policy with Open_Duck_Playground for this body (19 DoF, arms).
- Export the policy and the robot to the Open_Duck_Mini_Runtime format.
