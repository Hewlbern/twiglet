"""Stance-leg and swing-foot balance for the arms-forward pose.

The arm wave is fixed: shoulder mean command 22 deg, swing ±10 deg, head yaw ±8 deg,
phase 1.2 rad. No-overlay walking is not modified. Train 50000-50063.
Held-out 47000-47199 is scored only after the choice. Flat check is 50200-50399.

  python run_balance.py
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
from manoeuvre import rollout
from simlib import params_path

TRAIN = (50000, 64)
HELD = (47000, 200)
FLAT = (50200, 200)
LONG = (50400, 40)
PUSH = (50500, 40)

def arm(**kw):
    s = dict(kind="coord", name="arm", A_sh=10, A_el=5, Y_yaw=8, Y_pitch=1.5, Y_roll=1.5,
             k_imu=3.0, k_roll=0.25, sh0=22.0, el0=30.0, pitch0=-4.0, grip=18.0,
             t0=0.4, dur=1.4, scale_min=0.55, tilt0=0.06, arm_phase=1.2, head_phase=1.2,
             kp_sh=0.0, kp_head=0.0, body_lean=0.0, yaw_ff=0.0, balance=False,
             k_place=0.0, d_place=0.0, k_hip=0.0, d_hip=0.0, k_ank=0.0, d_ank=0.0,
             k_lat=0.0, d_lat=0.0)
    s.update(kw)
    return s

GRID = [
    arm(name="wave"),
    arm(name="lean02", body_lean=-0.02),
    arm(name="place", balance=True, k_place=0.9, d_place=0.08),
    arm(name="stance", balance=True, k_hip=-0.5, d_hip=-0.06),
    arm(name="combo", balance=True, body_lean=-0.02, k_place=0.6, d_place=0.05, k_hip=-0.25),
    arm(name="combo_lat", balance=True, body_lean=-0.02, k_place=0.6, d_place=0.05, k_hip=-0.25, k_lat=-0.4, d_lat=-0.05),
]
X = None

def jobs(start, n, T=10.0, **kw):
    base = dict(x=X, rand=True, T=T, measure_path=True)
    base.update(kw)
    return [dict(base, seed=start + i) for i in range(n)]

def run(js):
    with mp.Pool(4) as pool:
        return pool.map(rollout, js, chunksize=2)

def med(vals):
    vals = [v for v in vals if v is not None]
    return None if not vals else float(np.median(vals))

def summarize(rows):
    surv = [r for r in rows if r["fell"] is None]
    falls = [r for r in rows if r["fell"] is not None]
    long = [r for r in rows if r["fell"] is None or (r["fell"] or 0) >= 8.0]
    sh, hy, shm = [], [], []
    for r in surv:
        pp, mn = r.get("motion_pp_deg") or {}, r.get("motion_mean_deg") or {}
        if "shoulder_L" in pp:
            sh.append(0.5 * (pp["shoulder_L"] + pp["shoulder_R"]))
            shm.append(0.5 * (mn.get("shoulder_L", 0) + mn.get("shoulder_R", 0)))
        if "head_yaw" in pp:
            hy.append(pp["head_yaw"])
    def avg(key, src):
        v = [r.get(key) for r in src if isinstance(r.get(key), (int, float))]
        return None if not v else float(np.mean(v))
    return dict(
        succ=len(surv), n=len(rows), fell=[r["seed"] for r in falls],
        progress_all=float(np.mean([r["dx"] / r["T"] for r in rows])),
        speed_survivors=avg("speed", surv),
        path_survivors=avg("path_speed", surv),
        yaw_all=float(np.degrees(np.mean([r["yaw_change"] for r in rows]))),
        yaw_survivors=None if not surv else float(np.degrees(np.mean([r["yaw_change"] for r in surv]))),
        shoulder_pp=med(sh), shoulder_mean=med(shm), head_yaw_pp=med(hy),
        main_rms=None if not surv else float(np.mean([r["load"]["main_rms"] for r in surv])),
        main_sat=None if not surv else float(np.mean([r["load"]["main_sat"] for r in surv])),
        fall_t=med([r["fell"] for r in falls]),
        fall_roll=None if not falls else float(np.mean([abs(math.degrees(r["roll_end"])) for r in falls])),
        fall_pitch=None if not falls else float(np.mean([abs(math.degrees(r["pitch_end"])) for r in falls])),
        n_long=len(long),
    )

def show(name, s):
    print(name, f"{s['succ']}/{s['n']}",
          "prog", round(s["progress_all"], 3),
          "dxS", None if s["speed_survivors"] is None else round(s["speed_survivors"], 3),
          "path", None if s["path_survivors"] is None else round(s["path_survivors"], 3),
          "yawAll", round(s["yaw_all"], 1),
          "sh", None if s["shoulder_pp"] is None else round(s["shoulder_pp"], 1),
          "mean", None if s["shoulder_mean"] is None else round(s["shoulder_mean"], 1),
          "hy", None if s["head_yaw_pp"] is None else round(s["head_yaw_pp"], 1),
          "sat", None if s["main_sat"] is None else round(100 * s["main_sat"], 2),
          "rms", None if s["main_rms"] is None else round(s["main_rms"], 3),
          flush=True)

def eligible(r):
    return (r["shoulder_pp"] or 0) >= 14 and (r["head_yaw_pp"] or 0) >= 12 and (r["shoulder_mean"] or 0) >= 18 and abs(r["yaw_all"]) <= 12

def choose(table):
    kept = [r for r in table if eligible(r)]
    if not kept:
        return None
    best = max(r["succ"] for r in kept)
    near = [r for r in kept if r["succ"] >= best - 2]
    near.sort(key=lambda r: (-r["succ"], -(r["progress_all"] or 0), abs(r["yaw_all"])))
    return near[0]

def main():
    global X
    t0 = time.time()
    X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(X), 5000, True, 10.0))
    b = rollout(dict(x=X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6 or bool(a["fell"]) != (b["fell"] is not None):
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 4), flush=True)
    print("flat batch", flush=True)
    with mp.Pool(4) as pool:
        R = W.batch([np.array(X)] * FLAT[1], range(FLAT[0], FLAT[0] + FLAT[1]), True, pool, T=10.0)
    fell = [FLAT[0] + i for i, r in enumerate(R) if r["fell"]]
    spd = float(np.mean([r["dx"] / 10 for r in R if not r["fell"]] or [0]))
    print("flat", FLAT[1] - len(fell), spd, fell[:8], flush=True)
    if FLAT[1] - len(fell) < 199:
        raise SystemExit("flat regression")
    table = []
    for sp in GRID:
        s = summarize(run(jobs(*TRAIN, headarm=sp)))
        s["name"] = sp["name"]
        table.append(s)
        show("train " + sp["name"], s)
    winner = choose(table)
    print("CHOSEN", None if winner is None else winner["name"], flush=True)
    rep = dict(identity_dx=b["dx"], flat=dict(seeds=list(FLAT), succ=FLAT[1] - len(fell), speed_survivors=spd, fell=fell),
               train_seeds=list(TRAIN), held_seeds=list(HELD),
               rule="keep shoulder mean>=18, pp>=14, head yaw pp>=12, |yaw_all|<=12; max survival; within 2 falls prefer all-trial forward progress",
               train=[{k: v for k, v in r.items() if k != "fell"} | {"fell_n": len(r["fell"])} for r in table],
               chosen=None if winner is None else winner["name"])
    if winner is None:
        rep["blocker"] = "no train candidate kept the forward pose, the wave, and a yaw inside 12 deg while beating the others under the rule"
    else:
        sp = next(g for g in GRID if g["name"] == winner["name"])
        def block(name, head, T=10.0, push=None):
            kw = dict(headarm=head) if head is not None else {}
            if push is not None:
                kw["push"] = push
            s = summarize(run(jobs(HELD[0] if T == 10 and push is None else (LONG[0] if T == 20 else PUSH[0]),
                                  HELD[1] if T == 10 and push is None else (LONG[1] if T == 20 else PUSH[1]),
                                  T=T, **kw)))
            # The start index above is wrong for held. Handle held separately.
            return s
        rep["held_winner"] = summarize(run(jobs(HELD[0], HELD[1], headarm=sp)))
        show("held " + sp["name"], rep["held_winner"])
        rep["held_wave"] = summarize(run(jobs(HELD[0], HELD[1], headarm=GRID[0])))
        show("held wave", rep["held_wave"])
        still = arm(name="still", A_sh=0, A_el=0, Y_yaw=0, Y_pitch=0, Y_roll=0, k_imu=0, k_roll=0)
        rep["held_still"] = summarize(run(jobs(HELD[0], HELD[1], headarm=still)))
        show("held still", rep["held_still"])
        rep["held_walk"] = summarize(run(jobs(HELD[0], HELD[1])))
        show("held walk", rep["held_walk"])
        if rep["held_winner"]["succ"] >= 180 and abs(rep["held_winner"]["yaw_all"]) <= 12:
            rep["long"] = summarize(run(jobs(LONG[0], LONG[1], T=20.0, headarm=sp)))
            show("long", rep["long"])
            rep["push"] = summarize(run(jobs(PUSH[0], PUSH[1], headarm=sp, push=(4.0, 0.1, 0.0, 2.0))))
            show("push", rep["push"])
            rep["push_walk"] = summarize(run(jobs(PUSH[0], PUSH[1], push=(4.0, 0.1, 0.0, 2.0))))
            show("push walk", rep["push_walk"])
        else:
            rep["long"] = None
    rep["seconds"] = round(time.time() - t0, 1)
    json.dump(rep, open(os.path.join(ROOT, "results", "balance.json"), "w"), indent=1, default=float)
    print("BALANCE_DONE", rep.get("chosen"), rep["seconds"], flush=True)

if __name__ == "__main__":
    main()
