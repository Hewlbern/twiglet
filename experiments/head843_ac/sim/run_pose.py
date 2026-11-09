"""The forward arm pose, not the wave size, is what the ablation tied to the falls.

Diagnostic seeds 44000-44015 (16) are not used to pick a controller.
Train 44100-44163. Held-out after the choice is the reserved 43000-43199 (200).
Every candidate keeps A_sh=10 deg and Y_yaw=8 deg. A lower shoulder mean is a
different pose, reported separately from the peak-to-peak amplitude.

  python run_pose.py
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

TRAIN = (44100, 64)
HELD = (43000, 200)
LONG = (46000, 40)
PUSH = (46100, 40)
# 47000-47199 left unused

def spec(**kw):
    s = dict(kind="coord", A_sh=10, A_el=5, Y_yaw=8, Y_pitch=1.5, Y_roll=1.5,
             k_imu=3.0, k_roll=0.25, grip=18, t0=0.4, dur=1.4, scale_min=0.55, tilt0=0.06,
             arm_phase=1.2, head_phase=1.2, pitch0=-4.0, kp_sh=0.0, kp_head=0.0,
             sh0=22.0, el0=30.0, body_lean=0.0, yaw_ff=0.0, yaw_hold=0.0)
    s.update(kw)
    return s

GRID = [
    spec(name="mean22"),
    spec(name="mean12", sh0=12, el0=30),
    spec(name="mean8", sh0=8, el0=36),
    spec(name="mean22_lean03", body_lean=-0.03),
    spec(name="mean22_lean05", body_lean=-0.05),
    spec(name="mean12_trim", sh0=12, el0=30, body_lean=-0.02, yaw_ff=-0.02),
]
X = None

def jobs(start, n, T=10.0, **kw):
    base = dict(x=X, rand=True, T=T, measure_path=True, command_sign=-1.0, damp_align=1.0)
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
    sh, hy, shm = [], [], []
    for r in surv:
        pp = r.get("motion_pp_deg") or {}
        mn = r.get("motion_mean_deg") or {}
        if "shoulder_L" in pp:
            sh.append(0.5 * (pp["shoulder_L"] + pp["shoulder_R"]))
            shm.append(0.5 * (mn.get("shoulder_L", 0) + mn.get("shoulder_R", 0)))
        if "head_yaw" in pp:
            hy.append(pp["head_yaw"])
    def mean(key, src):
        v = [r.get(key) for r in src if r.get(key) is not None]
        return None if not v else float(np.mean(v))
    yaw_s = [math.degrees(r["yaw_change"]) for r in surv]
    yaw_a = [math.degrees(r["yaw_change"]) for r in rows]
    return dict(
        succ=len(surv), n=len(rows), fell=[r["seed"] for r in falls],
        speed=mean("speed", surv), path_speed=mean("path_speed", surv),
        yaw_survivors=None if not yaw_s else float(np.mean(yaw_s)),
        yaw_all=None if not yaw_a else float(np.mean(yaw_a)),
        shoulder_pp=med(sh), shoulder_mean=med(shm), head_yaw_pp=med(hy),
        main_rms=None if not surv else float(np.mean([r["load"]["main_rms"] for r in surv])),
        main_sat=None if not surv else float(np.mean([r["load"]["main_sat"] for r in surv])),
        fall_t=med([r["fell"] for r in falls]),
        fall_roll=None if not falls else float(np.mean([abs(math.degrees(r["roll_end"])) for r in falls])),
        fall_pitch=None if not falls else float(np.mean([abs(math.degrees(r["pitch_end"])) for r in falls])),
    )

def show(name, s):
    print(name, f"{s['succ']}/{s['n']}",
          "dx", None if s["speed"] is None else round(s["speed"], 3),
          "path", None if s["path_speed"] is None else round(s["path_speed"], 3),
          "yawS", None if s["yaw_survivors"] is None else round(s["yaw_survivors"], 1),
          "yawAll", None if s["yaw_all"] is None else round(s["yaw_all"], 1),
          "sh", s["shoulder_pp"], "shMean", s["shoulder_mean"], "hy", s["head_yaw_pp"],
          "sat", None if s["main_sat"] is None else round(100 * s["main_sat"], 2),
          flush=True)

def choose(table):
    kept = [r for r in table if (r["shoulder_pp"] or 0) >= 14 and (r["head_yaw_pp"] or 0) >= 12]
    if not kept:
        return None
    best = max(r["succ"] for r in kept)
    near = [r for r in kept if r["succ"] >= best - 2]
    # Survival first. On a tie, keep the more forward arm mean, then the smaller |yaw|.
    near.sort(key=lambda r: (-r["succ"], -(r["shoulder_mean"] or 0), abs(r["yaw_survivors"] or 99)))
    return near[0]

def main():
    global X
    t0 = time.time()
    X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(X), 5000, True, 10.0))
    b = rollout(dict(x=X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6:
        raise SystemExit("baseline dx changed")
    print("identity", round(b["dx"], 4), flush=True)
    table = []
    for sp in GRID:
        s = summarize(run(jobs(TRAIN[0], TRAIN[1], headarm=sp)))
        s["name"] = sp["name"]
        s["sh0"] = sp["sh0"]
        s["body_lean"] = sp["body_lean"]
        table.append(s)
        show("train " + sp["name"], s)
    winner = choose(table)
    print("CHOSEN", None if winner is None else winner["name"], flush=True)
    spec_w = next(sp for sp in GRID if winner and sp["name"] == winner["name"]) if winner else GRID[0]
    rep = dict(train_seeds=list(TRAIN), held_seeds=list(HELD),
               rule="same sine amplitudes; require measured shoulder pp>=14 and head yaw pp>=12; max survival; within 2 falls prefer the higher shoulder mean, then smaller |yaw|",
               ablation_note="44000-44015, 16 seeds, not used for selection: static arms at 22 deg with no swing fell 5/16; the same swing about an 8 deg mean fell 0/16",
               train=[{k: v for k, v in r.items() if k != "fell"} | {"fell_n": len(r["fell"])} for r in table],
               chosen=spec_w["name"])
    def block(name, start, n, T=10.0, push=None, head=None):
        kw = {}
        if head is not None:
            kw["headarm"] = head
        if push is not None:
            kw["push"] = push
        s = summarize(run(jobs(start, n, T=T, **kw)))
        show(name, s)
        s["seeds"] = [start, n]
        s["T"] = T
        return s
    rep["held_winner"] = block("held " + spec_w["name"], HELD[0], HELD[1], head=spec_w)
    if spec_w["name"] != "mean22":
        rep["held_mean22"] = block("held mean22", HELD[0], HELD[1], head=GRID[0])
    else:
        rep["held_mean22"] = dict(note="winner is mean22", **rep["held_winner"])
    rep["held_walk"] = block("held walk", HELD[0], HELD[1])
    if rep["held_winner"]["succ"] >= 180:
        rep["long"] = block("long", LONG[0], LONG[1], T=20.0, head=spec_w)
        rep["push"] = block("push", PUSH[0], PUSH[1], head=spec_w, push=(4.0, 0.1, 0.0, 2.0))
        rep["push_walk"] = block("push walk", PUSH[0], PUSH[1], push=(4.0, 0.1, 0.0, 2.0))
    else:
        rep["long"] = None
        rep["extension_skipped"] = "held-out under 180/200, so the 20 s and push blocks were not run"
    rep["seconds"] = round(time.time() - t0, 1)
    rep["unused"] = "47000-47199"
    json.dump(rep, open(os.path.join(ROOT, "results", "pose.json"), "w"), indent=1, default=float)
    print("POSE_DONE", rep["seconds"], "chosen", spec_w["name"], "held", rep["held_winner"]["succ"], flush=True)

if __name__ == "__main__":
    main()
