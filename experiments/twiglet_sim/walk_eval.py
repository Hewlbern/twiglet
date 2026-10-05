"""v3.1: re-evaluate the v3 gaits (walk_v3[_eff]_best.npy, found by walk_search.py on v3) on the v3.1 model: nominal 10 s + 20 randomized
trials (same randomization/seeds as walk_search). Optional small CEM refine (--refine N). Writes walk_v3[_eff].json in the walk_search format."""
import sys, os, json, math, numpy as np, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk_search as W
from simlib import LEGS, STALL, RATED, OUT, params_path
if __name__ == "__main__":
    SUF = "_eff" if "--eff" in sys.argv else ""
    best = np.load(params_path(SUF)); pool = mp.Pool(5)
    Rr = W.batch([best] * 20, range(5000, 5020), True, pool, T=10.0)
    succ = float(np.mean([not r["fell"] for r in Rr])); spd = float(np.mean([r["dx"] / 10.0 for r in Rr if not r["fell"]] or [0]))
    nom = W.evaluate((best, 0, False, 10.0)); keys_t = sorted(nom["stats"].keys())
    peak = {k: max(r["stats"][k]["peak"] for r in Rr if r["stats"]) for k in keys_t}
    rms = {k: round(float(np.mean([r["stats"][k]["rms"] for r in Rr if r["stats"]])), 3) for k in keys_t}
    out = dict(variant="v3.2", source="v3 gait params re-evaluated on the v3.2 model; max-speed gait locally refined by walk_refine.py (see walk_refine_v32.json)", best_params={k: round(float(v), 4) for k, v in zip(W.KEYS, best)},
               success_rate_randomized=succ, speed_mps_randomized_mean=round(spd, 4),
               nominal=dict(dx_10s=round(nom["dx"], 3), dy=round(nom["dy"], 3), yaw_deg=round(math.degrees(nom["yaw"]), 1), fell=nom["fell"]),
               torque_nominal=nom["stats"], torque_peak_over_randomized=peak, torque_rms_mean_randomized=rms, bus_current_A_mean=round(nom["I"], 2),
               limits=dict(stall_Nm=STALL, rated_continuous_Nm=RATED))
    json.dump(out, open(os.path.join(OUT, f"walk_v3{SUF}.json"), "w"), indent=1, default=float)
    print(SUF, "succ", succ, "speed", round(spd, 3), "I", out["bus_current_A_mean"], "nominal", out["nominal"], flush=True)
