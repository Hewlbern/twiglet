"""Broader leg-trajectory search so the ankle target is one the servo can track.

The negative tracking error on a loaded foot is present at pitch near 0°, so it
is a trajectory offset, not a pitch-feedback spike. ank_off is allowed outside
the old search box, still inside the ankle soft limit. No ankle-command ease
and no swing-hip offset. Baseline is the frozen head843 search. Train seeds
start at 125200. Selection starts at 126000. Held-outs start at 127000 only
if the frozen gait fell at least 3 times and the paired gain is at least 3.
"""
import os, sys, json, time
from math import comb
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_search as S
import run_head843_heading as H
import run_head843_yawstate as Y

KEYS = ["f", "stride", "lift", "crouch", "lean", "kp_pitch", "ank_off", "body_lean", "k_hip"]
# ank_off wider than walk_search's ±0.15 because a 16° tracking gap cannot be
# removed inside that box. Still inside the ankle soft limit of -65° to +47°.
LO = np.array([1.70, 0.10, 0.18, 0.15, -0.15, -1.50, -0.40, -0.08, -0.55])
HI = np.array([2.60, 0.24, 0.45, 0.45,  0.05,  0.40,  0.30,  0.00,  0.10])
SIG = np.array([0.10, 0.03, 0.05, 0.05, 0.04, 0.30, 0.08, 0.015, 0.08])

def mu_of(search):
    g = search["searched_gait"]
    c = search["searched_ctrl"]
    return np.array([g["f"], g["stride"], g["lift"], g["crouch"], g["lean"], g["kp_pitch"], g["ank_off"],
                     c["body_lean"], c["k_hip"]], float)

def jobs(mode, r, base, gait, seeds, xml, T):
    out = []
    for s in seeds:
        sp = S.spec_from(base)
        sp["k_support_yaw"] = 0.0
        g = np.array(gait, float)
        if mode == "cand":
            g[0], g[2], g[5], g[6], g[7], g[11] = r[0], r[2], r[3], r[4], r[5], r[6]
            g[1] = r[1]
            sp["body_lean"] = float(r[7])
            sp["k_hip"] = float(r[8])
        out.append(dict(x=[float(v) for v in g], seed=int(s), rand=True, T=T, headarm=sp,
                        command_sign=-1.0, measure_path=True, pitch_tail=True, track_ankle=True,
                        xml=xml))
    return out

def enrich(rows):
    s = Y.fit(rows)
    fa = [((r.get("ankle_track") or {}).get("frac_abs")) for r in rows]
    fn = [((r.get("ankle_track") or {}).get("frac_neg")) for r in rows]
    fa = [v for v in fa if v is not None]
    fn = [v for v in fn if v is not None]
    s["frac_abs"] = float(np.mean(fa)) if fa else 0.0
    s["frac_neg"] = float(np.mean(fn)) if fn else 0.0
    gt10 = [((r.get("pitch_tail") or {}).get("frac_gt10")) for r in rows]
    gt10 = [v for v in gt10 if v is not None]
    s["gt10"] = float(np.mean(gt10)) if gt10 else 0.0
    stall = s.get("stall") or {}
    s["score"] = (s["progress"] - 4.0 * (1.0 - s["succ"] / max(s["n"], 1))
                  - 0.35 * s["frac15"] - 0.70 * s["frac_neg"] - 0.25 * s["frac_abs"]
                  - 0.15 * (stall.get("ankle") or 0.0))
    if s["progress"] < 0.10:
        s["score"] -= 5.0
    if s["shoulder_mean"] is not None and (s["shoulder_mean"] < 18 or (s["shoulder_pp"] or 0) < 16 or (s["head_yaw_pp"] or 0) < 14):
        s["score"] -= 3.0
    return s

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    mu = mu_of(search)
    sig = SIG.copy()
    rng = np.random.default_rng(27)
    log = []
    for gen in range(5):
        nom = list(range(125200 + gen * 4, 125200 + gen * 4 + 4))
        long = list(range(125400 + gen * 2, 125400 + gen * 2 + 2))
        heavy = list(range(125500 + gen * 2, 125500 + gen * 2 + 2))
        low = list(range(125600 + gen * 2, 125600 + gen * 2 + 2))
        Z = np.minimum(HI, np.maximum(LO, mu + sig * rng.standard_normal((8, 9))))
        Z[0] = np.minimum(HI, np.maximum(LO, mu))
        packed, owners = [], []
        for i in range(8):
            packed += jobs("cand", Z[i], base, gait, nom, H.NOM, 10.0)
            packed += jobs("cand", Z[i], base, gait, long, H.NOM, 20.0)
            packed += jobs("cand", Z[i], base, gait, heavy, H.HI, 10.0)
            packed += jobs("cand", Z[i], base, gait, low, H.LO, 10.0)
            owners += [i] * (len(nom) + len(long) + len(heavy) + len(low))
        rows = Y.run_jobs(packed)
        buckets = [[] for _ in range(8)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        stats = [enrich(b) for b in buckets]
        order = sorted(range(8), key=lambda i: stats[i]["score"], reverse=True)
        mu = Z[order[:3]].mean(0)
        sig = np.maximum(Z[order[:3]].std(0), 0.40 * SIG)
        best = stats[order[0]]
        rec = dict(gen=gen, succ=int(best["succ"]), n=int(best["n"]), progress=best["progress"],
                   frac15=best["frac15"], frac_neg=best["frac_neg"], frac_abs=best["frac_abs"],
                   score=best["score"], z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", gen, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "neg", round(best["frac_neg"], 3), "y15", round(best["frac15"], 3),
              "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_traj_ckpt.json"), "w"), indent=1)
    r = np.array([log[-1]["z"][k] for k in KEYS], float)
    plan = (
        ("A", list(range(126000, 126100)), H.NOM, 10.0),
        ("B", list(range(126100, 126200)), H.NOM, 10.0),
        ("n20", list(range(126400, 126440)), H.NOM, 20.0),
        ("hi", list(range(126500, 126524)), H.HI, 10.0),
        ("lo", list(range(126500, 126524)), H.LO, 10.0),
    )
    blocks = {}
    for name, seeds, xml, T in plan:
        for mode in ("cand", "frozen"):
            s = enrich(Y.run_jobs(jobs(mode, r, base, gait, seeds, xml, T)))
            blocks[name + "_" + mode] = s
            Y.show(name + " " + mode, s)
            print("  neg", round(s["frac_neg"], 3), "abs", round(s["frac_abs"], 3),
                  "ankle", None if s["stall"]["ankle"] is None else round(s["stall"]["ankle"], 4), flush=True)
    pA = Y.pair(blocks["A_cand"], blocks["A_frozen"])
    pB = Y.pair(blocks["B_cand"], blocks["B_frozen"])
    p20 = Y.pair(blocks["n20_cand"], blocks["n20_frozen"])
    phi = Y.pair(blocks["hi_cand"], blocks["hi_frozen"])
    fa = set(blocks["A_cand"]["fell"]) | set(blocks["B_cand"]["fell"])
    fb = set(blocks["A_frozen"]["fell"]) | set(blocks["B_frozen"]["fell"])
    saved, cost = sorted(fb - fa), sorted(fa - fb)
    net = len(saved) - len(cost)
    F = len(fb)
    n = len(saved) + len(cost)
    kk = min(len(saved), len(cost)) if n else 0
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(kk + 1)) / 2 ** n)
    c20, f20 = blocks["n20_cand"], blocks["n20_frozen"]
    prog_c = 0.5 * (blocks["A_cand"]["progress"] + blocks["B_cand"]["progress"])
    prog_f = 0.5 * (blocks["A_frozen"]["progress"] + blocks["B_frozen"]["progress"])
    need = 3 if F >= 3 else None
    gate = False
    reason = "underpowered" if F < 3 else "no gain"
    if need is not None and net >= need and p20["net"] >= -1 and phi["net"] >= -1:
        if prog_c >= 0.10 and prog_c >= prog_f - 0.03:
            if c20["frac15"] <= f20["frac15"] + 0.12 and (c20["shoulder_mean"] or 0) >= 18 and (c20["shoulder_pp"] or 0) >= 16 and (c20["head_yaw_pp"] or 0) >= 14:
                gate = True
                reason = "open"
    print("COMBINED10", "F", F, "net", net, "p", p, "need", need, "20", p20["net"], "hi", phi["net"], "GATE", gate, reason, flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log, z={k: float(v) for k, v in zip(KEYS, r)},
               selection=blocks, combined10=dict(frozen_falls=F, net=net, mcnemar_p=p, saved=len(saved), cost=len(cost),
                                                 saved_seeds=saved, cost_seeds=cost, need=need, reason=reason),
               pair20=p20, pair_heavy=phi, gate=gate)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_traj.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", reason, flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_traj.npy"), r)
    held = {"z": out["z"]}
    for tag, start in (("A", 127000), ("B", 127200)):
        seeds = list(range(start, start + 200))
        for mode in ("cand", "frozen"):
            held[tag + "_" + mode] = enrich(Y.run_jobs(jobs(mode, r, base, gait, seeds, H.NOM, 10.0)))
            held[tag + "_" + mode]["wilson"] = Y.wilson(held[tag + "_" + mode]["succ"], 200)
            Y.show(tag + " " + mode, held[tag + "_" + mode])
        held[tag + "_pair"] = Y.pair(held[tag + "_cand"], held[tag + "_frozen"])
        print(tag, held[tag + "_pair"]["net"], held[tag + "_pair"]["mcnemar_p"], flush=True)
    s20 = list(range(127500, 127540))
    for mode in ("cand", "frozen"):
        held["long_" + mode] = enrich(Y.run_jobs(jobs(mode, r, base, gait, s20, H.NOM, 20.0)))
        Y.show("long " + mode, held["long_" + mode])
    held["long_pair"] = Y.pair(held["long_cand"], held["long_frozen"])
    bseeds = list(range(127600, 127640))
    for name, xml in (("nom", H.NOM), ("lo", H.LO), ("hi", H.HI)):
        for mode in ("cand", "frozen"):
            held["b_" + name + "_" + mode] = enrich(Y.run_jobs(jobs(mode, r, base, gait, bseeds, xml, 10.0)))
            Y.show("b " + name + " " + mode, held["b_" + name + "_" + mode])
        held["b_" + name + "_pair"] = Y.pair(held["b_" + name + "_cand"], held["b_" + name + "_frozen"])
    ns = held["A_cand"]["succ"] + held["B_cand"]["succ"]
    fs = held["A_frozen"]["succ"] + held["B_frozen"]["succ"]
    fa = set(held["A_cand"]["fell"]) | set(held["B_cand"]["fell"])
    fb2 = set(held["A_frozen"]["fell"]) | set(held["B_frozen"]["fell"])
    saved, cost = sorted(fb2 - fa), sorted(fa - fb2)
    n = len(saved) + len(cost)
    kk = min(len(saved), len(cost)) if n else 0
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(kk + 1)) / 2 ** n)
    held["combined"] = dict(cand=ns, frozen=fs, cand_wilson=Y.wilson(ns, 400), frozen_wilson=Y.wilson(fs, 400),
                            net=len(saved) - len(cost), mcnemar_p=p, saved_seeds=saved, cost_seeds=cost)
    print("HELD", held["combined"], flush=True)
    held["seconds"] = round(time.time() - t0, 1)
    json.dump(held, open(os.path.join(ROOT, "results", "head843_traj_held.json"), "w"), indent=1, default=float)
    print("wrote held", held["seconds"], flush=True)

if __name__ == "__main__":
    main()
