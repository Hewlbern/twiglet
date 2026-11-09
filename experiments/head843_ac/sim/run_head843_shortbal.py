"""Backward-pitch catch and heading trim on the frozen short-step gait.

The traj file is not modified. Gains are new. The long-stride negative yaw
gain is not used: on this gait a negative yaw gain spun the heading, and a
positive gain held it. Cap stays 0.06 rad. Train seeds start at 140200.
Selection starts at 141000. A 400-seed screen starts at 142000 only if the
selection gate passes. The 4000-seed qualification is not started here.
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
import run_head843_traj as T
import run_head843_search as S
import run_head843_heading as H
import run_head843_yawstate as Y

KEYS = ["pitch_on", "k_pitch", "k_rate", "k_yaw"]
LO = np.array([0.06, 0.2, 0.0, 0.0])
HI = np.array([0.14, 1.2, 0.35, 0.20])
MU = np.array([0.08, 0.9, 0.20, 0.12])
SIG = np.array([0.015, 0.2, 0.06, 0.04])

def jobs(mode, r, base, gait, ztraj, seeds, xml, Ts):
    js = T.jobs("cand", ztraj, base, gait, seeds, xml, Ts)
    if mode == "cand":
        for j in js:
            j["headarm"]["short_balance"] = dict(
                pitch_on=float(r[0]), k_pitch=float(r[1]), k_rate=float(r[2]),
                k_yaw=float(r[3]), pitch_sign=1.0)
    return js

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    ztraj = np.array([json.load(open(os.path.join(ROOT, "results", "head843_traj_qual_prereg.json")))["candidate"]["z"][k] for k in T.KEYS], float)
    rng = np.random.default_rng(28)
    mu, sig = MU.copy(), SIG.copy()
    log = []
    for gen in range(4):
        nom = list(range(140200 + gen * 4, 140200 + gen * 4 + 4))
        long = list(range(140400 + gen * 2, 140400 + gen * 2 + 2))
        heavy = list(range(140500 + gen * 2, 140500 + gen * 2 + 2))
        low = list(range(140600 + gen * 2, 140600 + gen * 2 + 2))
        Z = np.minimum(HI, np.maximum(LO, mu + sig * rng.standard_normal((6, 4))))
        Z[0] = np.minimum(HI, np.maximum(LO, mu))
        packed, owners = [], []
        for i in range(6):
            packed += jobs("cand", Z[i], base, gait, ztraj, nom, H.NOM, 10.0)
            packed += jobs("cand", Z[i], base, gait, ztraj, long, H.NOM, 20.0)
            packed += jobs("cand", Z[i], base, gait, ztraj, heavy, H.HI, 10.0)
            packed += jobs("cand", Z[i], base, gait, ztraj, low, H.LO, 10.0)
            owners += [i] * (len(nom) + len(long) + len(heavy) + len(low))
        rows = Y.run_jobs(packed)
        buckets = [[] for _ in range(6)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        stats = [T.enrich(b) for b in buckets]
        order = sorted(range(6), key=lambda i: stats[i]["score"], reverse=True)
        mu = Z[order[:3]].mean(0)
        sig = np.maximum(Z[order[:3]].std(0), 0.4 * SIG)
        best = stats[order[0]]
        rec = dict(gen=gen, succ=int(best["succ"]), n=int(best["n"]), progress=best["progress"],
                   frac15=best["frac15"], score=best["score"],
                   z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", gen, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_shortbal_ckpt.json"), "w"), indent=1)
    r = np.array([log[-1]["z"][k] for k in KEYS], float)
    plan = (
        ("n10", list(range(141000, 141200)), H.NOM, 10.0),
        ("n20", list(range(141300, 141340)), H.NOM, 20.0),
        ("hi", list(range(141400, 141424)), H.HI, 10.0),
        ("lo", list(range(141400, 141424)), H.LO, 10.0),
    )
    blocks = {}
    for name, seeds, xml, Ts in plan:
        for mode in ("cand", "base"):
            s = T.enrich(Y.run_jobs(jobs(mode, r, base, gait, ztraj, seeds, xml, Ts)))
            blocks[name + "_" + mode] = s
            Y.show(name + " " + mode, s)
    p10 = Y.pair(blocks["n10_cand"], blocks["n10_base"])
    p20 = Y.pair(blocks["n20_cand"], blocks["n20_base"])
    phi = Y.pair(blocks["hi_cand"], blocks["hi_base"])
    c20, b20 = blocks["n20_cand"], blocks["n20_base"]
    c10, b10 = blocks["n10_cand"], blocks["n10_base"]
    # Attainable against a ~99.5% baseline: do not demand several extra survivals.
    gate = (
        p10["net"] >= -1
        and c20["frac15"] <= b20["frac15"] - 0.10
        and c10["progress"] >= 0.09
        and c20["progress"] >= 0.09
        and phi["net"] >= -1
        and (c20["shoulder_mean"] or 0) >= 18
        and (c20["shoulder_pp"] or 0) >= 16
        and (c20["head_yaw_pp"] or 0) >= 14
    )
    print("GATE", gate, "10", p10["net"], p10["mcnemar_p"], "20y", round(c20["frac15"], 3), round(b20["frac15"], 3), "20net", p20["net"], flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               z={k: float(v) for k, v in zip(KEYS, r)}, base_npy="params/head843_traj.npy",
               selection=blocks, pair10=p10, pair20=p20, pair_heavy=phi, gate=gate)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_shortbal.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_shortbal.npy"), r)
    # 400-seed screen, fresh. Not the 4000.
    screen = {}
    seeds = list(range(142000, 142400))
    for mode in ("cand", "base"):
        screen[mode] = T.enrich(Y.run_jobs(jobs(mode, r, base, gait, ztraj, seeds, H.NOM, 10.0)))
        screen[mode]["wilson"] = Y.wilson(screen[mode]["succ"], 400)
        Y.show("screen " + mode, screen[mode])
    screen["pair"] = Y.pair(screen["cand"], screen["base"])
    s20 = list(range(142500, 142540))
    for mode in ("cand", "base"):
        screen["long_" + mode] = T.enrich(Y.run_jobs(jobs(mode, r, base, gait, ztraj, s20, H.NOM, 20.0)))
        Y.show("screen20 " + mode, screen["long_" + mode])
    screen["long_pair"] = Y.pair(screen["long_cand"], screen["long_base"])
    bseeds = list(range(142600, 142620))
    for name, xml in (("hi", H.HI), ("lo", H.LO)):
        for mode in ("cand", "base"):
            screen[name + "_" + mode] = T.enrich(Y.run_jobs(jobs(mode, r, base, gait, ztraj, bseeds, xml, 10.0)))
            Y.show("screen " + name + " " + mode, screen[name + "_" + mode])
        screen[name + "_pair"] = Y.pair(screen[name + "_cand"], screen[name + "_base"])
    hold = (
        screen["pair"]["net"] >= -2
        and screen["long_cand"]["frac15"] <= screen["long_base"]["frac15"] - 0.08
        and screen["cand"]["progress"] >= 0.09
    )
    screen["promising"] = hold
    print("SCREEN", screen["pair"]["net"], screen["pair"]["mcnemar_p"],
          "y20", round(screen["long_cand"]["frac15"], 3), round(screen["long_base"]["frac15"], 3),
          "promising", hold, flush=True)
    json.dump(screen, open(os.path.join(ROOT, "results", "head843_shortbal_screen.json"), "w"), indent=1, default=float)
    print("wrote screen", round(time.time() - t0, 1), flush=True)

if __name__ == "__main__":
    main()
