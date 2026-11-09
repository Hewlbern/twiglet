"""Lateral step and load shift on top of the sagittal balance controller.

Arm command is fixed at the forward pose and the measured wave. Positive k_lat
places the swing foot toward the side that dropped in the 51500-51523 probe
(roll about -43 deg). Train 52000-52079. Held-out 53000-53199 only after the choice.
Confirmation 54000-54199 is the same frozen controller, not a second tune.
Flat check 56000-56199. 47000 is not reused.

  python run_lateral.py
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
from simlib import params_path
import run_balance as B

TRAIN = (52000, 80)
HELD = (53000, 200)
CONFIRM = (54000, 200)
FLAT = (56000, 200)
LONG = (55000, 40)
PUSH = (55100, 40)

def base(**kw):
    s = B.arm(name="base", balance=True, body_lean=-0.02, k_place=0.6, d_place=0.05, k_hip=-0.25,
              slow_yaw_ki=0.12, slow_yaw_ulim=0.02, slow_yaw_ilim=0.5, step_width=0.0, k_roll_extra=0.0, d_roll_extra=0.0)
    s.update(kw)
    return s

GRID = [
    base(name="sagittal"),
    base(name="step_toward", k_lat=0.55, d_lat=0.06),
    base(name="wide", step_width=0.035),
    base(name="pelvis", k_roll_extra=0.45, d_roll_extra=0.05),
    base(name="step_wide", k_lat=0.45, d_lat=0.05, step_width=0.025),
    base(name="step_pelvis", k_lat=0.45, d_lat=0.05, k_roll_extra=0.30, d_roll_extra=0.04),
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
    if FLAT[1] - len(fell) < 199:
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
               roll_probe="51500-51523, 2 falls, both roll about -43 deg",
               rule="keep arm mean>=18, shoulder pp>=14, head yaw pp>=12, |yaw_all|<=8; max survival; within 2 falls prefer all-seed forward progress",
               train=[{k: v for k, v in r.items() if k != "fell"} | {"fell_n": len(r["fell"])} for r in table],
               chosen=None if winner is None else winner["name"])
    if winner is None:
        rep["blocker"] = "no lateral variant kept the pose, the wave, and the yaw cap"
    else:
        sp = next(g for g in GRID if g["name"] == winner["name"])
        sag = GRID[0]
        wave = B.arm(name="wave")
        rep["held_winner"] = B.summarize(B.run(B.jobs(HELD[0], HELD[1], headarm=sp, command_sign=-1.0)))
        B.show("held " + sp["name"], rep["held_winner"])
        rep["held_sagittal"] = B.summarize(B.run(B.jobs(HELD[0], HELD[1], headarm=sag, command_sign=-1.0))) if sp["name"] != "sagittal" else rep["held_winner"]
        if sp["name"] != "sagittal":
            B.show("held sagittal", rep["held_sagittal"])
        rep["held_wave"] = B.summarize(B.run(B.jobs(HELD[0], HELD[1], headarm=wave)))
        B.show("held wave", rep["held_wave"])
        rep["held_walk"] = B.summarize(B.run(B.jobs(HELD[0], HELD[1])))
        B.show("held walk", rep["held_walk"])
        rep["confirm"] = B.summarize(B.run(B.jobs(CONFIRM[0], CONFIRM[1], headarm=sp, command_sign=-1.0)))
        B.show("confirm", rep["confirm"])
        rep["confirm_walk"] = B.summarize(B.run(B.jobs(CONFIRM[0], CONFIRM[1])))
        B.show("confirm walk", rep["confirm_walk"])
        strong = rep["held_winner"]["succ"] >= 190 and rep["confirm"]["succ"] >= 190 and abs(rep["held_winner"]["yaw_all"]) <= 8
        if strong:
            rep["long"] = B.summarize(B.run(B.jobs(LONG[0], LONG[1], T=20.0, headarm=sp, command_sign=-1.0)))
            B.show("long", rep["long"])
            rep["push"] = B.summarize(B.run(B.jobs(PUSH[0], PUSH[1], headarm=sp, command_sign=-1.0, push=(4.0, 0.1, 0.0, 2.0))))
            B.show("push", rep["push"])
            rep["push_walk"] = B.summarize(B.run(B.jobs(PUSH[0], PUSH[1], push=(4.0, 0.1, 0.0, 2.0))))
            B.show("push walk", rep["push_walk"])
        else:
            rep["long"] = None
            rep["extension_skipped"] = "held-out or confirmation under 190/200, or yaw outside 8 deg"
    # per-joint loads of the held winner if present
    rep["seconds"] = round(time.time() - t0, 1)
    json.dump(rep, open(os.path.join(ROOT, "results", "lateral.json"), "w"), indent=1, default=float)
    print("LATERAL_DONE", rep.get("chosen"), rep["seconds"], flush=True)

if __name__ == "__main__":
    main()
