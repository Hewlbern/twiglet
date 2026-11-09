"""Swing-foot capture from IMU pitch rate, on the frozen searched gait.

Not a pitch-angle threshold and not the yaw-state parent. The comparison is
the frozen search. Train seeds start at 123000. Selection starts at 123500.
Held-outs start at 124000 only if a predeclared gate can actually be met:
the required paired gain cannot exceed the number of frozen falls.
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

KEYS = ["k", "cap", "rate_on"]
LO = np.array([0.04, 0.03, 0.15])
HI = np.array([0.35, 0.12, 0.55])
MU = np.array([0.15, 0.08, 0.30])
SIG = np.array([0.05, 0.02, 0.06])

def jobs(mode, r, base, gait, seeds, xml, T):
    out = []
    for s in seeds:
        sp = S.spec_from(base)
        sp["k_support_yaw"] = 0.0
        if mode == "cand":
            sp["rate_capture"] = dict(k=float(r[0]), cap=float(r[1]), rate_on=float(r[2]))
        out.append(dict(x=[float(v) for v in gait], seed=int(s), rand=True, T=T, headarm=sp,
                        command_sign=-1.0, measure_path=True, pitch_tail=True, trunk_stats=True,
                        xml=xml))
    return out

def enrich(rows):
    s = Y.fit(rows)
    gt10 = [((r.get("pitch_tail") or {}).get("frac_gt10")) for r in rows]
    gt10 = [v for v in gt10 if v is not None]
    s["gt10"] = float(np.mean(gt10)) if gt10 else 0.0
    caps = [r.get("capture_n") or 0 for r in rows]
    s["capture_med"] = float(np.median(caps))
    stall = s.get("stall") or {}
    s["score"] = (s["progress"] - 4.0 * (1.0 - s["succ"] / max(s["n"], 1))
                  - 0.45 * s["frac15"] - 0.8 * s["gt10"] - 0.15 * (stall.get("main") or 0.0))
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
    rng = np.random.default_rng(26)
    mu, sig = MU.copy(), SIG.copy()
    log = []
    for gen in range(3):
        nom = list(range(123000 + gen * 4, 123000 + gen * 4 + 4))
        long = list(range(123040 + gen * 2, 123040 + gen * 2 + 2))
        heavy = list(range(123080 + gen * 2, 123080 + gen * 2 + 2))
        Z = np.minimum(HI, np.maximum(LO, mu + sig * rng.standard_normal((6, 3))))
        Z[0] = np.minimum(HI, np.maximum(LO, mu))
        packed, owners = [], []
        for i in range(6):
            packed += jobs("cand", Z[i], base, gait, nom, H.NOM, 10.0)
            packed += jobs("cand", Z[i], base, gait, long, H.NOM, 20.0)
            packed += jobs("cand", Z[i], base, gait, heavy, H.HI, 10.0)
            owners += [i] * (len(nom) + len(long) + len(heavy))
        rows = Y.run_jobs(packed)
        buckets = [[] for _ in range(6)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        stats = [enrich(b) for b in buckets]
        order = sorted(range(6), key=lambda i: stats[i]["score"], reverse=True)
        mu = Z[order[:3]].mean(0)
        sig = np.maximum(Z[order[:3]].std(0), 0.4 * SIG)
        best = stats[order[0]]
        rec = dict(gen=gen, succ=int(best["succ"]), n=int(best["n"]), progress=best["progress"],
                   frac15=best["frac15"], gt10=best["gt10"], score=best["score"],
                   z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", gen, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "gt10", round(best["gt10"], 4), "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_capture_ckpt.json"), "w"), indent=1)
    r = np.array([log[-1]["z"][k] for k in KEYS], float)
    blocks = {}
    plan = (
        ("A", list(range(123500, 123600)), H.NOM, 10.0),
        ("B", list(range(123600, 123700)), H.NOM, 10.0),
        ("n20", list(range(123800, 123832)), H.NOM, 20.0),
        ("hi", list(range(123900, 123920)), H.HI, 10.0),
        ("lo", list(range(123900, 123920)), H.LO, 10.0),
    )
    for name, seeds, xml, T in plan:
        for mode in ("cand", "frozen"):
            s = enrich(Y.run_jobs(jobs(mode, r, base, gait, seeds, xml, T)))
            blocks[name + "_" + mode] = s
            Y.show(name + " " + mode, s)
            print("  gt10", round(s["gt10"], 4), "cap", round(s["capture_med"], 1), flush=True)
    pA = Y.pair(blocks["A_cand"], blocks["A_frozen"])
    pB = Y.pair(blocks["B_cand"], blocks["B_frozen"])
    p20 = Y.pair(blocks["n20_cand"], blocks["n20_frozen"])
    phi = Y.pair(blocks["hi_cand"], blocks["hi_frozen"])
    # Combined 10 s blocks only. Not mixed with the 20 s horizon.
    fa = set(blocks["A_cand"]["fell"]) | set(blocks["B_cand"]["fell"])
    fb = set(blocks["A_frozen"]["fell"]) | set(blocks["B_frozen"]["fell"])
    saved, cost = sorted(fb - fa), sorted(fa - fb)
    net = len(saved) - len(cost)
    F = len(fb)
    n = len(saved) + len(cost)
    kk = min(len(saved), len(cost)) if n else 0
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(kk + 1)) / 2 ** n)
    # A required gain larger than F is impossible. Ask for 3 only when F allows it.
    need = 3 if F >= 3 else None
    c20, f20 = blocks["n20_cand"], blocks["n20_frozen"]
    cA, fA = blocks["A_cand"], blocks["A_frozen"]
    gate = False
    reason = "underpowered" if F < 3 else "no gain"
    if need is not None and net >= need and net <= F and p20["net"] >= -1 and phi["net"] >= -1:
        if (cA["progress"] + blocks["B_cand"]["progress"]) / 2 >= (fA["progress"] + blocks["B_frozen"]["progress"]) / 2 - 0.02:
            if c20["frac15"] <= f20["frac15"] + 0.10 and (c20["shoulder_mean"] or 0) >= 18 and (c20["shoulder_pp"] or 0) >= 16 and (c20["head_yaw_pp"] or 0) >= 14:
                if cA["progress"] >= 0.12:
                    gate = True
                    reason = "open"
    print("COMBINED10", "frozen_falls", F, "net", net, "p", p, "need", need, "20s", p20["net"], "heavy", phi["net"], "GATE", gate, reason, flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               z={k: float(v) for k, v in zip(KEYS, r)}, selection=blocks,
               combined10=dict(frozen_falls=F, saved=len(saved), cost=len(cost), net=net, mcnemar_p=p,
                               saved_seeds=saved, cost_seeds=cost, need=need, reason=reason),
               pair20=p20, pair_heavy=phi, gate=gate,
               gate_note="Required paired net is 3 only when the frozen gait fell at least 3 times on the combined 200-seed 10 s selection. A requirement of +4 against a 79/80 block is impossible and is not used.")
    json.dump(out, open(os.path.join(ROOT, "results", "head843_capture.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", reason, flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_capture.npy"), r)
    held = {"z": out["z"]}
    for tag, start in (("A", 124000), ("B", 124200)):
        seeds = list(range(start, start + 200))
        for mode in ("cand", "frozen"):
            held[tag + "_" + mode] = enrich(Y.run_jobs(jobs(mode, r, base, gait, seeds, H.NOM, 10.0)))
            held[tag + "_" + mode]["wilson"] = Y.wilson(held[tag + "_" + mode]["succ"], 200)
            Y.show(tag + " " + mode, held[tag + "_" + mode])
        held[tag + "_pair"] = Y.pair(held[tag + "_cand"], held[tag + "_frozen"])
        print(tag, held[tag + "_pair"]["net"], held[tag + "_pair"]["mcnemar_p"], flush=True)
    s20 = list(range(124500, 124540))
    for mode in ("cand", "frozen"):
        held["long_" + mode] = enrich(Y.run_jobs(jobs(mode, r, base, gait, s20, H.NOM, 20.0)))
        Y.show("long " + mode, held["long_" + mode])
    held["long_pair"] = Y.pair(held["long_cand"], held["long_frozen"])
    bseeds = list(range(124600, 124640))
    for name, xml in (("nom", H.NOM), ("lo", H.LO), ("hi", H.HI)):
        for mode in ("cand", "frozen"):
            held["b_" + name + "_" + mode] = enrich(Y.run_jobs(jobs(mode, r, base, gait, bseeds, xml, 10.0)))
            Y.show("b " + name + " " + mode, held["b_" + name + "_" + mode])
        held["b_" + name + "_pair"] = Y.pair(held["b_" + name + "_cand"], held["b_" + name + "_frozen"])
    ns = held["A_cand"]["succ"] + held["B_cand"]["succ"]
    fs = held["A_frozen"]["succ"] + held["B_frozen"]["succ"]
    fa = set(held["A_cand"]["fell"]) | set(held["B_cand"]["fell"])
    fb = set(held["A_frozen"]["fell"]) | set(held["B_frozen"]["fell"])
    saved, cost = sorted(fb - fa), sorted(fa - fb)
    n = len(saved) + len(cost)
    k = min(len(saved), len(cost)) if n else 0
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    held["combined"] = dict(cand=ns, frozen=fs, cand_wilson=Y.wilson(ns, 400), frozen_wilson=Y.wilson(fs, 400),
                            net=len(saved) - len(cost), mcnemar_p=p, saved_seeds=saved, cost_seeds=cost)
    print("HELD", held["combined"], flush=True)
    held["seconds"] = round(time.time() - t0, 1)
    json.dump(held, open(os.path.join(ROOT, "results", "head843_capture_held.json"), "w"), indent=1, default=float)
    print("wrote held", held["seconds"], flush=True)

if __name__ == "__main__":
    main()
