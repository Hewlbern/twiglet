"""Couple heading to the arm/head motion without shrinking the sine amplitude.

Train 39000-39031 chooses. Held-out 40000-40039 and confirmation 41000-41019
are not used for that choice. Flat regression is 42000-42199 with no overlay.
The run2 phase-locked command is included at the same amplitudes as the matched baseline.

  python run_couple.py
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
from manoeuvre import rollout, aggregate
from simlib import params_path

TRAIN = (39000, 32)
HELD = (40000, 40)
CONFIRM = (41000, 20)
FLAT = (42000, 200)
# 43000-43199 reserved, not scored

BASE = dict(kind="coord", A_sh=10, A_el=5, Y_yaw=8, Y_pitch=1.5, Y_roll=1.5,
            k_imu=3.0, k_roll=0.25, sh0=22.0, el0=30.0, pitch0=-4.0, grip=18.0,
            t0=0.4, dur=1.4, scale_min=0.55, tilt0=0.06, yaw_hold=0.0,
            couple_lim_sh=0.09, couple_lim_head=0.08)
FLOOR_SH, FLOOR_YAW = 14.0, 12.0

def spec(name, arm_phase, head_phase=None, kp_sh=0.0, kp_head=0.0):
    s = dict(BASE)
    s.update(name=name, arm_phase=float(arm_phase),
             head_phase=float(arm_phase if head_phase is None else head_phase),
             kp_sh=float(kp_sh), kp_head=float(kp_head))
    return s

GRID = [
    spec("matched_phase0", 0.0),
    spec("phase_0.6", 0.6),
    spec("phase_0.9", 0.9),
    spec("phase_1.2", 1.2),
    spec("arms0.9_head0", 0.9, 0.0),
    spec("arms0_head0.9", 0.0, 0.9),
    spec("couple_phase0", 0.0, kp_sh=0.45, kp_head=0.25),
    spec("couple_phase0.9", 0.9, kp_sh=0.45, kp_head=0.25),
]

X = None

def jobs(start, n, **kw):
    base = dict(x=X, rand=True, T=10.0, command_sign=-1.0, damp_align=1.0, measure_path=True)
    base.update(kw)
    return [dict(base, seed=start + i) for i in range(n)]

def run(js):
    with mp.Pool(4) as pool:
        return pool.map(rollout, js, chunksize=2)

def med(vals):
    vals = [v for v in vals if v is not None]
    return None if not vals else float(np.median(vals))

def row_summary(rows):
    ag = aggregate(rows)
    surv = [r for r in rows if r["fell"] is None]
    falls = [r for r in rows if r["fell"] is not None]
    sh, hy, hp = [], [], []
    for r in surv:
        m = r.get("motion_pp_deg") or {}
        if "shoulder_L" in m:
            sh.append(0.5 * (m["shoulder_L"] + m["shoulder_R"]))
        if "head_yaw" in m:
            hy.append(m["head_yaw"])
        if "head_pitch" in m:
            hp.append(m["head_pitch"])
    return dict(
        succ=ag["succ"], n=ag["n"], fell=ag["fell"],
        speed_mps=ag["speed_mps"],
        path_speed=None if not surv else float(np.mean([r["path_speed"] for r in surv if r.get("path_speed") is not None])),
        yaw_change_deg=ag.get("yaw_change_deg"),
        main_rms=ag.get("main_rms"), main_sat=ag.get("main_sat"), current_proxy_A=ag.get("current_proxy_A"),
        shoulder_pp=med(sh), head_yaw_pp=med(hy), head_pitch_pp=med(hp),
        gain=med([r.get("coord_gain_mean") for r in surv]),
        fall_roll_deg=None if not falls else float(np.mean([abs(math.degrees(r.get("roll_end") or 0)) for r in falls])),
        fall_pitch_deg=None if not falls else float(np.mean([abs(math.degrees(r.get("pitch_end") or 0)) for r in falls])),
        fall_t=med([r["fell"] for r in falls]),
    )

def floor_ok(s):
    return s.get("shoulder_pp") is not None and s.get("head_yaw_pp") is not None and s["shoulder_pp"] >= FLOOR_SH and s["head_yaw_pp"] >= FLOOR_YAW

def select(table):
    """Motion floor first. Then highest survival. Within 2 falls, smallest |yaw|, then path speed.
    A smaller wave cannot win, because it fails the floor shared with the matched baseline."""
    kept = [r for r in table if r["floor"]]
    if not kept:
        return None
    best = max(r["succ"] for r in kept)
    near = [r for r in kept if r["succ"] >= best - 2]
    near.sort(key=lambda r: (abs(r["yaw_change_deg"] or 999), -r["succ"], -(r["path_speed"] or 0)))
    return near[0]

def show(name, s):
    print(name, f"{s['succ']}/{s['n']}", "dx", None if s["speed_mps"] is None else round(s["speed_mps"], 3),
          "path", None if s["path_speed"] is None else round(s["path_speed"], 3),
          "yaw", None if s["yaw_change_deg"] is None else round(s["yaw_change_deg"], 1),
          "sh", None if s["shoulder_pp"] is None else round(s["shoulder_pp"], 1),
          "hy", None if s["head_yaw_pp"] is None else round(s["head_yaw_pp"], 1),
          "sat", None if s["main_sat"] is None else round(100 * s["main_sat"], 2),
          "rms", None if s["main_rms"] is None else round(s["main_rms"], 3),
          "fall_rp", None if s["fall_roll_deg"] is None else (round(s["fall_roll_deg"], 1), round(s["fall_pitch_deg"], 1)),
          flush=True)

def main():
    global X
    t0 = time.time()
    X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(X), 5000, True, 10.0))
    b = rollout(dict(x=X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6 or bool(a["fell"]) != (b["fell"] is not None):
        raise SystemExit("flat path drifted")
    print("identity ok", round(b["dx"], 4), flush=True)
    rep = dict(floor=dict(shoulder_pp=FLOOR_SH, head_yaw_pp=FLOOR_YAW),
               amplitudes=dict(A_sh=10, Y_yaw=8, Y_pitch=1.5, Y_roll=1.5),
               couple="clipped shoulder differential and head-yaw bias from heading error; hip yaw stays at the gait value 0",
               rule="same sine amplitudes; reject below 14 deg shoulder and 12 deg head-yaw peak-to-peak; then max survival; within 2 falls minimize |yaw change|; then path speed")
    s, n = TRAIN
    table = []
    for sp in GRID:
        summary = row_summary(run(jobs(s, n, headarm=sp)))
        summary["name"] = sp["name"]
        summary["floor"] = floor_ok(summary)
        summary["arm_phase"] = sp["arm_phase"]
        summary["head_phase"] = sp["head_phase"]
        summary["kp_sh"] = sp["kp_sh"]
        table.append(summary)
        show("train " + sp["name"], summary)
    chosen = select(table)
    rep["train"] = dict(seeds=list(TRAIN), table=[{k: v for k, v in r.items() if k != "fell"} | {"fell_n": len(r["fell"])} for r in table],
                        chosen=None if chosen is None else chosen["name"])
    print("CHOSEN", None if chosen is None else chosen["name"], flush=True)
    winner = next(sp for sp in GRID if chosen and sp["name"] == chosen["name"]) if chosen else GRID[0]
    matched = GRID[0]
    s, n = HELD
    rep["held_winner"] = dict(seeds=list(HELD), **{k: v for k, v in row_summary(run(jobs(s, n, headarm=winner))).items()})
    show("held winner", rep["held_winner"])
    if winner["name"] != "matched_phase0":
        rep["held_matched"] = dict(seeds=list(HELD), **row_summary(run(jobs(s, n, headarm=matched))))
        show("held matched", rep["held_matched"])
    else:
        rep["held_matched"] = dict(note="winner is the matched baseline; not run twice", **rep["held_winner"])
    rep["held_walkonly"] = dict(seeds=list(HELD), **row_summary(run(jobs(s, n))))
    show("held walkonly", rep["held_walkonly"])
    s, n = CONFIRM
    rep["confirm"] = dict(seeds=list(CONFIRM), **row_summary(run(jobs(s, n, headarm=winner))))
    show("confirm", rep["confirm"])
    print("flat regression", flush=True)
    with mp.Pool(4) as pool:
        R = W.batch([np.array(X)] * FLAT[1], range(FLAT[0], sum(FLAT)), True, pool, T=10.0)
    fell = [FLAT[0] + i for i, r in enumerate(R) if r["fell"]]
    spd = float(np.mean([r["dx"] / 10.0 for r in R if not r["fell"]] or [0]))
    rep["flat"] = dict(seeds=list(FLAT), succ=FLAT[1] - len(fell), n=FLAT[1], fell=fell, speed=spd, pass_199=(FLAT[1] - len(fell) >= 199))
    print("flat", rep["flat"]["succ"], round(spd, 4), fell[:6], flush=True)
    rep["seconds"] = round(time.time() - t0, 1)
    rep["reserved_unscored"] = "43000-43199"
    json.dump(rep, open(os.path.join(ROOT, "results", "couple.json"), "w"), indent=1, default=float)
    print("COUPLE_DONE", rep["seconds"], flush=True)

if __name__ == "__main__":
    main()
