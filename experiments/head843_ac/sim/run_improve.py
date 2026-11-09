"""Controller improvement pass. Reliable gait vector and AC plant stay fixed.

Train blocks are declared here and are the only scores used to pick a controller.
Held-out blocks are scored after that choice. The wait-at-zero start is not a candidate.

  python run_improve.py
"""
import os, sys, json, math, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
os.environ["TWIGLET_SCENE"] = os.path.join(ROOT, "geometry", "scene_v335ac.npz")
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
from manoeuvre import rollout, aggregate, SmoothWalk
from simlib import params_path

# Declared before any of these seeds are scored.
TRAIN_COORD = (30000, 32)     # head/arm coordination
TRAIN_START = (31000, 20)     # smooth start duration
TRAIN_HEAD = (32000, 24)      # heading integral, both turn signs
HELD_COORD_RESERVED = (29020, 40)   # previously unused
HELD_COORD_FRESH = (33000, 40)
HELD_START = (34000, 40)
HELD_HEAD = (35000, 40)       # +20 and -20
FLAT_FRESH = (36000, 200)     # unmodified reliable, regression
PUSH_FRESH = (37000, 20)
# 38000-38199 left unused

COORD = [
    dict(name="phase_arms10_yaw10", kind="coord", A_sh=10, A_el=5, Y_yaw=10, Y_pitch=3, Y_roll=1.5, k_imu=0.0, k_roll=0.0, arm_phase=0.0),
    dict(name="phase_imu", kind="coord", A_sh=10, A_el=5, Y_yaw=10, Y_pitch=3, Y_roll=1.5, k_imu=2.0, k_roll=0.25, arm_phase=0.0),
    dict(name="phase_imu_bigger", kind="coord", A_sh=14, A_el=6, Y_yaw=12, Y_pitch=4, Y_roll=2.0, k_imu=2.0, k_roll=0.25, arm_phase=0.0),
    dict(name="phase_imu_modest", kind="coord", A_sh=8, A_el=4, Y_yaw=8, Y_pitch=2, Y_roll=1.0, k_imu=2.5, k_roll=0.2, arm_phase=0.0),
    dict(name="phase_imu_quad", kind="coord", A_sh=12, A_el=5, Y_yaw=14, Y_pitch=3, Y_roll=2.0, k_imu=1.5, k_roll=0.25, arm_phase=math.pi / 2),
    dict(name="phase_counterroll", kind="coord", A_sh=12, A_el=5, Y_yaw=10, Y_pitch=3, Y_roll=2.5, k_imu=2.0, k_roll=0.45, arm_phase=0.0),
    dict(name="phase_imu_softpitch", kind="coord", A_sh=10, A_el=5, Y_yaw=8, Y_pitch=1.5, Y_roll=1.5, k_imu=3.0, k_roll=0.25, arm_phase=0.0),
]
for c in COORD:
    c.update(sh0=22.0, el0=30.0, pitch0=-4.0, grip=18.0, t0=0.4, dur=1.4, scale_min=0.55, tilt0=0.06)
START_DURS = (1.0, 1.2, 1.5)
HEAD_KI = (0.0, 0.15, 0.4)
MOTION_FLOOR = dict(shoulder_pp_deg=8.0, head_yaw_pp_deg=6.0)
SIGN, DAMP = -1.0, 1.0
X = None

def jobs(start, n, **kw):
    base = dict(x=X, rand=True, T=10.0, command_sign=SIGN, damp_align=DAMP)
    base.update(kw)
    return [dict(base, seed=start + i) for i in range(n)]

def run(js):
    if not js:
        return []
    with mp.Pool(4) as pool:
        return pool.map(rollout, js, chunksize=2)

def _med(vals):
    vals = [v for v in vals if v is not None]
    return None if not vals else float(np.median(vals))

def summarise(rows):
    ag = aggregate(rows)
    surv = [r for r in rows if r["fell"] is None]
    def pp(key):
        return _med([(r.get("motion_pp_deg") or {}).get(key) for r in surv])
    sh = []
    for r in surv:
        m = r.get("motion_pp_deg") or {}
        if "shoulder_L" in m and "shoulder_R" in m:
            sh.append(0.5 * (m["shoulder_L"] + m["shoulder_R"]))
    ag["shoulder_pp_deg"] = _med(sh)
    ag["head_yaw_pp_deg"] = pp("head_yaw")
    ag["head_pitch_pp_deg"] = pp("head_pitch")
    ag["head_roll_pp_deg"] = pp("head_roll")
    ag["elbow_pp_deg"] = _med([0.5 * ((r.get("motion_pp_deg") or {}).get("elbow_L", 0) + (r.get("motion_pp_deg") or {}).get("elbow_R", 0)) for r in surv if r.get("motion_pp_deg")])
    ag["coord_gain_median"] = _med([r.get("coord_gain_mean") for r in surv])
    ag["fell_times"] = [round(r["fell"], 3) for r in rows if r["fell"] is not None][:12]
    return ag

def pack(name, rows, extra=None):
    ag = summarise(rows)
    body = dict(name=name, aggregate=ag, seeds=[dict(
        seed=r["seed"], fell=r["fell"], speed=r["speed"],
        main_rms=None if not r.get("load") else round(r["load"]["main_rms"], 4),
        main_sat=None if not r.get("load") else round(r["load"]["main_sat"], 4),
        motion_pp_deg=r.get("motion_pp_deg"),
        coord_gain_mean=r.get("coord_gain_mean"),
        heading_err_rms_deg=(r.get("heading") or {}).get("heading_err_rms_deg"),
        heading_err_final_deg=(r.get("heading") or {}).get("heading_err_final_deg"),
        yaw_change_deg=round(math.degrees(r["yaw_change"]), 3) if r.get("yaw_change") is not None else None,
        speed_before_stop=(r.get("stop") or {}).get("speed_before_stop"),
        speed_after_settle=(r.get("stop") or {}).get("speed_after_settle"),
        disp_after_stop_m=(r.get("stop") or {}).get("disp_after_stop_m")) for r in rows])
    if extra:
        body.update(extra)
    print(name, f"{ag['succ']}/{ag['n']}", "spd", None if ag.get("speed_mps") is None else round(ag["speed_mps"], 3),
          "sh", ag.get("shoulder_pp_deg"), "yaw", ag.get("head_yaw_pp_deg"),
          "gain", ag.get("coord_gain_median"), "rms", None if ag.get("main_rms") is None else round(ag["main_rms"], 3),
          "herr", ag.get("heading_err_rms_deg"), "dYaw", ag.get("yaw_change_deg"), flush=True)
    return body

def meets_floor(ag):
    sh, hy = ag.get("shoulder_pp_deg"), ag.get("head_yaw_pp_deg")
    return sh is not None and hy is not None and sh >= MOTION_FLOOR["shoulder_pp_deg"] and hy >= MOTION_FLOOR["head_yaw_pp_deg"]

def select_coord(table):
    """Max survival. Within 1 fall, require the motion floor, then largest shoulder+0.5*yaw, then speed."""
    best = max(r["succ"] for r in table)
    near = [r for r in table if r["succ"] >= best - 1]
    floored = [r for r in near if r["floor"]]
    pool = floored or near
    def key(r):
        motion = (r.get("shoulder_pp_deg") or 0) + 0.5 * (r.get("head_yaw_pp_deg") or 0)
        return (-r["succ"], 0 if r["floor"] else 1, -motion, -(r.get("speed_mps") or 0))
    pool.sort(key=key)
    return pool[0]

def href(delta_deg, ki):
    return dict(kind="feedback", kp=0.6, kd=0.02, ki=float(ki), ilim=0.35, limit=math.radians(7),
                t0=3.0, t1=5.5, delta=math.radians(delta_deg))

def main():
    global X
    t0 = time.time()
    X = [float(v) for v in np.load(params_path(""))]
    # identity: default path still matches the published evaluator
    checks = []
    for seed, rand in ((5000, True), (0, False)):
        a = W.evaluate((np.array(X), seed, rand, 10.0))
        b = rollout(dict(x=X, seed=seed, rand=rand, T=10.0))
        ok = abs(a["dx"] - b["dx"]) < 1e-6 and (bool(a["fell"]) == (b["fell"] is not None))
        checks.append(dict(seed=seed, ok=bool(ok), dx=b["dx"], fell=b["fell"]))
        if not ok:
            raise SystemExit("baseline path changed " + json.dumps(checks[-1], default=str))
    print("identity", checks, flush=True)
    sw = SmoothWalk(2.214964588932748, 1.2, 6.0)
    print("smooth schedule", sw.info(), flush=True)
    rep = dict(identity=checks, motion_floor=MOTION_FLOOR,
               coord_grid=[{k: c[k] for k in ("name", "A_sh", "A_el", "Y_yaw", "Y_pitch", "Y_roll", "k_imu", "k_roll", "arm_phase", "scale_min")} for c in COORD],
               note="Reliable parameter vector is not modified. Overlays only. Wait-at-zero start is not a candidate.")

    # --- coordination train ---
    s, n = TRAIN_COORD
    table = []
    for spec in COORD:
        rows = run(jobs(s, n, headarm=spec))
        body = pack("train_" + spec["name"], rows)
        ag = body["aggregate"]
        table.append(dict(name=spec["name"], succ=ag["succ"], n=ag["n"], speed_mps=ag["speed_mps"],
                          main_rms=ag["main_rms"], main_sat=ag["main_sat"], current_proxy_A=ag["current_proxy_A"],
                          shoulder_pp_deg=ag["shoulder_pp_deg"], head_yaw_pp_deg=ag["head_yaw_pp_deg"],
                          head_pitch_pp_deg=ag["head_pitch_pp_deg"], head_roll_pp_deg=ag["head_roll_pp_deg"],
                          elbow_pp_deg=ag["elbow_pp_deg"], coord_gain_median=ag["coord_gain_median"],
                          floor=meets_floor(ag), fell=ag["fell"][:8]))
    chosen = select_coord(table)
    spec = next(c for c in COORD if c["name"] == chosen["name"])
    rep["coord_train"] = dict(seeds=list(TRAIN_COORD), table=table, chosen=chosen["name"], meets_floor=chosen["floor"],
                              rule="max survival; within 1 fall keep only motion-floor candidates if any; then largest median shoulder pp + 0.5*head-yaw pp, then speed")
    print("CHOSEN", chosen["name"], "floor", chosen["floor"], flush=True)

    s, n = HELD_COORD_FRESH
    rep["coord_held_fresh"] = pack("coord_fresh", run(jobs(s, n, headarm=spec)), extra=dict(seeds=list(HELD_COORD_FRESH)))
    rep["mild_on_fresh"] = pack("old_mild_fresh", run(jobs(s, n, headarm="mild")), extra=dict(seeds=list(HELD_COORD_FRESH), role="paired previous command, not used to choose"))
    rep["walkonly_on_fresh"] = pack("walkonly_fresh", run(jobs(s, n)), extra=dict(seeds=list(HELD_COORD_FRESH)))
    s, n = HELD_COORD_RESERVED
    rep["coord_held_29020"] = pack("coord_29020", run(jobs(s, n, headarm=spec)), extra=dict(seeds=list(HELD_COORD_RESERVED)))

    # disturbance, not used for selection
    s, n = PUSH_FRESH
    push = (4.0, 0.1, 0.0, 2.0)
    rep["push_coord"] = pack("push_coord", run(jobs(s, n, headarm=spec, push=push)), extra=dict(push_N_s=[0.0, 2.0, 0.1], seeds=list(PUSH_FRESH)))
    rep["push_walkonly"] = pack("push_walkonly", run(jobs(s, n, push=push)), extra=dict(seeds=list(PUSH_FRESH)))

    # --- smooth start, no motionless wait ---
    s, n = TRAIN_START
    start_table = []
    for dur in START_DURS:
        rows = run(jobs(s, n, T=9.0, amp=dict(kind="smooth_walk", dur=dur, t_stop=6.0)))
        body = pack(f"train_smooth_{dur}", rows)
        ag = body["aggregate"]
        start_table.append(dict(dur=dur, succ=ag["succ"], n=ag["n"], speed_before=ag["speed_before_stop"],
                                speed_after=ag["speed_after_settle"], disp=ag["disp_after_stop_m"], fell=ag["fell"][:8]))
    best_s = max(r["succ"] for r in start_table)
    near = [r for r in start_table if r["succ"] >= best_s - 1]
    near.sort(key=lambda r: (abs(r["dur"] - 1.2), -r["succ"]))
    dur = near[0]["dur"]
    rep["start_train"] = dict(seeds=list(TRAIN_START), table=start_table, chosen_dur=dur,
                              rule="highest survival; within 1 fall choose duration closest to 1.2 s. Wait-at-zero is not eligible.")
    rep["start_held"] = pack("smooth_held", run(jobs(HELD_START[0], HELD_START[1], T=9.0, amp=dict(kind="smooth_walk", dur=dur, t_stop=6.0))),
                            extra=dict(seeds=list(HELD_START), dur=dur))

    # --- heading integral, both signs on the train set ---
    s, n = TRAIN_HEAD
    head_table = []
    for ki in HEAD_KI:
        pos = summarise(run(jobs(s, n, heading=href(20, ki))))
        neg = summarise(run(jobs(s, n, heading=href(-20, ki))))
        head_table.append(dict(
            ki=ki, succ_pos=pos["succ"], succ_neg=neg["succ"], n=n,
            rms_pos=pos["heading_err_rms_deg"], rms_neg=neg["heading_err_rms_deg"],
            final_pos=pos["heading_err_final_deg"], final_neg=neg["heading_err_final_deg"],
            yaw_pos=pos["yaw_change_deg"], yaw_neg=neg["yaw_change_deg"],
            speed_pos=pos["speed_mps"], speed_neg=neg["speed_mps"],
            asym=None if pos["yaw_change_deg"] is None or neg["yaw_change_deg"] is None else abs(abs(pos["yaw_change_deg"]) - abs(neg["yaw_change_deg"]))))
        print("ki", ki, head_table[-1], flush=True)
    def hkey(r):
        rms = (r["rms_pos"] or 99) + (r["rms_neg"] or 99)
        return (-min(r["succ_pos"], r["succ_neg"]), -(r["succ_pos"] + r["succ_neg"]), rms, r["asym"] or 99)
    head_table_sorted = sorted(head_table, key=hkey)
    ki = head_table_sorted[0]["ki"]
    rep["heading_train"] = dict(seeds=list(TRAIN_HEAD), table=head_table, chosen_ki=ki,
                                rule="max the worse of the two turn signs, then total survival, then sum of RMS, then yaw-change asymmetry")
    s, n = HELD_HEAD
    rep["heading_held_pos"] = pack("head_pos", run(jobs(s, n, heading=href(20, ki))), extra=dict(seeds=list(HELD_HEAD), ki=ki))
    rep["heading_held_neg"] = pack("head_neg", run(jobs(s, n, heading=href(-20, ki))), extra=dict(seeds=list(HELD_HEAD), ki=ki))
    rep["heading_held_pos_ki0"] = pack("head_pos_ki0", run(jobs(s, n, heading=href(20, 0.0))), extra=dict(role="same seeds, previous kp/kd without integral"))
    rep["heading_held_neg_ki0"] = pack("head_neg_ki0", run(jobs(s, n, heading=href(-20, 0.0))))

    # flat regression on an unused block, original evaluator and the rollout path
    print("flat regression", flush=True)
    with mp.Pool(4) as pool:
        R = W.batch([np.array(X)] * FLAT_FRESH[1], range(FLAT_FRESH[0], FLAT_FRESH[0] + FLAT_FRESH[1]), True, pool, T=10.0)
    fell = [FLAT_FRESH[0] + i for i, r in enumerate(R) if r["fell"]]
    spd = float(np.mean([r["dx"] / 10 for r in R if not r["fell"]] or [0]))
    rep["flat_regression"] = dict(seeds=list(FLAT_FRESH), succ=FLAT_FRESH[1] - len(fell), n=FLAT_FRESH[1], fell=fell, speed=spd,
                                 pass_199=FLAT_FRESH[1] - len(fell) >= 199)
    print("flat", rep["flat_regression"]["succ"], spd, fell[:8], flush=True)
    rep["seconds"] = round(time.time() - t0, 1)
    rep["unused_after"] = "38000-38199 not used"
    out = os.path.join(ROOT, "results", "improve.json")
    json.dump(rep, open(out, "w"), indent=1, default=float)
    print("IMPROVE_DONE", rep["seconds"], out, flush=True)

if __name__ == "__main__":
    main()
