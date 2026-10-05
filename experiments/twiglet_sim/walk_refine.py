"""v3.2: small local refine of the v3 max-speed gait on the v3.2 model (heavier 200 mm head). 24 perturbations (sigma 4 % of range)
x 10 randomized seeds (5000-5009); the best by success x speed is re-scored on the standard 20 seeds (5000-5019) by walk_eval.py.
twiglet repo copy: writes out/walk_v3[_eff]_best_refined.npy (+ _unrefined) if it beats the unrefined params; the shipped params are never overwritten."""
import sys, os, json, numpy as np, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk_search as W
def score(R):
    s = np.mean([not r["fell"] for r in R]); v = np.mean([r["dx"] / 10.0 for r in R if not r["fell"]] or [0]); return s, v
if __name__ == "__main__":
    SUF = "_eff" if "--eff" in sys.argv else ""
    best0 = np.load(W.params_path(SUF)); pool = mp.Pool(7); rng = np.random.default_rng(int(os.environ.get("REFINE_SEED", "32")))
    cands = [best0] + [np.clip(best0 + rng.normal(0, 0.04, len(best0)) * (W.HI - W.LO), W.LO, W.HI) for _ in range(24)]
    res = []
    for i, x in enumerate(cands):
        s, v = score(W.batch([x] * 10, range(5000, 5010), True, pool, T=10.0)); res.append((s * v if s >= 0.9 else s * v * 0.5, s, v, i)); print(i, round(s, 2), round(v, 3), flush=True)
    res.sort(reverse=True); top = [cands[r[3]] for r in res[:3]]
    fin = []
    for x in top:
        s, v = score(W.batch([x] * 20, range(5000, 5020), True, pool, T=10.0)); fin.append((s, v, x)); print("final", round(s, 2), round(v, 3), flush=True)
    s0, v0 = score(W.batch([best0] * 20, range(5000, 5020), True, pool, T=10.0))
    fin.sort(key=lambda t: (t[0], t[1]), reverse=True); s, v, x = fin[0]
    rep = dict(unrefined=dict(success=s0, speed=v0), refined=dict(success=s, speed=v), accepted=bool((s, v) > (s0, v0)))
    if rep["accepted"]:
        np.save(os.path.join(W.OUT, f"walk_v3{SUF}_best_unrefined.npy"), best0); np.save(os.path.join(W.OUT, f"walk_v3{SUF}_best_refined.npy"), x)   # repo copy: never overwrites the shipped params
    json.dump(rep, open(os.path.join(W.OUT, f"walk_refine{SUF}.json"), "w"), indent=1, default=float); print(rep, flush=True)
