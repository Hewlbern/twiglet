"""Joint gait search on the corrected 0.84258 kg head. Does not write reliable.npy.

Stage 1 retunes the 12 gait parameters with the arms still. Stage 2 continues
from that gait and also moves the support gains, a zero-mean arm-phase hip yaw,
and a planted-ankle feedforward. Each generation is scored on a fresh slice of
the train pool. Validation seeds are not used for selection.

  python run_head843_search.py
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
from walk_search import KEYS, LO, HI
import run_balance as B
import run_recover as R
from simlib import params_path
from manoeuvre import rollout

XML = os.path.join(HERE, "models", "twiglet_v3_v335ac_head843.xml")
CKPT = os.path.join(ROOT, "results", "head843_search_ckpt.json")
# Local step around the inherited gait. Not the full search box.
SIG = np.array([0.12, 0.03, 0.04, 0.03, 0.25, 0.03, 0.04, 0.25, 0.03, 0.15, 0.03, 0.03])
CTRL_KEYS = ["body_lean", "k_place", "k_hip", "k_lat", "k_roll_extra", "k_yaw_phase", "ank_arm"]
CTRL0 = np.array([-0.04, 0.6, -0.25, 0.45, 0.30, 0.0, 0.0])
CTRL_SIG = np.array([0.02, 0.15, 0.12, 0.12, 0.10, 0.015, 0.015])
CTRL_LO = np.array([-0.08, 0.0, -0.6, 0.0, 0.0, -0.03, -0.04])
CTRL_HI = np.array([0.02, 1.0, 0.2, 0.8, 0.6, 0.03, 0.04])

def clip_gait(x):
    return np.minimum(HI, np.maximum(LO, x))

def clip_ctrl(c):
    return np.minimum(CTRL_HI, np.maximum(CTRL_LO, c))

def spec_from(ctrl):
    c = dict(zip(CTRL_KEYS, [float(v) for v in ctrl]))
    sp = R.base(name="search", body_lean=c["body_lean"], k_place=c["k_place"], d_place=0.05,
                k_hip=c["k_hip"], k_lat=c["k_lat"], d_lat=0.05,
                k_roll_extra=c["k_roll_extra"], d_roll_extra=0.04,
                k_yaw_phase=c["k_yaw_phase"], ank_arm=c["ank_arm"], ank_lim=0.04)
    return sp

def jobs_for(x, ctrl, seeds, T, arms):
    head = spec_from(ctrl) if arms else None
    out = []
    for s in seeds:
        out.append(dict(x=[float(v) for v in x], seed=int(s), rand=True, T=T,
                        headarm=head, command_sign=-1.0, measure_path=True,
                        pitch_tail=True, xml=XML))
    return out

def run_jobs(js):
    with mp.Pool(4) as pool:
        return pool.map(rollout, js, chunksize=2)

def summarize(rows):
    n = len(rows)
    surv = [r for r in rows if r["fell"] is None]
    ys = np.degrees([r["yaw_change"] for r in rows])
    sh = hy = shm = None
    if surv and surv[0].get("motion_mean_deg"):
        means, pps, hys = [], [], []
        for r in surv:
            mn, pp = r.get("motion_mean_deg") or {}, r.get("motion_pp_deg") or {}
            if "shoulder_L" in mn:
                means.append(0.5 * (mn["shoulder_L"] + mn["shoulder_R"]))
                pps.append(0.5 * (pp["shoulder_L"] + pp["shoulder_R"]))
            if "head_yaw" in pp:
                hys.append(pp["head_yaw"])
        if means:
            shm, sh = float(np.median(means)), float(np.median(pps))
        if hys:
            hy = float(np.median(hys))
    gt8 = []
    for r in rows:
        p = r.get("pitch_tail") or {}
        if p.get("frac_gt8") is not None:
            gt8.append(p["frac_gt8"])
    return dict(
        succ=len(surv), n=n,
        progress=float(np.mean([r["dx"] / r["T"] for r in rows])),
        speed=None if not surv else float(np.mean([r["speed"] for r in surv])),
        yaw_mean=float(np.mean(ys)),
        frac15=float(np.mean(np.abs(ys) > 15)),
        gt8=None if not gt8 else float(np.mean(gt8)),
        shoulder_mean=shm, shoulder_pp=sh, head_yaw_pp=hy,
        fell=[r["seed"] for r in rows if r["fell"] is not None],
    )

def rank_key(s):
    # Survival, then forward progress, then a yaw-tail penalty. Speed is not required.
    return (s["succ"], s["progress"] - 0.15 * s["frac15"], -abs(s["yaw_mean"]))

def cem(mu_g, sig_g, mu_c, sig_c, arms, gen0, ngen, pop, nseed, seed0, rng, log):
    elite_g = np.tile(mu_g, (4, 1))
    elite_c = np.tile(mu_c, (4, 1))
    for g in range(ngen):
        seeds = list(range(seed0 + (gen0 + g) * nseed, seed0 + (gen0 + g + 1) * nseed))
        G = clip_gait(mu_g + sig_g * rng.standard_normal((pop, len(mu_g))))
        C = clip_ctrl(mu_c + sig_c * rng.standard_normal((pop, len(mu_c))))
        # Keep the current mean in the population.
        G[0], C[0] = mu_g, mu_c
        packed = []
        owners = []
        for i in range(pop):
            js = jobs_for(G[i], C[i], seeds, 8.0, arms)
            packed.extend(js)
            owners.extend([i] * len(seeds))
        rows = run_jobs(packed)
        buckets = [[] for _ in range(pop)]
        for own, row in zip(owners, rows):
            buckets[own].append(row)
        stats = [summarize(b) for b in buckets]
        order = sorted(range(pop), key=lambda i: rank_key(stats[i]), reverse=True)
        keep = order[:4]
        elite_g = G[keep]
        elite_c = C[keep]
        mu_g = elite_g.mean(0)
        mu_c = elite_c.mean(0)
        sig_g = np.maximum(elite_g.std(0), 0.25 * sig_g)
        sig_c = np.maximum(elite_c.std(0), 0.25 * sig_c)
        best = stats[order[0]]
        rec = dict(gen=gen0 + g, arms=arms, seeds=[seeds[0], len(seeds)],
                   best=best, gait={k: round(float(v), 5) for k, v in zip(KEYS, G[order[0]])},
                   ctrl={k: round(float(v), 5) for k, v in zip(CTRL_KEYS, C[order[0]])})
        log.append(rec)
        print("gen", rec["gen"], "arms", arms, f"{best['succ']}/{best['n']}",
              "prog", round(best["progress"], 3), "y15", round(best["frac15"], 3),
              "gt8", None if best["gt8"] is None else round(best["gt8"], 4), flush=True)
        json.dump(log, open(CKPT, "w"), indent=1, default=float)
    return mu_g, mu_c, elite_g[0], elite_c[0]

def main():
    t0 = time.time()
    rng = np.random.default_rng(843)
    x0 = np.load(params_path("")).astype(float)
    log = []
    print("stage1 arms-free gait", flush=True)
    _, _, g1, _ = cem(x0, SIG, CTRL0, np.zeros_like(CTRL_SIG), False, 0, 5, 12, 12, 100000, rng, log)
    print("stage2 arms on, joint support", flush=True)
    _, _, g2, c2 = cem(g1, 0.5 * SIG, CTRL0, CTRL_SIG, True, 5, 5, 12, 12, 100000, rng, log)
    # Validation is a seed block the search never touched.
    val = list(range(100400, 100480))
    inherited = jobs_for(x0, CTRL0, val, 10.0, True)
    found = jobs_for(g2, c2, val, 10.0, True)
    free_old = jobs_for(x0, CTRL0, val, 10.0, False)
    free_new = jobs_for(g2, CTRL0, val, 10.0, False)
    blocks = {
        "val_inherited_arms": summarize(run_jobs(inherited)),
        "val_searched_arms": summarize(run_jobs(found)),
        "val_inherited_free": summarize(run_jobs(free_old)),
        "val_searched_free": summarize(run_jobs(free_new)),
    }
    for k, s in blocks.items():
        print(k, f"{s['succ']}/{s['n']}", "prog", round(s["progress"], 3),
              "y15", round(s["frac15"], 3), "sh", s["shoulder_mean"], "pp", s["shoulder_pp"],
              "hy", s["head_yaw_pp"], flush=True)
    out = dict(seconds=round(time.time() - t0, 1), xml="twiglet_v3_v335ac_head843.xml",
               generations=log, validation_seeds=[100400, 80], validation=blocks,
               searched_gait={k: float(v) for k, v in zip(KEYS, g2)},
               searched_ctrl={k: float(v) for k, v in zip(CTRL_KEYS, c2)})
    # Save the vector beside reliable.npy, never over it.
    np.save(os.path.join(ROOT, "params", "head843_search.npy"), np.array(g2, float))
    path = os.path.join(ROOT, "results", "head843_search.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print("wrote", path, out["seconds"], flush=True)

if __name__ == "__main__":
    main()
