"""Earlier pitch-rate response on the frozen short-step trim.

The 0.06 rad cap stays. The frozen gains stay. The new branch turns the same
hip geometry on before -5 deg, and only when pitch rate is already backward.
rate_on is absent on the frozen checkpoint, so that file is unchanged.
Train seeds start at 200200. Selection starts at 201000. A 400-seed screen
starts at 202000 only if the selection gate passes. No 4000 in this script.
"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_traj as T
import run_head843_shortbal_val as V

KEYS = ["early_on", "rate_on", "k_rate_early"]
LO = np.array([0.025, 0.12, 0.0])
HI = np.array([0.060, 0.35, 0.60])
MU = np.array([0.040, 0.18, 0.25])
SIG = np.array([0.008, 0.05, 0.12])

def jobs(mode, early, seeds, xml, Ts):
    gait, base, ztraj, zsb = V.load_models()
    js = V.B.jobs("cand", zsb, base, gait, ztraj, seeds, xml, Ts)
    if mode == "early":
        for j in js:
            sb = j["headarm"]["short_balance"]
            sb["early_on"] = float(early[0])
            sb["rate_on"] = float(early[1])
            sb["k_rate_early"] = float(early[2])
    return js

def metric(rows):
    s = T.enrich(rows)
    mins = [(r.get("pitch_tail") or {}).get("min_deg") for r in rows]
    mins = [m for m in mins if m is not None]
    s["min_pitch"] = float(np.mean(mins)) if mins else 0.0
    s["p10_min"] = float(np.percentile(mins, 10)) if mins else 0.0
    s["back"] = float(np.mean([max(0.0, -3.0 - m) for m in mins])) if mins else 0.0
    s["part"] = s["progress"] - 6.0 * (1.0 - s["succ"] / s["n"]) - 0.45 * s["frac15"] - 0.06 * s["back"]
    if s["progress"] < 0.10:
        s["part"] -= 3.0
    if s["shoulder_mean"] is not None and (s["shoulder_mean"] < 18 or (s["shoulder_pp"] or 0) < 16 or (s["head_yaw_pp"] or 0) < 14):
        s["part"] -= 3.0
    return s

def runm(mode, early, seeds, xml, Ts):
    return metric(V.Y.run_jobs(jobs(mode, early, seeds, xml, Ts)))

def main():
    t0 = time.time()
    gait, base, ztraj, zsb = V.load_models()
    # Frozen law, diagnostic seed. The logger and the dormant early branch must not move it.
    prev = next(r for r in json.load(open(os.path.join(ROOT, "results", "head843_shortbal_low4000.json")))["rows"] if r["seed"] == 190007)
    chk = V.Y.run_jobs(jobs("base", MU, [190007], V.H.LO, 10.0))[0]
    print("frozen check", chk["fell"], prev["fell"], flush=True)
    if abs((chk["fell"] or -1) - (prev["fell"] or -2)) > 1e-6:
        raise SystemExit("frozen law moved")
    rng = np.random.default_rng(31)
    mu, sig = MU.copy(), SIG.copy()
    log = []
    for gen in range(4):
        low = list(range(200200 + gen * 8, 200200 + gen * 8 + 8))
        nom = list(range(200400 + gen * 4, 200400 + gen * 4 + 4))
        lng = list(range(200500 + gen * 2, 200500 + gen * 2 + 2))
        hev = list(range(200600 + gen * 2, 200600 + gen * 2 + 2))
        Z = np.minimum(HI, np.maximum(LO, mu + sig * rng.standard_normal((6, 3))))
        Z[0] = np.minimum(HI, np.maximum(LO, mu))
        packed, owners = [], []
        for i in range(6):
            for seeds, xml, Ts in ((low, V.H.LO, 10.0), (nom, V.H.NOM, 10.0), (lng, V.H.NOM, 20.0), (hev, V.H.HI, 10.0)):
                packed += jobs("early", Z[i], seeds, xml, Ts)
                owners += [i] * len(seeds)
        rows = V.Y.run_jobs(packed)
        buckets = [[] for _ in range(6)]
        for o, row in zip(owners, rows):
            buckets[o].append(row)
        # Score low and nominal pieces separately by splitting each bucket in order.
        stats = []
        for b in buckets:
            # 8 low, 4 nom, 2 long, 2 heavy
            parts = [metric(b[:8]), metric(b[8:12]), metric(b[12:14]), metric(b[14:])]
            score = 1.6 * parts[0]["part"] + parts[1]["part"] + 0.7 * parts[2]["part"] + 0.6 * parts[3]["part"]
            stats.append((score, parts))
        order = sorted(range(6), key=lambda i: stats[i][0], reverse=True)
        mu = Z[order[:3]].mean(0)
        sig = np.maximum(Z[order[:3]].std(0), 0.4 * SIG)
        best = stats[order[0]]
        rec = dict(gen=gen, score=best[0], low_succ=int(best[1][0]["succ"]), low_n=int(best[1][0]["n"]),
                   low_min=best[1][0]["min_pitch"], nom_succ=int(best[1][1]["succ"]),
                   z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", gen, "low", f"{rec['low_succ']}/{rec['low_n']}", "min", round(rec["low_min"], 2),
              "nom", rec["nom_succ"], "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_earlyrate_ckpt.json"), "w"), indent=1)
    early = np.array([log[-1]["z"][k] for k in KEYS], float)
    plan = (
        ("lo", list(range(201000, 201200)), V.H.LO, 10.0),
        ("nom", list(range(201200, 201320)), V.H.NOM, 10.0),
        ("n20", list(range(201400, 201432)), V.H.NOM, 20.0),
        ("hi", list(range(201500, 201524)), V.H.HI, 10.0),
    )
    blocks = {}
    for name, seeds, xml, Ts in plan:
        for mode in ("early", "base"):
            blocks[name + "_" + mode] = runm(mode, early, seeds, xml, Ts)
            s = blocks[name + "_" + mode]
            print(name, mode, f"{s['succ']}/{s['n']}", "prog", round(s["progress"], 3),
                  "y15", round(s["frac15"], 3), "p10", round(s["p10_min"], 2),
                  "min", round(s["min_pitch"], 2), flush=True)
    c, b = blocks["lo_early"], blocks["lo_base"]
    cn, bn = blocks["nom_early"], blocks["nom_base"]
    c20, b20 = blocks["n20_early"], blocks["n20_base"]
    ch, bh = blocks["hi_early"], blocks["hi_base"]
    low_better = (c["succ"] >= b["succ"] and c["p10_min"] >= b["p10_min"] + 0.5) or (c["succ"] >= b["succ"] + 1)
    nom_ok = cn["succ"] >= bn["succ"] and cn["progress"] >= 0.10 and cn["frac15"] <= bn["frac15"] + 0.02
    amp_ok = (cn["shoulder_mean"] or 0) >= 18 and (cn["shoulder_pp"] or 0) >= 16 and (cn["head_yaw_pp"] or 0) >= 14
    long_ok = c20["succ"] >= b20["succ"] and c20["progress"] >= 0.10 and c20["frac15"] <= b20["frac15"] + 0.05
    heavy_ok = ch["succ"] >= bh["succ"]
    gate = bool(low_better and nom_ok and amp_ok and long_ok and heavy_ok)
    print("GATE", gate, "low_better", low_better, "nom", nom_ok, "amp", amp_ok, "long", long_ok, "heavy", heavy_ok, flush=True)
    out = dict(seconds=round(time.time() - t0, 1), generations=log,
               z={k: float(v) for k, v in zip(KEYS, early)},
               frozen_npy="params/head843_shortbal.npy",
               selection=blocks, gate=gate,
               gate_rule="Low tail improves by 0.5 deg at the 10th percentile of min pitch with no extra falls, or at least one fewer fall. Nominal adds no falls, progress stays a walk, heading fraction within 0.02. 20 s heading within 0.05 and no extra falls. Heavy adds no falls.")
    json.dump(out, open(os.path.join(ROOT, "results", "head843_earlyrate.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed", flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_earlyrate.npy"), early)
    screen = {}
    for name, seeds, xml, Ts in (
        ("lo", list(range(202000, 202400)), V.H.LO, 10.0),
        ("nom", list(range(202400, 202800)), V.H.NOM, 10.0),
        ("n20", list(range(202800, 202832)), V.H.NOM, 20.0),
        ("hi", list(range(202900, 202924)), V.H.HI, 10.0),
    ):
        for mode in ("early", "base"):
            screen[name + "_" + mode] = runm(mode, early, seeds, xml, Ts)
            s = screen[name + "_" + mode]
            print("screen", name, mode, f"{s['succ']}/{s['n']}", "prog", round(s["progress"], 3),
                  "y15", round(s["frac15"], 3), "p10", round(s["p10_min"], 2), flush=True)
    screen["hold"] = bool(
        screen["lo_early"]["succ"] >= screen["lo_base"]["succ"]
        and screen["nom_early"]["succ"] >= screen["nom_base"]["succ"]
        and screen["nom_early"]["progress"] >= 0.10
        and screen["n20_early"]["frac15"] <= screen["n20_base"]["frac15"] + 0.05
        and screen["lo_early"]["p10_min"] >= screen["lo_base"]["p10_min"] - 0.2
    )
    print("SCREEN hold", screen["hold"], flush=True)
    json.dump(screen, open(os.path.join(ROOT, "results", "head843_earlyrate_screen.json"), "w"), indent=1, default=float)
    print("done", round(time.time() - t0, 1), flush=True)

if __name__ == "__main__":
    main()
