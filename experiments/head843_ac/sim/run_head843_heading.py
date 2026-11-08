"""20 s heading search on the frozen head843 gait. Does not overwrite head843_search.npy.

The gait vector stays params/head843_search.npy. This file moves support-phase
yaw authority, the slow-yaw limit, the arm-phase yaw term, and the planted ankle
feedforward. Each score mixes nominal 20 s trials with the heavy head bound.
"""
import os, sys, json, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_search as S
from simlib import params_path
from manoeuvre import rollout

NOM = os.path.join(HERE, "models", "twiglet_v3_v335ac_head843.xml")
HI = os.path.join(HERE, "models", "twiglet_v3_v335ac_head885.xml")
LO = os.path.join(HERE, "models", "twiglet_v3_v335ac_head823.xml")
KEYS = ["k_support_yaw", "slow_yaw_ulim", "k_yaw_phase", "ank_arm"]
MU0 = np.array([-0.20, 0.02, -0.0155, -0.018])
SIG = np.array([0.08, 0.008, 0.01, 0.008])
LO_B = np.array([-0.45, 0.01, -0.03, -0.04])
HI_B = np.array([0.05, 0.04, 0.03, 0.02])

def clip(z):
    return np.minimum(HI_B, np.maximum(LO_B, z))

def head_of(z, base_ctrl):
    sp = S.spec_from(base_ctrl)
    sp["k_support_yaw"] = float(z[0])
    sp["slow_yaw_ulim"] = float(z[1])
    sp["k_yaw_phase"] = float(z[2])
    sp["ank_arm"] = float(z[3])
    sp["ank_lim"] = 0.04
    return sp

def jobs(z, base_ctrl, gait, seeds, xml, T):
    h = head_of(z, base_ctrl)
    return [dict(x=[float(v) for v in gait], seed=int(s), rand=True, T=T, headarm=h,
                 command_sign=-1.0, measure_path=True, pitch_tail=True, xml=xml) for s in seeds]

def run(js):
    with mp.Pool(4) as pool:
        return pool.map(rollout, js, chunksize=2)

def fit(rows):
    s = S.summarize(rows)
    # All seeds, including falls. A walk that does not progress is not a solution.
    pen = 0.0
    if s["progress"] < 0.10:
        pen = 5.0
    motion_ok = True
    if s["shoulder_mean"] is not None and (s["shoulder_mean"] < 18 or (s["shoulder_pp"] or 0) < 16 or (s["head_yaw_pp"] or 0) < 14):
        motion_ok = False
        pen += 3.0
    score = s["progress"] - 0.55 * s["frac15"] - 1.6 * (1.0 - s["succ"] / s["n"]) - pen
    s["score"] = score
    s["motion_ok"] = motion_ok
    return s

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base_ctrl = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    rng = np.random.default_rng(20)
    mu, sig = MU0.copy(), SIG.copy()
    log = []
    for g in range(4):
        nom = list(range(102200 + g * 4, 102200 + g * 4 + 4))
        heavy = list(range(102500 + g * 2, 102500 + g * 2 + 2))
        Z = clip(mu + sig * rng.standard_normal((8, 4)))
        Z[0] = clip(mu)
        packed, owners = [], []
        for i in range(8):
            packed.extend(jobs(Z[i], base_ctrl, gait, nom, NOM, 20.0))
            packed.extend(jobs(Z[i], base_ctrl, gait, heavy, HI, 20.0))
            owners.extend([i] * (len(nom) + len(heavy)))
        rows = run(packed)
        buckets = [[] for _ in range(8)]
        for o, r in zip(owners, rows):
            buckets[o].append(r)
        stats = [fit(b) for b in buckets]
        order = sorted(range(8), key=lambda i: stats[i]["score"], reverse=True)
        keep = order[:3]
        mu = Z[keep].mean(0)
        sig = np.maximum(Z[keep].std(0), 0.35 * SIG)
        best = stats[order[0]]
        rec = dict(gen=g, seeds_nominal=nom, seeds_heavy=heavy,
                   best={k: best[k] for k in ("succ", "n", "progress", "speed", "yaw_mean", "frac15", "gt8", "shoulder_mean", "shoulder_pp", "head_yaw_pp", "score")},
                   z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", g, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "yaw", round(best["yaw_mean"], 1),
              "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_heading_ckpt.json"), "w"), indent=1)
    # Validation, new seeds, 20 s, nominal only. Benchmark is k_support_yaw = 0 and the frozen search gains.
    val = list(range(102800, 102840))
    z_best = np.array([log[-1]["z"][k] for k in KEYS], float)
    z_base = np.array([0.0, 0.02, search["searched_ctrl"]["k_yaw_phase"], search["searched_ctrl"]["ank_arm"]])
    val_new = fit(run(jobs(z_best, base_ctrl, gait, val, NOM, 20.0)))
    val_base = fit(run(jobs(z_base, base_ctrl, gait, val, NOM, 20.0)))
    print("val new", val_new["succ"], val_new["progress"], val_new["frac15"], val_new["yaw_mean"], val_new["shoulder_mean"], val_new["shoulder_pp"], val_new["head_yaw_pp"], flush=True)
    print("val base", val_base["succ"], val_base["progress"], val_base["frac15"], val_base["yaw_mean"], flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               z_best={k: float(v) for k, v in zip(KEYS, z_best)},
               validation_seeds=[102800, 40],
               val_new=val_new, val_base=val_base)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_heading.json"), "w"), indent=1, default=float)
    print("wrote heading", out["seconds"], flush=True)

if __name__ == "__main__":
    main()
