"""Stance-foot load shift when the body rolls toward the swing leg.

Known falls on 53000/54000, not used for gains, unload the stance foot and fall
toward the swing side. k_load shifts the pelvis toward the stance foot only
while that rate is present. The arm wave is unchanged.

Train 57000-57079. Held-out 58000-58199 and confirmation 59000-59199 after the freeze.
Flat 61000-61199. Long and push only if both 200-seed blocks are at least 196/200
and |yaw_all| is at most 8 deg.

  python run_lateral2.py
"""
import os, sys, json, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
from simlib import params_path
import run_balance as B

TRAIN, HELD, CONFIRM = (57000, 80), (58000, 200), (59000, 200)
FLAT, LONG, PUSH = (61000, 200), (60000, 40), (60100, 40)

def base(**kw):
    s = B.arm(name="base", balance=True, body_lean=-0.02, k_place=0.6, d_place=0.05, k_hip=-0.25,
              k_lat=0.45, d_lat=0.05, k_roll_extra=0.30, d_roll_extra=0.04,
              slow_yaw_ki=0.12, slow_yaw_ulim=0.02, slow_yaw_ilim=0.5, k_load=0.0)
    s.update(kw)
    return s

GRID = [
    base(name="current"),
    base(name="no_into_fall", k_roll_extra=0.0, d_roll_extra=0.0),
    base(name="load04", k_roll_extra=0.0, d_roll_extra=0.0, k_load=0.04),
    base(name="load08", k_roll_extra=0.0, d_roll_extra=0.0, k_load=0.08),
    base(name="load_keep", k_load=0.05),
    base(name="load_step", k_roll_extra=0.0, d_roll_extra=0.0, k_load=0.06, k_lat=0.7, d_lat=0.08),
]

def eligible(r):
    return ((r["shoulder_pp"] or 0) >= 14 and (r["head_yaw_pp"] or 0) >= 12
            and (r["shoulder_mean"] or 0) >= 18 and abs(r["yaw_all"]) <= 8)

def choose(table):
    kept = [r for r in table if eligible(r)]
    if not kept:
        return None
    best = max(r["succ"] for r in kept)
    near = [r for r in kept if r["succ"] >= best - 2]
    near.sort(key=lambda r: (-r["succ"], -(r["progress_all"] or 0), abs(r["yaw_all"])))
    return near[0]

def yaw_dist(rows):
    ys = np.degrees([r["yaw_change"] for r in rows])
    return dict(n=int(len(ys)), median=float(np.median(ys)), p10=float(np.percentile(ys, 10)),
                p90=float(np.percentile(ys, 90)), min=float(ys.min()), max=float(ys.max()),
                frac_abs_gt_15=float(np.mean(np.abs(ys) > 15)),
                frac_abs_gt_8=float(np.mean(np.abs(ys) > 8)))

def main():
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6:
        raise SystemExit("baseline changed")
    print("identity", round(b["dx"], 4), flush=True)
    with mp.Pool(4) as pool:
        R = W.batch([np.array(B.X)] * FLAT[1], range(FLAT[0], FLAT[0] + FLAT[1]), True, pool, T=10.0)
    fell = [FLAT[0] + i for i, r in enumerate(R) if r["fell"]]
    spd = float(np.mean([r["dx"] / 10 for r in R if not r["fell"]] or [0]))
    print("flat", FLAT[1] - len(fell), round(spd, 4), fell[:6], flush=True)
    # The untouched gait is 199/200 or 200/200 on published blocks, not always 200.
    # Identity with seed 5000 is the check that this process did not change that path.
    if FLAT[1] - len(fell) < 197:
        raise SystemExit("flat regression")
    table = []
    for sp in GRID:
        s = B.summarize(B.run(B.jobs(TRAIN[0], TRAIN[1], headarm=sp, command_sign=-1.0)))
        s["name"] = sp["name"]
        table.append(s)
        B.show("train " + sp["name"], s)
    winner = choose(table)
    print("CHOSEN", None if winner is None else winner["name"], flush=True)
    rep = dict(flat=dict(seeds=list(FLAT), succ=FLAT[1] - len(fell), speed=spd, fell=fell),
               train_seeds=list(TRAIN), held_seeds=list(HELD), confirm_seeds=list(CONFIRM),
               mechanism="falls in 53000/54000 unload the stance sole and roll toward the swing leg",
               yaw_mechanism="on 20 s the hip-yaw trim sits at ±0.02 rad for most of the trial; block means hide tails past ±15 deg",
               rule="arm mean>=18, shoulder pp>=14, head yaw pp>=12, |yaw_all|<=8; max survival; within 2 falls prefer all-seed progress",
               train=[{k: v for k, v in r.items() if k != "fell"} | {"fell_n": len(r["fell"])} for r in table],
               chosen=None if winner is None else winner["name"])
    if winner is None:
        rep["blocker"] = "no load-shift candidate cleared the pose and yaw gates"
    else:
        sp = next(g for g in GRID if g["name"] == winner["name"])
        cur = GRID[0]
        wave = B.arm(name="wave")
        def held(name, head, start):
            rows = B.run(B.jobs(start, 200, headarm=head, command_sign=-1.0 if head else 1.0))
            s = B.summarize(rows)
            s["yaw_dist"] = yaw_dist(rows)
            B.show(name, s)
            return s
        rep["held_winner"] = held("held " + sp["name"], sp, HELD[0])
        rep["held_current"] = held("held current", cur, HELD[0]) if sp["name"] != "current" else rep["held_winner"]
        rep["held_wave"] = held("held wave", wave, HELD[0])
        rep["held_walk"] = held("held walk", None, HELD[0])
        rep["confirm"] = held("confirm", sp, CONFIRM[0])
        rep["confirm_walk"] = held("confirm walk", None, CONFIRM[0])
        ok = (rep["held_winner"]["succ"] >= 196 and rep["confirm"]["succ"] >= 196
              and abs(rep["held_winner"]["yaw_all"]) <= 8 and abs(rep["confirm"]["yaw_all"]) <= 8)
        if ok:
            rows = B.run(B.jobs(LONG[0], LONG[1], T=20.0, headarm=sp, command_sign=-1.0, keep_trace=True))
            rep["long"] = B.summarize(rows)
            rep["long"]["yaw_dist"] = yaw_dist(rows)
            # saturation of the ±0.02 command
            sats = []
            for r in rows:
                u = np.array([p["hip_yaw"] for p in r["trace"]])
                sats.append(float(np.mean(np.abs(np.abs(u) - sp["slow_yaw_ulim"]) < 1e-4)))
            rep["long"]["hip_yaw_sat_median"] = float(np.median(sats))
            rep["long"]["hip_yaw_sat_p90"] = float(np.percentile(sats, 90))
            B.show("long", rep["long"])
            print("long yaw dist", rep["long"]["yaw_dist"], "sat", rep["long"]["hip_yaw_sat_median"], flush=True)
            rep["push"] = B.summarize(B.run(B.jobs(PUSH[0], PUSH[1], headarm=sp, command_sign=-1.0, push=(4.0, 0.1, 0.0, 2.0))))
            B.show("push", rep["push"])
            rep["push_walk"] = B.summarize(B.run(B.jobs(PUSH[0], PUSH[1], push=(4.0, 0.1, 0.0, 2.0))))
            B.show("push walk", rep["push_walk"])
        else:
            rep["long"] = None
            rep["extension_skipped"] = "one of the 200-seed blocks is under 196/200 or |yaw| exceeds 8 deg"
    rep["seconds"] = round(time.time() - t0, 1)
    # drop bulky traces if any slipped in
    json.dump(rep, open(os.path.join(ROOT, "results", "lateral2.json"), "w"), indent=1, default=float)
    print("LATERAL2_DONE", rep.get("chosen"), rep["seconds"], flush=True)

if __name__ == "__main__":
    main()
