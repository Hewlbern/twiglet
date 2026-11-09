"""Joint arm-phase and step-timing search on the yaw-state heading law.

The early-transfer gate is not in this search. Amplitudes A_sh and Y_yaw stay
at their current values. Head phase tracks arm phase. Train seeds start at
119000. Selection starts at 120000. Held-outs start at 121000 and run only
if the selection gate clears. A perfect short block is not that gate.
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

KEYS = ["f", "stride", "lift", "sway_ph", "arm_phase", "body_lean", "k_place", "k_hip"]

def center(search, z_yaw):
    g = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    c = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    # Yaw-state already moved sway, lateral, roll-extra, and placement.
    g2, sp = Y.apply_z(z_yaw, c, g)
    return g2, sp

def bounds(g, sp):
    mu = np.array([g[0], g[1], g[2], g[4], 1.2, sp["body_lean"], sp["k_place"], sp["k_hip"]], float)
    lo = np.array([2.00, 0.13, 0.32, 0.45, 0.30, -0.070, 0.30, -0.45])
    hi = np.array([2.35, 0.19, 0.44, 0.95, 2.20, -0.020, 0.75, -0.05])
    sig = np.array([0.04, 0.012, 0.018, 0.05, 0.28, 0.008, 0.05, 0.04])
    return mu, lo, hi, sig

def jobs(mode, r, z_yaw, base, gait0, seeds, xml, T):
    out = []
    for s in seeds:
        if mode == "frozen":
            g = np.array(gait0, float)
            sp = S.spec_from(base)
            sp["k_support_yaw"] = 0.0
        else:
            g, sp = Y.apply_z(z_yaw, base, gait0)
            if mode == "cand":
                g = np.array(g, float)
                g[0], g[1], g[2], g[4] = r[0], r[1], r[2], r[3]
                sp["arm_phase"] = float(r[4])
                sp["head_phase"] = float(r[4])
                sp["body_lean"] = float(r[5])
                sp["k_place"] = float(r[6])
                sp["k_hip"] = float(r[7])
        out.append(dict(x=[float(v) for v in g], seed=int(s), rand=True, T=T, headarm=sp,
                        command_sign=-1.0, measure_path=True, pitch_tail=True, trunk_stats=True,
                        xml=xml))
    return out

def enrich(rows):
    s = Y.fit(rows)
    gt10 = []
    for r in rows:
        p = r.get("pitch_tail") or {}
        if p.get("frac_gt10") is not None:
            gt10.append(p["frac_gt10"])
    s["gt10"] = float(np.mean(gt10)) if gt10 else 0.0
    stall = s.get("stall") or {}
    s["score"] = (s["progress"] - 5.0 * (1.0 - s["succ"] / s["n"]) - 0.70 * s["frac15"]
                  - 1.4 * s["gt10"] - 0.20 * (stall.get("main") or 0.0))
    if s["progress"] < 0.10:
        s["score"] -= 5.0
    if s["shoulder_mean"] is not None and (s["shoulder_mean"] < 18 or (s["shoulder_pp"] or 0) < 16 or (s["head_yaw_pp"] or 0) < 14):
        s["score"] -= 3.0
    return s

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait0 = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    z_yaw = np.load(os.path.join(ROOT, "params", "head843_yawstate.npy"))
    g_c, sp_c = center(search, z_yaw)
    mu, lo, hi, sig = bounds(g_c, sp_c)
    rng = np.random.default_rng(25)
    log = []
    for gen in range(4):
        nom10 = list(range(119000 + gen * 4, 119000 + gen * 4 + 4))
        nom20 = list(range(119100 + gen * 2, 119100 + gen * 2 + 2))
        heavy = list(range(119200 + gen * 2, 119200 + gen * 2 + 2))
        Z = np.minimum(hi, np.maximum(lo, mu + sig * rng.standard_normal((8, 8))))
        Z[0] = np.minimum(hi, np.maximum(lo, mu))
        packed, owners = [], []
        for i in range(8):
            packed += jobs("cand", Z[i], z_yaw, base, gait0, nom10, H.NOM, 10.0)
            packed += jobs("cand", Z[i], z_yaw, base, gait0, nom20, H.NOM, 20.0)
            packed += jobs("cand", Z[i], z_yaw, base, gait0, heavy, H.HI, 10.0)
            owners += [i] * (len(nom10) + len(nom20) + len(heavy))
        rows = Y.run_jobs(packed)
        buckets = [[] for _ in range(8)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        stats = [enrich(b) for b in buckets]
        order = sorted(range(8), key=lambda i: stats[i]["score"], reverse=True)
        mu = Z[order[:3]].mean(0)
        sig = np.maximum(Z[order[:3]].std(0), 0.35 * sig)
        best = stats[order[0]]
        rec = dict(gen=gen, succ=int(best["succ"]), n=int(best["n"]), progress=best["progress"],
                   frac15=best["frac15"], gt10=best["gt10"], score=best["score"],
                   z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", gen, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "gt10", round(best["gt10"], 4),
              "score", round(best["score"], 3), "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_coord_ckpt.json"), "w"), indent=1)
    r = np.array([log[-1]["z"][k] for k in KEYS], float)
    sel10 = list(range(120000, 120080))
    sel20 = list(range(120300, 120332))
    selb = list(range(120400, 120420))

    def pack(mode, seeds, xml, T):
        return enrich(Y.run_jobs(jobs(mode, r, z_yaw, base, gait0, seeds, xml, T)))

    blocks = {}
    for name, seeds, xml, T in (
        ("n10", sel10, H.NOM, 10.0), ("n20", sel20, H.NOM, 20.0),
        ("hi", selb, H.HI, 10.0), ("lo", selb, H.LO, 10.0),
    ):
        for mode in ("cand", "frozen", "parent"):
            s = pack(mode, seeds, xml, T)
            blocks[name + "_" + mode] = s
            Y.show(name + " " + mode, s)
            print("  gt10", round(s["gt10"], 4), "stall", None if s["stall"]["main"] is None else round(s["stall"]["main"], 4), flush=True)
    pf = Y.pair(blocks["n10_cand"], blocks["n10_frozen"])
    pp = Y.pair(blocks["n10_cand"], blocks["n10_parent"])
    p20 = Y.pair(blocks["n20_cand"], blocks["n20_frozen"])
    print("10s vs frozen", pf, "vs parent", pp["net"], "20s vs frozen", p20["net"], p20["mcnemar_p"], flush=True)
    c10, f10 = blocks["n10_cand"], blocks["n10_frozen"]
    c20, f20, p20s = blocks["n20_cand"], blocks["n20_frozen"], blocks["n20_parent"]
    gate = (
        pf["net"] >= 4 and pp["net"] >= 0
        and p20["net"] >= -1
        and c20["frac15"] <= p20s["frac15"] + 0.08
        and c10["progress"] >= 0.12 and c10["progress"] >= f10["progress"] - 0.02
        and blocks["hi_cand"]["succ"] + 1 >= blocks["hi_frozen"]["succ"]
        and (c20["shoulder_mean"] or 0) >= 18 and (c20["shoulder_pp"] or 0) >= 16
        and (c20["head_yaw_pp"] or 0) >= 14
        and c20["gt10"] <= f20["gt10"] + 0.01
    )
    print("GATE", gate, flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               z={k: float(v) for k, v in zip(KEYS, r)},
               selection=blocks, pair10_frozen=pf, pair10_parent=pp, pair20_frozen=p20, gate=gate)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_coord.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_coord.npy"), r)
    held = {"z": out["z"]}
    for tag, start in (("A", 121000), ("B", 121200)):
        seeds = list(range(start, start + 200))
        for mode in ("cand", "frozen", "parent"):
            held[tag + "_" + mode] = pack(mode, seeds, H.NOM, 10.0)
            held[tag + "_" + mode]["wilson"] = Y.wilson(held[tag + "_" + mode]["succ"], 200)
            Y.show(tag + " " + mode, held[tag + "_" + mode])
        held[tag + "_pf"] = Y.pair(held[tag + "_cand"], held[tag + "_frozen"])
        held[tag + "_pp"] = Y.pair(held[tag + "_cand"], held[tag + "_parent"])
        print(tag, "frozen", held[tag + "_pf"]["net"], held[tag + "_pf"]["mcnemar_p"],
              "parent", held[tag + "_pp"]["net"], flush=True)
    s20 = list(range(121500, 121540))
    for mode in ("cand", "frozen", "parent"):
        held["long_" + mode] = pack(mode, s20, H.NOM, 20.0)
        Y.show("long " + mode, held["long_" + mode])
    held["long_pf"] = Y.pair(held["long_cand"], held["long_frozen"])
    bseeds = list(range(121600, 121640))
    for name, xml in (("nom", H.NOM), ("lo", H.LO), ("hi", H.HI)):
        for mode in ("cand", "frozen"):
            held["b_" + name + "_" + mode] = pack(mode, bseeds, xml, 10.0)
            Y.show("b " + name + " " + mode, held["b_" + name + "_" + mode])
        held["b_" + name + "_pair"] = Y.pair(held["b_" + name + "_cand"], held["b_" + name + "_frozen"])
        print("bound", name, held["b_" + name + "_pair"]["net"], held["b_" + name + "_pair"]["mcnemar_p"], flush=True)
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
    held["combined"] = dict(cand=ns, frozen=fs, parent=ps, cand_wilson=Y.wilson(ns, 400),
                            frozen_wilson=Y.wilson(fs, 400), parent_wilson=Y.wilson(ps, 400),
                            vs_frozen=net(fb), vs_parent=net(fp))
    print("COMBINED", held["combined"], flush=True)
    held["seconds"] = round(time.time() - t0, 1)
    json.dump(held, open(os.path.join(ROOT, "results", "head843_coord_held.json"), "w"), indent=1, default=float)
    print("wrote held", held["seconds"], flush=True)

if __name__ == "__main__":
    main()
