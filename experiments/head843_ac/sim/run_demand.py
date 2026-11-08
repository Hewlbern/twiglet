"""Lower step demand, or the same placement started before toe-off.

Train 75000-75079. A candidate is frozen only if, on that block, it keeps the
arm wave, survives at least 4 more walks than the current controller, lowers
the median absolute pitch at toe-off by at least 1 deg, and lowers either
hip-pitch stall or placement-clip occupancy. Speed is reported and is not a gate.

Held-out, only after that gate: 76000-76199 and 77000-77199, against the current
controller and arms-free walking. A 20 s block is 78000-78039 and runs only if
both held-outs beat the matched current survival.

  python run_demand.py
"""
import os, sys, json, math, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
import run_balance as B
import run_recover as R
from simlib import params_path

TRAIN = (75000, 80)
HELD = ((76000, 200), (77000, 200))
LONG = (78000, 40)

def pose_ok(s):
    return ((s["shoulder_pp"] or 0) >= 14 and (s["head_yaw_pp"] or 0) >= 12
            and (s["shoulder_mean"] or 0) >= 18)

def margin_of(rows):
    pitch = []
    n = clip = 0
    for r in rows:
        m = r.get("margin") or {}
        pitch.extend(m.get("pitch") or [])
        n += int(m.get("n") or 0)
        clip += int(m.get("clip") or 0)
    if not pitch:
        return dict(n_swing=0)
    p = np.degrees(np.array(pitch))
    return dict(
        n_swing=int(len(p)),
        pitch_med=float(np.median(p)),
        pitch_p90=float(np.percentile(p, 90)),
        frac_pitch_gt_8=float(np.mean(p > 8.0)),
        clip_frac=float(clip / n) if n else None,
    )

def hip_sat(rows):
    surv = [r for r in rows if r["fell"] is None and r.get("joints")]
    if not surv:
        return None
    vals = [0.5 * (r["joints"]["left_hip_pitch"]["sat"] + r["joints"]["right_hip_pitch"]["sat"]) for r in surv]
    return float(np.mean(vals))

def yaw_dist(rows):
    ys = np.degrees([r["yaw_change"] for r in rows])
    return dict(n=int(len(ys)), median=float(np.median(ys)),
                p10=float(np.percentile(ys, 10)), p90=float(np.percentile(ys, 90)),
                min=float(ys.min()), max=float(ys.max()),
                frac_exceeding_15deg=float(np.mean(np.abs(ys) > 15)))

def run(jobs):
    with mp.Pool(4) as pool:
        return pool.map(B.rollout, jobs, chunksize=2)

def score(name, start, n, head, demand=None, T=10.0):
    jobs = B.jobs(start, n, T=T, headarm=head, command_sign=-1.0 if head else 1.0, margin=True)
    if demand is not None:
        for j in jobs:
            j["demand"] = demand
    rows = run(jobs)
    s = B.summarize(rows)
    s["name"] = name
    s["margin"] = margin_of(rows)
    s["hip_pitch_sat"] = hip_sat(rows)
    s["yaw_dist"] = yaw_dist(rows)
    B.show(name, s)
    m = s["margin"]
    print("  pitchMed", None if m.get("pitch_med") is None else round(m["pitch_med"], 2),
          "gt8", None if m.get("frac_pitch_gt_8") is None else round(m["frac_pitch_gt_8"], 3),
          "clip", None if m.get("clip_frac") is None else round(m["clip_frac"], 3),
          "hipSat", None if s["hip_pitch_sat"] is None else round(100 * s["hip_pitch_sat"], 2),
          "yaw15", round(s["yaw_dist"]["frac_exceeding_15deg"], 3), flush=True)
    return s

def slim(s):
    d = {k: v for k, v in s.items() if k != "fell"}
    d["fell_n"] = len(s.get("fell") or [])
    d["fell"] = s.get("fell") or []
    return d

def main():
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6 or bool(a["fell"]) != (b["fell"] is not None):
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 6), flush=True)
    cur = R.base(name="current")
    specs = [
        ("current", cur, None),
        ("demand90", cur, 0.90),
        ("demand80", cur, 0.80),
        ("pre_toe", R.base(name="pre_toe", pre_toe=True), None),
    ]
    table = []
    for name, head, demand in specs:
        table.append(score("train " + name, TRAIN[0], TRAIN[1], head, demand))
    base = table[0]
    kept = []
    for s in table[1:]:
        if not pose_ok(s):
            continue
        if s["succ"] < base["succ"] + 4:
            continue
        if s["margin"].get("pitch_med") is None or base["margin"].get("pitch_med") is None:
            continue
        pitch_drop = base["margin"]["pitch_med"] - s["margin"]["pitch_med"]
        sat_drop = (base["hip_pitch_sat"] or 0) - (s["hip_pitch_sat"] or 0)
        clip_drop = (base["margin"].get("clip_frac") or 0) - (s["margin"].get("clip_frac") or 0)
        if pitch_drop < 1.0:
            continue
        if sat_drop < 0.005 and clip_drop < 0.01:
            continue
        if clip_drop < -0.005:
            continue
        kept.append(s)
    winner = None
    if kept:
        winner = max(kept, key=lambda s: (s["succ"], s["progress_all"] or 0))
    print("CHOSEN", None if winner is None else winner["name"], flush=True)
    rep = dict(
        identity_dx=float(b["dx"]),
        train_seeds=list(TRAIN),
        rule="pose gates; +4/80 survival; toe-off |pitch| median down >= 1 deg; hip-pitch stall down >= 0.5 pp or placement-clip down >= 1 pp; clip not worse by 0.5 pp. Speed is not a gate.",
        pitch_first="coordinated-wave falls on 58000, 59000, and 68000 reached 10 deg of pitch before 10 deg of roll. This pass does not add lateral offsets.",
        train=[slim(s) for s in table],
        chosen=None if winner is None else winner["name"].replace("train ", ""),
    )
    if winner is not None:
        key = winner["name"].replace("train ", "")
        head, demand = next((h, d) for n, h, d in specs if n == key)
        wave_free = None
        for tag, start, n in (("heldA", HELD[0][0], HELD[0][1]), ("heldB", HELD[1][0], HELD[1][1])):
            rep[tag + "_winner"] = slim(score(tag + " " + key, start, n, head, demand))
            rep[tag + "_current"] = slim(score(tag + " current", start, n, cur, None))
            rep[tag + "_walk"] = slim(score(tag + " walk", start, n, None, None))
        wA, wB = rep["heldA_winner"], rep["heldB_winner"]
        cA, cB = rep["heldA_current"], rep["heldB_current"]
        if (wA["succ"] > cA["succ"] and wB["succ"] > cB["succ"] and pose_ok(wA) and pose_ok(wB)):
            rep["long_winner"] = slim(score("long " + key, LONG[0], LONG[1], head, demand, T=20.0))
            rep["long_current"] = slim(score("long current", LONG[0], LONG[1], cur, None, T=20.0))
            rep["long_seeds"] = list(LONG)
    rep["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(ROOT, "results", "demand.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, rep["seconds"], flush=True)

if __name__ == "__main__":
    main()
