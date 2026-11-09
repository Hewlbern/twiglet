"""(d) Walking: parametric open-loop gait + IMU feedback (ankle pitch, hip roll), random search + CEM refinement, then a
robustness check over randomized trials (mass +-10 %, friction 0.6-1.0, armature/damping +-30 %, 0-10 ms latency, backlash 0.4 deg).
Usage: python walk_search.py v2|stock [n_random] [--video]"""
import sys, os, json, math, numpy as np, mujoco, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from simlib import *
from episode import run
V = sys.argv[1]; NR = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 700; VIDEO = "--video" in sys.argv
EFF = 0.6 if "--eff" in sys.argv else 0.0          # energy-aware objective: penalise mean leg-joint RMS torque (N.m)
SUF = "_eff" if EFF else ""
KEYS = ["f", "stride", "lift", "sway", "sway_ph", "crouch", "lean", "kp_pitch", "kd_pitch", "kp_roll", "kd_roll", "ank_off"]
LO = np.array([1.0, 0.00, 0.05, 0.00, -math.pi, 0.15, -0.15, -1.5, -0.15, -1.5, -0.15, -0.15])
HI = np.array([3.0, 0.35, 0.45, 0.22, math.pi, 0.65, 0.15, 1.5, 0.15, 1.5, 0.15, 0.15])
T_EP = 8.0
def evaluate(args):
    x, seed, rand, T = args
    p = dict(zip(KEYS, x)); p["ramp"] = 1.0
    m, d = load(V); rng = np.random.default_rng(seed)
    lat = 0
    if rand: randomize(m, rng); lat = int(rng.integers(0, 6))
    sv = Servo(m, latency_steps=lat); g = Gait(sv.names, p, V); q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN[V])
    reset(m, d, q0); rec = Recorder(sv.names, sv.stall)
    info = run(m, d, sv, lambda t, r, gy: g(t, r, gy, q0), T, V, rec=rec)
    fell = info["fell"] is not None
    st = rec.stats(); legrms = np.mean([v["rms"] for k, v in st.items() if any(j in k for j in LEGS)]) if st else 0.0
    score = info["dx"] - 0.5 * abs(info["dy"]) - 0.1 * abs(info["yaw"]) - (1.0 + 0.2 * (T - info["t"]) if fell else 0.0) - EFF * legrms * T / 8.0
    return dict(score=score, fell=fell, dx=info["dx"], dy=info["dy"], yaw=info["yaw"], t=info["t"], stats=rec.stats(), I=rec.current())
def batch(xs, seeds, rand, pool, T=T_EP): return pool.map(evaluate, [(x, s, rand, T) for x, s in zip(xs, seeds)])
if __name__ == "__main__":
    rng = np.random.default_rng(1); pool = mp.Pool(7); out = {"variant": V}
    X = LO + (HI - LO) * rng.random((NR, len(KEYS)))
    R = batch(X, range(NR), False, pool); sc = np.array([r["score"] for r in R])
    print("random: best", sc.max().round(3), "no-fall", sum(not r["fell"] for r in R), flush=True)
    # CEM refinement (nominal model + one randomized trial each, averaged)
    elite = X[np.argsort(-sc)[:12]]
    for it in range(5):
        mu, sd = elite.mean(0), elite.std(0) + 0.02 * (HI - LO)
        Xn = np.clip(mu + sd * rng.standard_normal((140, len(KEYS))), LO, HI)
        R1 = batch(Xn, range(140), False, pool); R2 = batch(Xn, range(1000 + it * 1000, 1140 + it * 1000), True, pool)
        s = np.array([(a["score"] + b["score"]) / 2 for a, b in zip(R1, R2)])
        allX = np.vstack([elite, Xn]); 
        es = np.array([evaluate((x, 7, False, T_EP))["score"] for x in elite[:0]]) if False else None
        X = np.vstack([X, Xn]); sc = np.concatenate([sc, s])
        elite = X[np.argsort(-sc)[:12]]
        print("cem", it, "best", s.max().round(3), "mean elite", np.sort(sc)[-12:].mean().round(3), flush=True)
    # robustness of the 6 best candidates: 20 randomized trials of 10 s
    cands = X[np.argsort(-sc)[:6]]; rob = []
    for c in cands:
        Rr = batch([c] * 20, range(5000, 5020), True, pool, T=10.0)
        succ = np.mean([not r["fell"] for r in Rr]); spd = np.mean([r["dx"] / 10.0 for r in Rr if not r["fell"]] or [0])
        rob.append((succ * max(spd, 0), succ, spd, c, Rr))
        print("cand succ", succ, "speed", round(spd, 3), flush=True)
    if EFF:   # prefer low torque among robust candidates: success * speed / (leg rms)
        for i, z in enumerate(rob):
            lr = np.mean([np.mean([r["stats"][k]["rms"] for k in r["stats"] if any(j in k for j in LEGS)]) for r in z[4] if r["stats"]])
            rob[i] = (z[1] * max(z[2], 0) / max(lr, 0.2),) + z[1:]
    rob.sort(key=lambda z: -z[0]); _, succ, spd, best, Rr = rob[0]
    nom = evaluate((best, 0, False, 10.0))
    keys_t = sorted(nom["stats"].keys())
    peak = {k: max(r["stats"][k]["peak"] for r in Rr if r["stats"]) for k in keys_t}
    rms = {k: round(float(np.mean([r["stats"][k]["rms"] for r in Rr if r["stats"]])), 3) for k in keys_t}
    out.update(best_params={k: round(float(v), 4) for k, v in zip(KEYS, best)}, success_rate_randomized=float(succ),
               speed_mps_randomized_mean=round(float(spd), 4), nominal=dict(dx_10s=round(nom["dx"], 3), dy=round(nom["dy"], 3), yaw_deg=round(math.degrees(nom["yaw"]), 1), fell=nom["fell"]),
               torque_nominal=nom["stats"], torque_peak_over_randomized=peak, torque_rms_mean_randomized=rms,
               bus_current_A_mean=round(nom["I"], 2), limits=dict(stall_Nm=STALL, rated_continuous_Nm=RATED),
               candidates=[dict(success=float(z[1]), speed=round(float(z[2]), 4)) for z in rob],
               n_evaluated=int(len(sc)))
    json.dump(out, open(os.path.join(OUT, f"walk_{V}{SUF}_search.json"), "w"), indent=1, default=float)
    np.save(os.path.join(OUT, f"walk_{V}{SUF}_best_search.npy"), best)   # repo copy: never overwrites the shipped params
    print("best", out["best_params"], "succ", succ, "speed", spd, flush=True)
