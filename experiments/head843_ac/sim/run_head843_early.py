"""Early stance transfer once pitch passes the transient. Fresh seeds only.

The heading vector stays head843_yawstate.npy. This file trains the pitch
onset, the pitch-rate onset, the swing-lift reduction, and the hip share.
Held-outs start at 118000 and run only if the selection gate clears.
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

KEYS = ["pitch_on", "rate_on", "depth", "hip"]
LO = np.array([0.16, 0.15, 0.08, 0.00])
HI = np.array([0.24, 0.55, 0.20, 0.10])
MU = np.array([0.18, 0.25, 0.16, 0.06])
SIG = np.array([0.015, 0.06, 0.03, 0.02])

def early_of(r):
    return dict(pitch_on=float(r[0]), rate_on=float(r[1]), k=1.5, depth=float(r[2]), hip=float(r[3]))

def jobs(mode, r, z_yaw, base, gait, seeds, xml, T):
    out = []
    for s in seeds:
        if mode == "frozen":
            g = np.array(gait, float)
            sp = S.spec_from(base)
            sp["k_support_yaw"] = 0.0
        else:
            g, sp = Y.apply_z(z_yaw, base, gait)
            if mode == "cand":
                sp["early"] = early_of(r)
        out.append(dict(x=[float(v) for v in g], seed=int(s), rand=True, T=T, headarm=sp,
                        command_sign=-1.0, measure_path=True, pitch_tail=True, trunk_stats=True,
                        xml=xml))
    return out

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    z_yaw = np.load(os.path.join(ROOT, "params", "head843_yawstate.npy"))
    rng = np.random.default_rng(24)
    mu, sig = MU.copy(), SIG.copy()
    log = []
    for g in range(3):
        nom = list(range(116000 + g * 3, 116000 + g * 3 + 3))
        heavy = list(range(116100 + g * 2, 116100 + g * 2 + 2))
        low = list(range(116140 + g * 2, 116140 + g * 2 + 2))
        Z = np.minimum(HI, np.maximum(LO, mu + sig * rng.standard_normal((5, 4))))
        Z[0] = np.minimum(HI, np.maximum(LO, mu))
        packed, owners = [], []
        for i in range(5):
            packed += jobs("cand", Z[i], z_yaw, base, gait, nom, H.NOM, 20.0)
            packed += jobs("cand", Z[i], z_yaw, base, gait, heavy, H.HI, 10.0)
            packed += jobs("cand", Z[i], z_yaw, base, gait, low, H.LO, 10.0)
            owners += [i] * (len(nom) + len(heavy) + len(low))
        rows = Y.run_jobs(packed)
        buckets = [[] for _ in range(5)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        stats = [Y.fit(b) for b in buckets]
        order = sorted(range(5), key=lambda i: stats[i]["score"], reverse=True)
        mu = Z[order[:3]].mean(0)
        sig = np.maximum(Z[order[:3]].std(0), 0.40 * SIG)
        best = stats[order[0]]
        rec = dict(gen=g, succ=int(best["succ"]), n=int(best["n"]), progress=best["progress"],
                   frac15=best["frac15"], z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", g, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_early_ckpt.json"), "w"), indent=1)
    r = np.array([log[-1]["z"][k] for k in KEYS], float)
    sel = list(range(117000, 117048))
    sel20 = list(range(117100, 117124))
    selb = list(range(117200, 117216))

    def pack(mode, seeds, xml, T):
        rows = Y.run_jobs(jobs(mode, r, z_yaw, base, gait, seeds, xml, T))
        s = Y.fit(rows)
        s["early_med"] = float(np.median([row.get("early_n") or 0 for row in rows]))
        return s

    blocks = {}
    for name, seeds, xml, T in (
        ("n10", sel, H.NOM, 10.0), ("n20", sel20, H.NOM, 20.0),
        ("hi", selb, H.HI, 10.0), ("lo", selb, H.LO, 10.0),
    ):
        for mode in ("cand", "frozen", "parent"):
            s = pack(mode, seeds, xml, T)
            blocks[f"{name}_{mode}"] = s
            Y.show(f"{name} {mode}", s)
            print("  early_med", round(s["early_med"], 1), flush=True)
    pf = Y.pair(blocks["n10_cand"], blocks["n10_frozen"])
    pp = Y.pair(blocks["n10_cand"], blocks["n10_parent"])
    hf = Y.pair(blocks["hi_cand"], blocks["hi_frozen"])
    print("pair frozen", pf["net"], pf["mcnemar_p"], "parent", pp["net"], "heavy", hf["net"], flush=True)
    c10, f10 = blocks["n10_cand"], blocks["n10_frozen"]
    c20, p20, f20 = blocks["n20_cand"], blocks["n20_parent"], blocks["n20_frozen"]
    gate = (
        pf["net"] >= 3 and pp["net"] >= 0
        and c20["frac15"] <= p20["frac15"] + 0.05
        and c10["progress"] >= 0.10 and c10["progress"] >= f10["progress"] - 0.015
        and blocks["hi_cand"]["succ"] + 1 >= blocks["hi_frozen"]["succ"]
        and (c20["shoulder_mean"] or 0) >= 18 and (c20["shoulder_pp"] or 0) >= 16
        and (c20["head_yaw_pp"] or 0) >= 14
    )
    print("GATE", gate, flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               early={k: float(v) for k, v in zip(KEYS, r)},
               selection=blocks, pair_frozen=pf, pair_parent=pp, pair_heavy=hf, gate=gate)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_early.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_early.npy"), r)
    held = {"early": out["early"]}
    for tag, start in (("A", 118000), ("B", 118200)):
        seeds = list(range(start, start + 200))
        for mode in ("cand", "frozen", "parent"):
            held[tag + "_" + mode] = pack(mode, seeds, H.NOM, 10.0)
            held[tag + "_" + mode]["wilson"] = Y.wilson(held[tag + "_" + mode]["succ"], 200)
            Y.show(tag + " " + mode, held[tag + "_" + mode])
        held[tag + "_pair_frozen"] = Y.pair(held[tag + "_cand"], held[tag + "_frozen"])
        held[tag + "_pair_parent"] = Y.pair(held[tag + "_cand"], held[tag + "_parent"])
        print(tag, "frozen", held[tag + "_pair_frozen"]["net"], held[tag + "_pair_frozen"]["mcnemar_p"],
              "parent", held[tag + "_pair_parent"]["net"], flush=True)
    s20 = list(range(118500, 118540))
    for mode in ("cand", "frozen", "parent"):
        held["long_" + mode] = pack(mode, s20, H.NOM, 20.0)
        Y.show("long " + mode, held["long_" + mode])
    bseeds = list(range(118600, 118640))
    for name, xml in (("nom", H.NOM), ("lo", H.LO), ("hi", H.HI)):
        for mode in ("cand", "frozen"):
            held[f"b_{name}_{mode}"] = pack(mode, bseeds, xml, 10.0)
            Y.show(f"b {name} {mode}", held[f"b_{name}_{mode}"])
        held[f"b_{name}_pair"] = Y.pair(held[f"b_{name}_cand"], held[f"b_{name}_frozen"])
        print("bound", name, held[f"b_{name}_pair"]["net"], held[f"b_{name}_pair"]["mcnemar_p"], flush=True)
    ns = held["A_cand"]["succ"] + held["B_cand"]["succ"]
    fs = held["A_frozen"]["succ"] + held["B_frozen"]["succ"]
    ps = held["A_parent"]["succ"] + held["B_parent"]["succ"]
    fa = set(held["A_cand"]["fell"]) | set(held["B_cand"]["fell"])
    fb = set(held["A_frozen"]["fell"]) | set(held["B_frozen"]["fell"])
    fp = set(held["A_parent"]["fell"]) | set(held["B_parent"]["fell"])
    from math import comb
    def net(other):
        saved, cost = sorted(other - fa), sorted(fa - other)
        n = len(saved) + len(cost)
        k = min(len(saved), len(cost)) if n else 0
        p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
        return dict(saved=len(saved), cost=len(cost), net=len(saved) - len(cost), mcnemar_p=p,
                    cost_seeds=cost, saved_seeds=saved)
    held["combined"] = dict(cand=ns, frozen=fs, parent=ps,
                            cand_wilson=Y.wilson(ns, 400), frozen_wilson=Y.wilson(fs, 400),
                            parent_wilson=Y.wilson(ps, 400), vs_frozen=net(fb), vs_parent=net(fp))
    print("COMBINED", ns, fs, ps, held["combined"]["vs_frozen"], held["combined"]["vs_parent"], flush=True)
    held["seconds"] = round(time.time() - t0, 1)
    json.dump(held, open(os.path.join(ROOT, "results", "head843_early_held.json"), "w"), indent=1, default=float)
    print("wrote held", held["seconds"], flush=True)

if __name__ == "__main__":
    main()
