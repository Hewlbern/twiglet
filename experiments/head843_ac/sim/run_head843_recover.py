"""Pitch-window swing recovery on the frozen yaw-state heading law.

Does not overwrite head843_search.npy, head843_support020.npy, or
head843_yawstate.npy. Recovery parameters are the only ones trained.
Heading gains stay at the yaw-state vector. Held-outs start at 114000 and
run only after the selection gate. Train seeds start at 112000.
"""
import os, sys, json, time
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

RKEYS = ["pitch_on", "k_pitch", "k_prate", "place_cap", "roll_on", "k_roll", "lat_cap"]
LO = np.array([0.10, 0.0, 0.0, 0.03, 0.08, 0.0, 0.02])
HI = np.array([0.22, 1.6, 0.40, 0.14, 0.22, 1.4, 0.10])
MU = np.array([0.16, 0.80, 0.15, 0.08, 0.14, 0.60, 0.06])
SIG = np.array([0.02, 0.25, 0.05, 0.015, 0.02, 0.20, 0.015])

def recover_of(r):
    return dict(
        pitch_on=float(r[0]), k_pitch=float(r[1]), k_prate=float(r[2]), place_cap=float(r[3]),
        roll_on=float(r[4]), k_roll=float(r[5]), lat_cap=float(r[6]),
    )

def jobs(mode, r, z_yaw, base, gait, seeds, xml, T):
    if mode == "frozen":
        g = np.array(gait, float)
        sp = S.spec_from(base)
        sp["k_support_yaw"] = 0.0
    else:
        g, sp = Y.apply_z(z_yaw, base, gait)
        if mode == "cand":
            sp["recover"] = recover_of(r)
    return [dict(x=[float(v) for v in g], seed=int(s), rand=True, T=T, headarm=sp,
                 command_sign=-1.0, measure_path=True, pitch_tail=True, trunk_stats=True,
                 xml=xml) for s in seeds]

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    z_yaw = np.load(os.path.join(ROOT, "params", "head843_yawstate.npy"))
    rng = np.random.default_rng(23)
    mu, sig = MU.copy(), SIG.copy()
    log = []
    for g in range(4):
        nom = list(range(112000 + g * 3, 112000 + g * 3 + 3))
        heavy = list(range(112100 + g * 2, 112100 + g * 2 + 2))
        low = list(range(112150 + g * 2, 112150 + g * 2 + 2))
        Z = np.minimum(HI, np.maximum(LO, mu + sig * rng.standard_normal((6, 7))))
        Z[0] = np.minimum(HI, np.maximum(LO, mu))
        packed, owners = [], []
        for i in range(6):
            packed += jobs("cand", Z[i], z_yaw, base, gait, nom, H.NOM, 20.0)
            packed += jobs("cand", Z[i], z_yaw, base, gait, heavy, H.HI, 20.0)
            packed += jobs("cand", Z[i], z_yaw, base, gait, low, H.LO, 20.0)
            owners += [i] * (len(nom) + len(heavy) + len(low))
        rows = Y.run_jobs(packed)
        buckets = [[] for _ in range(6)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        stats = [Y.fit(b) for b in buckets]
        order = sorted(range(6), key=lambda i: stats[i]["score"], reverse=True)
        keep = order[:3]
        mu = Z[keep].mean(0)
        sig = np.maximum(Z[keep].std(0), 0.40 * SIG)
        best = stats[order[0]]
        rec = dict(gen=g, succ=best["succ"], n=best["n"], progress=best["progress"], frac15=best["frac15"],
                   score=best["score"], z={k: round(float(v), 5) for k, v in zip(RKEYS, Z[order[0]])})
        log.append(rec)
        print("gen", g, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_recover_ckpt.json"), "w"), indent=1)
    r = np.array([log[-1]["z"][k] for k in RKEYS], float)
    sel10 = list(range(113000, 113040))
    sel20 = list(range(113100, 113124))
    selb = list(range(113200, 113220))

    def pack(mode, seeds, xml, T):
        return Y.fit(Y.run_jobs(jobs(mode, r, z_yaw, base, gait, seeds, xml, T)))

    blocks = {}
    for name, seeds, xml, T in (
        ("n10", sel10, H.NOM, 10.0),
        ("n20", sel20, H.NOM, 20.0),
        ("hi", selb, H.HI, 10.0),
        ("lo", selb, H.LO, 10.0),
    ):
        for mode in ("cand", "frozen", "parent"):
            s = pack(mode, seeds, xml, T)
            blocks[f"{name}_{mode}"] = s
            Y.show(f"{name} {mode}", s)
    c10, f10, p10 = blocks["n10_cand"], blocks["n10_frozen"], blocks["n10_parent"]
    c20, f20, p20 = blocks["n20_cand"], blocks["n20_frozen"], blocks["n20_parent"]
    chi, fhi = blocks["hi_cand"], blocks["hi_frozen"]
    clo, flo = blocks["lo_cand"], blocks["lo_frozen"]
    gate = (
        c10["succ"] >= f10["succ"] and c10["succ"] >= p10["succ"]
        and (c10["succ"] + chi["succ"]) > (f10["succ"] + fhi["succ"])
        and c20["frac15"] <= p20["frac15"] + 0.05
        and c20["progress"] >= 0.10 and c20["progress"] >= f20["progress"] - 0.015
        and (c20["shoulder_mean"] or 0) >= 18 and (c20["shoulder_pp"] or 0) >= 16
        and (c20["head_yaw_pp"] or 0) >= 14
        and clo["succ"] + 1 >= flo["succ"]
    )
    print("GATE", gate, flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               recover={k: float(v) for k, v in zip(RKEYS, r)},
               yawstate="head843_yawstate.npy", selection=blocks, gate=gate)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_recover.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_recover.npy"), r)
    held = {"recover": out["recover"]}
    for tag, start in (("A", 114000), ("B", 114200)):
        seeds = list(range(start, start + 200))
        held[tag + "_cand"] = pack("cand", seeds, H.NOM, 10.0)
        held[tag + "_frozen"] = pack("frozen", seeds, H.NOM, 10.0)
        held[tag + "_parent"] = pack("parent", seeds, H.NOM, 10.0)
        for mode in ("cand", "frozen", "parent"):
            held[tag + "_" + mode]["wilson"] = Y.wilson(held[tag + "_" + mode]["succ"], 200)
            Y.show(tag + " " + mode, held[tag + "_" + mode])
        held[tag + "_pair_frozen"] = Y.pair(held[tag + "_cand"], held[tag + "_frozen"])
        held[tag + "_pair_parent"] = Y.pair(held[tag + "_cand"], held[tag + "_parent"])
        print(tag, "vs frozen", held[tag + "_pair_frozen"]["net"], held[tag + "_pair_frozen"]["mcnemar_p"],
              "vs parent", held[tag + "_pair_parent"]["net"], held[tag + "_pair_parent"]["mcnemar_p"], flush=True)
    s20 = list(range(114500, 114540))
    for mode in ("cand", "frozen", "parent"):
        held["long_" + mode] = pack(mode, s20, H.NOM, 20.0)
        Y.show("long " + mode, held["long_" + mode])
    held["long_pair_frozen"] = Y.pair(held["long_cand"], held["long_frozen"])
    bseeds = list(range(114600, 114640))
    for name, xml in (("nom", H.NOM), ("lo", H.LO), ("hi", H.HI)):
        for mode in ("cand", "frozen"):
            held[f"bound_{name}_{mode}"] = pack(mode, bseeds, xml, 10.0)
            Y.show(f"bound {name} {mode}", held[f"bound_{name}_{mode}"])
        held[f"bound_{name}_pair"] = Y.pair(held[f"bound_{name}_cand"], held[f"bound_{name}_frozen"])
        print("bound", name, held[f"bound_{name}_pair"]["net"], held[f"bound_{name}_pair"]["mcnemar_p"], flush=True)
    ns = held["A_cand"]["succ"] + held["B_cand"]["succ"]
    fs = held["A_frozen"]["succ"] + held["B_frozen"]["succ"]
    ps = held["A_parent"]["succ"] + held["B_parent"]["succ"]
    fa = set(held["A_cand"]["fell"]) | set(held["B_cand"]["fell"])
    fb = set(held["A_frozen"]["fell"]) | set(held["B_frozen"]["fell"])
    fp = set(held["A_parent"]["fell"]) | set(held["B_parent"]["fell"])
    def net(other):
        saved, cost = sorted(other - fa), sorted(fa - other)
        n = len(saved) + len(cost)
        k = min(len(saved), len(cost)) if n else 0
        from math import comb
        p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
        return dict(saved=len(saved), cost=len(cost), net=len(saved) - len(cost), mcnemar_p=p,
                    cost_seeds=cost, saved_seeds=saved)
    held["combined"] = dict(cand=ns, frozen=fs, parent=ps,
                            cand_wilson=Y.wilson(ns, 400), frozen_wilson=Y.wilson(fs, 400),
                            parent_wilson=Y.wilson(ps, 400),
                            vs_frozen=net(fb), vs_parent=net(fp))
    print("COMBINED", ns, "frozen", fs, "parent", ps, held["combined"]["vs_frozen"], held["combined"]["vs_parent"], flush=True)
    held["seconds"] = round(time.time() - t0, 1)
    json.dump(held, open(os.path.join(ROOT, "results", "head843_recover_held.json"), "w"), indent=1, default=float)
    print("wrote held", held["seconds"], flush=True)

if __name__ == "__main__":
    main()
