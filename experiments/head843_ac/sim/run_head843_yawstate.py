"""State-gated stance-yaw plus a local timing search. Does not overwrite prior npy files.

The correction stays on the loaded foot and scales with heading error. Authority
fades as |roll| grows and drops to zero when roll is already leaving the upright
band. Swing-foot yaw is not used: a constant swing offset reversed heading on
the 106100 probe. sway_ph, k_lat, k_roll_extra, and k_place move only inside a
tight box around the frozen searched gait.

Train seeds start at 107000. Selection seeds start at 107200. Held-out seeds
start at 108000 and run only if the selection gate passes. Those held-outs are
not an input to the search.
"""
import os, sys, json, time, math
from math import comb
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_search as S
import run_head843_heading as H

KEYS = ["k", "roll_fade", "roll_hold", "lim", "sway_ph", "k_lat", "k_roll_extra", "k_place"]

def bounds(search):
    sp = float(search["searched_gait"]["sway_ph"])
    kl = float(search["searched_ctrl"]["k_lat"])
    kr = float(search["searched_ctrl"]["k_roll_extra"])
    kp = float(search["searched_ctrl"]["k_place"])
    lo = np.array([-0.40, 0.08, 0.05, 0.015, sp - 0.18, max(0.0, kl - 0.15), max(0.0, kr - 0.10), max(0.0, kp - 0.12)])
    hi = np.array([-0.02, 0.28, 0.16, 0.040, sp + 0.18, min(0.80, kl + 0.15), min(0.60, kr + 0.10), min(1.00, kp + 0.12)])
    mu = np.array([-0.20, 0.12, 0.08, 0.035, sp, kl, kr, kp])
    sig = np.array([0.05, 0.03, 0.02, 0.005, 0.04, 0.035, 0.025, 0.03])
    return lo, hi, mu, sig

def clip(z, lo, hi):
    return np.minimum(hi, np.maximum(lo, z))

def apply_z(z, base_ctrl, gait):
    ctrl = np.array(base_ctrl, float).copy()
    g = np.array(gait, float).copy()
    # CTRL_KEYS: body_lean, k_place, k_hip, k_lat, k_roll_extra, k_yaw_phase, ank_arm
    ctrl[1] = float(z[7])
    ctrl[3] = float(z[5])
    ctrl[4] = float(z[6])
    g[4] = float(z[4])  # sway_ph
    sp = S.spec_from(ctrl)
    sp["k_support_yaw"] = 0.0
    sp["yaw_add"] = dict(
        from_error=True, k=float(z[0]), lim=float(z[3]), where="stance",
        roll_fade=float(z[1]), hold_upright=True, roll_hold=float(z[2]),
        w_stance=1.0, w_swing=0.0,
    )
    return g, sp

def jobs(z, base_ctrl, gait, seeds, xml, T, use_law):
    if use_law:
        g, sp = apply_z(z, base_ctrl, gait)
    else:
        g = np.array(gait, float)
        sp = S.spec_from(base_ctrl)
        sp["k_support_yaw"] = 0.0
    return [dict(x=[float(v) for v in g], seed=int(s), rand=True, T=T, headarm=sp,
                 command_sign=-1.0, measure_path=True, pitch_tail=True, trunk_stats=True,
                 xml=xml) for s in seeds]

def run_jobs(js):
    return S.run_jobs(js)

def fit(rows):
    s = S.summarize(rows)
    ys = np.degrees([r["yaw_change"] for r in rows])
    s["yaw_dist"] = dict(median=float(np.median(ys)), p10=float(np.percentile(ys, 10)),
                         p90=float(np.percentile(ys, 90)), min=float(ys.min()), max=float(ys.max()))
    rolls = [r.get("trunk", {}).get("frac_roll8") for r in rows if r.get("trunk")]
    heights = [r.get("trunk", {}).get("height_min") for r in rows if r.get("trunk")]
    s["frac_roll8"] = float(np.mean(rolls)) if rolls else 0.0
    s["height_min"] = float(np.median(heights)) if heights else None
    pen = 0.0
    if s["progress"] < 0.10:
        pen += 5.0
    if s["shoulder_mean"] is not None and (s["shoulder_mean"] < 18 or (s["shoulder_pp"] or 0) < 16 or (s["head_yaw_pp"] or 0) < 14):
        pen += 3.0
    s["score"] = s["progress"] - 0.70 * s["frac15"] - 3.5 * (1.0 - s["succ"] / s["n"]) - 0.40 * s["frac_roll8"] - pen
    anks, hips, mains = [], [], []
    for r in rows:
        ld, j = r.get("load") or {}, r.get("joints") or {}
        if ld:
            mains.append(ld.get("main_sat"))
        for n in ("left_ankle", "right_ankle"):
            if n in j:
                anks.append(j[n]["sat"])
        for n in ("left_hip_pitch", "right_hip_pitch"):
            if n in j:
                hips.append(j[n]["sat"])
    s["stall"] = dict(ankle=None if not anks else float(np.mean(anks)),
                      hip_pitch=None if not hips else float(np.mean(hips)),
                      main=None if not mains else float(np.mean(mains)))
    return s

def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ph, c - h, c + h]

def pair(a, b):
    fa, fb = set(a["fell"]), set(b["fell"])
    saved, cost, both = sorted(fb - fa), sorted(fa - fb), sorted(fa & fb)
    n = len(saved) + len(cost)
    if n == 0:
        p = 1.0
    else:
        k = min(len(saved), len(cost))
        p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    return dict(saved=saved, cost=cost, both=both, net=len(saved) - len(cost), n_disc=n, mcnemar_p=p)

def show(name, s):
    print(name, f"{s['succ']}/{s['n']}", "prog", round(s["progress"], 3),
          "y15", round(s["frac15"], 3), "ymed", round(s["yaw_dist"]["median"], 1),
          "p10", round(s["yaw_dist"]["p10"], 1), "p90", round(s["yaw_dist"]["p90"], 1),
          "r8", round(s.get("frac_roll8") or 0, 3),
          "sh", None if s["shoulder_mean"] is None else round(s["shoulder_mean"], 2),
          "pp", None if s["shoulder_pp"] is None else round(s["shoulder_pp"], 2),
          "hy", None if s["head_yaw_pp"] is None else round(s["head_yaw_pp"], 2),
          "falls", len(s["fell"]), flush=True)

def main():
    t0 = time.time()
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base_ctrl = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    lo, hi, mu, sig = bounds(search)
    rng = np.random.default_rng(21)
    log = []
    for g in range(5):
        nom = list(range(107000 + g * 4, 107000 + g * 4 + 4))
        heavy = list(range(107040 + g * 2, 107040 + g * 2 + 2))
        low = list(range(107060 + g * 2, 107060 + g * 2 + 2))
        Z = clip(mu + sig * rng.standard_normal((8, 8)), lo, hi)
        Z[0] = clip(mu, lo, hi)
        packed, owners = [], []
        for i in range(8):
            packed.extend(jobs(Z[i], base_ctrl, gait, nom, H.NOM, 20.0, True))
            packed.extend(jobs(Z[i], base_ctrl, gait, heavy, H.HI, 20.0, True))
            packed.extend(jobs(Z[i], base_ctrl, gait, low, H.LO, 20.0, True))
            owners.extend([i] * (len(nom) + len(heavy) + len(low)))
        rows = run_jobs(packed)
        buckets = [[] for _ in range(8)]
        for o, r in zip(owners, rows):
            buckets[o].append(r)
        stats = [fit(b) for b in buckets]
        order = sorted(range(8), key=lambda i: stats[i]["score"], reverse=True)
        keep = order[:3]
        mu = Z[keep].mean(0)
        sig = np.maximum(Z[keep].std(0), 0.35 * sig)
        best = stats[order[0]]
        rec = dict(gen=g, seeds_nominal=nom, seeds_heavy=heavy, seeds_low=low,
                   best={k: best[k] for k in ("succ", "n", "progress", "frac15", "score", "shoulder_mean", "shoulder_pp", "head_yaw_pp", "frac_roll8")},
                   z={k: round(float(v), 5) for k, v in zip(KEYS, Z[order[0]])})
        log.append(rec)
        print("gen", g, f"{best['succ']}/{best['n']}", "prog", round(best["progress"], 3),
              "y15", round(best["frac15"], 3), "score", round(best["score"], 3), "z", rec["z"], flush=True)
        json.dump(log, open(os.path.join(ROOT, "results", "head843_yawstate_ckpt.json"), "w"), indent=1)
    z_best = np.array([log[-1]["z"][k] for k in KEYS], float)
    # Selection. Not the train seeds, and not a held-out.
    sel20 = list(range(107200, 107232))
    sel10 = list(range(107300, 107332))
    selb = list(range(107400, 107416))
    new20 = fit(run_jobs(jobs(z_best, base_ctrl, gait, sel20, H.NOM, 20.0, True)))
    base20 = fit(run_jobs(jobs(z_best, base_ctrl, gait, sel20, H.NOM, 20.0, False)))
    new10 = fit(run_jobs(jobs(z_best, base_ctrl, gait, sel10, H.NOM, 10.0, True)))
    base10 = fit(run_jobs(jobs(z_best, base_ctrl, gait, sel10, H.NOM, 10.0, False)))
    new_hi = fit(run_jobs(jobs(z_best, base_ctrl, gait, selb, H.HI, 10.0, True)))
    base_hi = fit(run_jobs(jobs(z_best, base_ctrl, gait, selb, H.HI, 10.0, False)))
    new_lo = fit(run_jobs(jobs(z_best, base_ctrl, gait, selb, H.LO, 10.0, True)))
    base_lo = fit(run_jobs(jobs(z_best, base_ctrl, gait, selb, H.LO, 10.0, False)))
    for nm, s in (("sel20 new", new20), ("sel20 base", base20), ("sel10 new", new10), ("sel10 base", base10),
                  ("sel hi", new_hi), ("sel hi base", base_hi), ("sel lo", new_lo), ("sel lo base", base_lo)):
        show(nm, s)
    gate = (
        new20["frac15"] <= base20["frac15"] - 0.15
        and new20["succ"] >= base20["succ"] - 1
        and new20["progress"] >= 0.10
        and new20["progress"] >= base20["progress"] - 0.015
        and new10["succ"] >= base10["succ"] - 1
        and (new_hi["succ"] + new_lo["succ"]) >= (base_hi["succ"] + base_lo["succ"]) - 2
        and (new20["shoulder_mean"] or 0) >= 18
        and (new20["head_yaw_pp"] or 0) >= 14
        and (new20["shoulder_pp"] or 0) >= 16
    )
    print("GATE", gate, flush=True)
    out = dict(seconds_train=round(time.time() - t0, 1), generations=log,
               z_best={k: float(v) for k, v in zip(KEYS, z_best)},
               selection=dict(new20=new20, base20=base20, new10=new10, base10=base10,
                              new_hi=new_hi, base_hi=base_hi, new_lo=new_lo, base_lo=base_lo),
               gate=gate)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_yawstate.json"), "w"), indent=1, default=float)
    if not gate:
        print("selection gate closed; no held-out", flush=True)
        return
    np.save(os.path.join(ROOT, "params", "head843_yawstate.npy"), z_best)
    held = {"z": out["z_best"]}
    for tag, start in (("A", 108000), ("B", 108200)):
        seeds = list(range(start, start + 200))
        held[tag + "_new"] = fit(run_jobs(jobs(z_best, base_ctrl, gait, seeds, H.NOM, 10.0, True)))
        held[tag + "_base"] = fit(run_jobs(jobs(z_best, base_ctrl, gait, seeds, H.NOM, 10.0, False)))
        held[tag + "_new"]["wilson"] = wilson(held[tag + "_new"]["succ"], 200)
        held[tag + "_base"]["wilson"] = wilson(held[tag + "_base"]["succ"], 200)
        held[tag + "_pair"] = pair(held[tag + "_new"], held[tag + "_base"])
        show(tag + " new", held[tag + "_new"])
        show(tag + " base", held[tag + "_base"])
        print(tag, "pair", held[tag + "_pair"]["net"], held[tag + "_pair"]["mcnemar_p"], flush=True)
    seeds20 = list(range(108500, 108540))
    held["long_new"] = fit(run_jobs(jobs(z_best, base_ctrl, gait, seeds20, H.NOM, 20.0, True)))
    held["long_base"] = fit(run_jobs(jobs(z_best, base_ctrl, gait, seeds20, H.NOM, 20.0, False)))
    # Reference only. support020 is not the control and is not promoted.
    z020 = np.array([-0.20, 0.02, search["searched_ctrl"]["k_yaw_phase"], search["searched_ctrl"]["ank_arm"]])
    js = H.jobs(z020, base_ctrl, gait, seeds20, H.NOM, 20.0)
    for j in js:
        j["trunk_stats"] = True
    held["long_support020"] = fit(run_jobs(js))
    held["long_pair"] = pair(held["long_new"], held["long_base"])
    show("long new", held["long_new"])
    show("long base", held["long_base"])
    show("long support020", held["long_support020"])
    bseeds = list(range(108600, 108640))
    for name, xml in (("nom", H.NOM), ("lo", H.LO), ("hi", H.HI)):
        held["bound_" + name] = fit(run_jobs(jobs(z_best, base_ctrl, gait, bseeds, xml, 10.0, True)))
        held["bound_base_" + name] = fit(run_jobs(jobs(z_best, base_ctrl, gait, bseeds, xml, 10.0, False)))
        held["bound_pair_" + name] = pair(held["bound_" + name], held["bound_base_" + name])
        show("bound " + name, held["bound_" + name])
        show("bound base " + name, held["bound_base_" + name])
        print("bound pair", name, held["bound_pair_" + name]["net"], held["bound_pair_" + name]["mcnemar_p"], flush=True)
    ns = held["A_new"]["succ"] + held["B_new"]["succ"]
    bs = held["A_base"]["succ"] + held["B_base"]["succ"]
    fa = set(held["A_new"]["fell"]) | set(held["B_new"]["fell"])
    fb = set(held["A_base"]["fell"]) | set(held["B_base"]["fell"])
    saved, cost = sorted(fb - fa), sorted(fa - fb)
    n = len(saved) + len(cost)
    k = min(len(saved), len(cost)) if n else 0
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    held["combined"] = dict(new=ns, base=bs, n=400, new_wilson=wilson(ns, 400), base_wilson=wilson(bs, 400),
                            saved=len(saved), cost=len(cost), net=len(saved) - len(cost), mcnemar_p=p,
                            saved_seeds=saved, cost_seeds=cost)
    print("COMBINED", ns, bs, "net", len(saved) - len(cost), "p", p, flush=True)
    held["seconds"] = round(time.time() - t0, 1)
    json.dump(held, open(os.path.join(ROOT, "results", "head843_yawstate_held.json"), "w"), indent=1, default=float)
    print("wrote held", held["seconds"], flush=True)

if __name__ == "__main__":
    main()
