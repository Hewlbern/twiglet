"""Stance-ankle pitch feedback using only residual torque on the loaded foot.

Sign was identified on 79100-79111: u = -k * pitch lowered the pitch peak and
removed the two falls; u = +k * pitch did not. This file trains on 79200-79279.
A candidate is promising when the arm wave holds and either survival rises by
at least 3 walks, or survival does not fall and the fraction of time past 8°
of pitch is cut by half. Mean toe-off pitch is reported and is not the gate.

Held-out only for a promising candidate: 80000-80199 and 81000-81199, against
the frozen controller and arms-free walking. 20 s seeds 82000-82039 run only
if both held-outs survive more often than the matched frozen controller.

  python run_ankle.py
"""
import os, sys, json, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
_MODE = sys.argv[-1] if len(sys.argv) > 1 else ""
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
import run_balance as B
import run_recover as R
from simlib import params_path

TRAIN = (79200, 80)
HELD = ((80000, 200), (81000, 200))
LONG = (82000, 40)

def pose_ok(s):
    return ((s["shoulder_pp"] or 0) >= 14 and (s["head_yaw_pp"] or 0) >= 12
            and (s["shoulder_mean"] or 0) >= 18)

def tail(rows):
    gt8, gt10, mx, n = [], [], [], 0
    for r in rows:
        p = r.get("pitch_tail") or {}
        if p.get("frac_gt8") is None:
            continue
        gt8.append(p["frac_gt8"])
        gt10.append(p["frac_gt10"])
        mx.append(p["max_deg"])
        n += 1
    if not gt8:
        return dict(n=0)
    return dict(n=n, frac_gt8=float(np.mean(gt8)), frac_gt10=float(np.mean(gt10)),
                max_med=float(np.median(mx)), n_max_gt10=int(np.sum(np.array(mx) > 10)))

def joint_sat(rows, names):
    surv = [r for r in rows if r["fell"] is None and r.get("joints")]
    if not surv:
        return None
    vals = []
    for r in surv:
        vals.append(float(np.mean([r["joints"][n]["sat"] for n in names])))
    return float(np.mean(vals))

def ank_use(rows):
    stats = [r.get("ank_stats") for r in rows if r.get("ank_stats")]
    if not stats:
        return None
    return dict(frac_clamped=float(np.mean([s["frac_clamped"] for s in stats])),
                frac_no_residual=float(np.mean([s["frac_no_residual"] for s in stats])))

def yaw_dist(rows):
    ys = np.degrees([r["yaw_change"] for r in rows])
    return dict(n=int(len(ys)), median=float(np.median(ys)),
                p10=float(np.percentile(ys, 10)), p90=float(np.percentile(ys, 90)),
                min=float(ys.min()), max=float(ys.max()),
                frac_exceeding_15deg=float(np.mean(np.abs(ys) > 15)))

def fall_shape(rows):
    out = []
    for r in rows:
        if r["fell"] is None:
            continue
        out.append(dict(seed=r["seed"], t=r["fell"],
                        pitch=round(float(np.degrees(abs(r["pitch_end"]))), 1),
                        roll=round(float(np.degrees(abs(r["roll_end"]))), 1)))
    return out

def run(jobs):
    with mp.Pool(4) as pool:
        return pool.map(B.rollout, jobs, chunksize=2)

def score(name, start, n, head, T=10.0):
    rows = run(B.jobs(start, n, T=T, headarm=head, command_sign=-1.0 if head else 1.0, pitch_tail=True))
    s = B.summarize(rows)
    s["name"] = name
    s["pitch_tail"] = tail(rows)
    s["ankle_sat"] = joint_sat(rows, ("left_ankle", "right_ankle"))
    s["hip_pitch_sat"] = joint_sat(rows, ("left_hip_pitch", "right_hip_pitch"))
    s["ank_use"] = ank_use(rows)
    s["yaw_dist"] = yaw_dist(rows)
    s["fall_shape"] = fall_shape(rows)
    B.show(name, s)
    pt = s["pitch_tail"]
    print("  gt8", None if pt.get("frac_gt8") is None else round(pt["frac_gt8"], 4),
          "gt10", None if pt.get("frac_gt10") is None else round(pt["frac_gt10"], 4),
          "n>10", pt.get("n_max_gt10"),
          "ankSat", None if s["ankle_sat"] is None else round(100 * s["ankle_sat"], 2),
          "hipSat", None if s["hip_pitch_sat"] is None else round(100 * s["hip_pitch_sat"], 2),
          "use", s["ank_use"],
          "yaw15", round(s["yaw_dist"]["frac_exceeding_15deg"], 3), flush=True)
    return s

def slim(s):
    d = {k: v for k, v in s.items() if k != "fell"}
    d["fell_n"] = len(s.get("fell") or [])
    d["fell"] = s.get("fell") or []
    return d

def promising(s, base):
    if not pose_ok(s):
        return False
    if s["ankle_sat"] is not None and base["ankle_sat"] is not None and s["ankle_sat"] > base["ankle_sat"] + 0.02:
        return False
    if s["succ"] >= base["succ"] + 3:
        return True
    tail_base = base["pitch_tail"].get("frac_gt8") or 0.0
    tail_s = s["pitch_tail"].get("frac_gt8") or 0.0
    tail10 = (s["pitch_tail"].get("frac_gt10") or 0.0) <= (base["pitch_tail"].get("frac_gt10") or 0.0)
    if s["succ"] >= base["succ"] and tail_base > 0 and tail_s <= 0.5 * tail_base and tail10:
        return True
    return False

def main():
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6:
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 6), flush=True)
    cur = R.base(name="current")
    def ank(**kw):
        sp = R.base(name="ank", ank_sign=-1.0, ank_lim=0.05)
        sp.update(kw)
        return sp
    specs = [
        ("current", cur),
        ("ank25", ank(name="ank25", k_stance_ank=0.25)),
        ("ank40", ank(name="ank40", k_stance_ank=0.40)),
        ("ank40d", ank(name="ank40d", k_stance_ank=0.40, d_stance_ank=0.05)),
        ("ank_i", ank(name="ank_i", k_stance_ank=0.30, i_stance_ank=0.12)),
        ("pre_toe", R.base(name="pre_toe", pre_toe=True)),
        ("ank_pre", ank(name="ank_pre", k_stance_ank=0.40, pre_toe=True)),
    ]
    table = [score("train " + n, TRAIN[0], TRAIN[1], h) for n, h in specs]
    base = table[0]
    kept = [s for s in table[1:] if promising(s, base)]
    winner = None
    if kept:
        winner = max(kept, key=lambda s: (s["succ"], -(s["pitch_tail"].get("frac_gt10") or 0), s["progress_all"] or 0))
    print("CHOSEN", None if winner is None else winner["name"], flush=True)
    rep = dict(
        identity_dx=float(b["dx"]),
        sign_id="79100-79111, u=-0.40*pitch saved both falls and cut time past 8 deg; u=+0.40*pitch did not. Constant ±0.04 rad bias on 79000-79011 raised the pitch peak both ways.",
        train_seeds=list(TRAIN),
        rule="arm wave held; ankle stall not up by more than 2 points; promising if +3 survivals, or survival not worse and time past 8 deg of pitch cut by half. Mean toe-off pitch is not the gate.",
        train=[slim(s) for s in table],
        chosen=None if winner is None else winner["name"].replace("train ", ""),
    )
    if winner is not None:
        key = winner["name"].replace("train ", "")
        head = next(h for n, h in specs if n == key)
        for tag, start, n in (("heldA", HELD[0][0], HELD[0][1]), ("heldB", HELD[1][0], HELD[1][1])):
            rep[tag + "_winner"] = slim(score(tag + " " + key, start, n, head))
            rep[tag + "_current"] = slim(score(tag + " current", start, n, cur))
            rep[tag + "_walk"] = slim(score(tag + " walk", start, n, None))
        if (rep["heldA_winner"]["succ"] > rep["heldA_current"]["succ"]
                and rep["heldB_winner"]["succ"] > rep["heldB_current"]["succ"]
                and pose_ok(rep["heldA_winner"]) and pose_ok(rep["heldB_winner"])):
            rep["long_winner"] = slim(score("long " + key, LONG[0], LONG[1], head, T=20.0))
            rep["long_current"] = slim(score("long current", LONG[0], LONG[1], cur, T=20.0))
            rep["long_seeds"] = list(LONG)
    rep["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(ROOT, "results", "ankle.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, rep["seconds"], flush=True)

def deadzone_main():
    """Same restoring sign, command only outside the ordinary pitch band.

    79300-79379 is the selection block unless current falls fewer than 4 times,
    in which case 79400-79479 is used and both current scores are kept.
    """
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6:
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 6), flush=True)
    cur = R.base(name="current")
    def ank(**kw):
        sp = R.base(name="dz", ank_sign=-1.0, ank_lim=0.05, k_stance_ank=0.40)
        sp.update(kw)
        return sp
    specs = [
        ("current", cur),
        ("dz4", ank(name="dz4", ank_deadzone=0.070)),
        ("dz6", ank(name="dz6", ank_deadzone=0.105)),
    ]
    tables = []
    for start in (79300, 79400):
        table = [score("dz %d %s" % (start, n), start, 80, h) for n, h in specs]
        tables.append(table)
        if table[0]["n"] - table[0]["succ"] >= 4:
            break
    select = tables[-1]
    base = select[0]
    kept = [s for s in select[1:] if promising(s, base)]
    winner = max(kept, key=lambda s: (s["succ"], -(s["pitch_tail"].get("frac_gt10") or 0))) if kept else None
    print("DZ", None if winner is None else winner["name"], flush=True)
    rep = dict(identity_dx=float(b["dx"]),
               blocks=[[slim(s) for s in table] for table in tables],
               chosen=None if winner is None else winner["name"],
               rule="same reliability rule as the proportional train; deadzone 4 deg and 6 deg")
    if winner is not None:
        key = winner["name"].split()[-1]
        head = next(h for n, h in specs if n == key)
        for tag, start in (("heldA", 80000), ("heldB", 81000)):
            rep[tag + "_winner"] = slim(score(tag + " " + key, start, 200, head))
            rep[tag + "_current"] = slim(score(tag + " current", start, 200, cur))
            rep[tag + "_walk"] = slim(score(tag + " walk", start, 200, None))
        if (rep["heldA_winner"]["succ"] > rep["heldA_current"]["succ"]
                and rep["heldB_winner"]["succ"] > rep["heldB_current"]["succ"]
                and pose_ok(rep["heldA_winner"]) and pose_ok(rep["heldB_winner"])):
            rep["long_winner"] = slim(score("long " + key, 82000, 40, head, T=20.0))
            rep["long_current"] = slim(score("long current", 82000, 40, cur, T=20.0))
    rep["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(ROOT, "results", "ankle_dz.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, rep["seconds"], flush=True)

if __name__ == "__main__":
    if _MODE == "dz":
        deadzone_main()
    else:
        main()
