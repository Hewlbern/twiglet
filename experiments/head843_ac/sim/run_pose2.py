"""Second pose pass. The survival-only rule picked a hip-yaw trim that yaws +19 deg in 10 s
and +42 deg in 20 s. This pass rejects any candidate whose all-trial yaw exceeds 12 deg.
Amplitudes stay A_sh=10 and Y_yaw=8. Train 44200-44263. Held-out 48000-48199.
43000-43199 already tested mean12_trim and is not reused.
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
from run_pose import spec, jobs, run, summarize, show
# jobs/run/summarize use run_pose.X which is set in run_pose.main. Set it here.
import run_pose

TRAIN = (44200, 64)
HELD = (48000, 200)
YAW_CAP = 12.0
GRID = [
    spec(name="mean22"),
    spec(name="mean12", sh0=12, el0=30),
    spec(name="mean8", sh0=8, el0=36),
    spec(name="mean22_lean02", body_lean=-0.02),
    spec(name="mean22_lean03", body_lean=-0.03),
    spec(name="mean12_ff", sh0=12, el0=30, yaw_ff=-0.008),
]

def choose(table):
    kept = [r for r in table if (r["shoulder_pp"] or 0) >= 14 and (r["head_yaw_pp"] or 0) >= 12 and abs(r["yaw_all"] or 99) <= YAW_CAP]
    if not kept:
        return None, "none inside the 12 deg yaw cap"
    best = max(r["succ"] for r in kept)
    near = [r for r in kept if r["succ"] >= best - 2]
    near.sort(key=lambda r: (-r["succ"], -(r["shoulder_mean"] or 0), abs(r["yaw_all"] or 99)))
    return near[0], "max survival inside pp floor and |yaw_all|<=12; within 2 falls prefer higher shoulder mean"

def main():
    t0 = time.time()
    run_pose.X = [float(v) for v in np.load(params_path(""))]
    # jobs() in run_pose reads global X inside that module
    table = []
    for sp in GRID:
        s = summarize(run(jobs(TRAIN[0], TRAIN[1], headarm=sp)))
        s["name"] = sp["name"]
        table.append(s)
        show("train " + sp["name"], s)
    winner, why = choose(table)
    print("CHOSEN", None if winner is None else winner["name"], why, flush=True)
    rep = dict(train_seeds=list(TRAIN), held_seeds=list(HELD), yaw_cap_deg=YAW_CAP, rule=why,
               train=[{k: v for k, v in r.items() if k != "fell"} | {"fell_n": len(r["fell"])} for r in table],
               chosen=None if winner is None else winner["name"])
    if winner is None:
        # Pareto, no held-out shopping
        rep["held"] = None
        rep["blocker"] = "no train candidate kept the swing and stayed inside 12 deg of yaw"
    else:
        sp = next(g for g in GRID if g["name"] == winner["name"])
        def block(name, head):
            s = summarize(run(jobs(HELD[0], HELD[1], headarm=head)))
            show(name, s)
            return s
        rep["held_winner"] = block("held " + sp["name"], sp)
        rep["held_mean22"] = block("held mean22", GRID[0]) if sp["name"] != "mean22" else rep["held_winner"]
        rep["held_walk"] = summarize(run(jobs(HELD[0], HELD[1])))
        show("held walk", rep["held_walk"])
    rep["seconds"] = round(time.time() - t0, 1)
    json.dump(rep, open(os.path.join(ROOT, "results", "pose2.json"), "w"), indent=1, default=float)
    print("POSE2_DONE", rep["seconds"], flush=True)

if __name__ == "__main__":
    main()
