"""Train vs held-out manoeuvre study on the unchanged reliable gait.

Does not write params/, the AC XML, or the scene. Does not promote a gait.
Historical seed blocks are reproduction only. Fresh blocks are declared in seed_registry.py.

Usage (from sim/):
  python run_capabilities.py            # full study
  python run_capabilities.py --quick    # tiny smoke of every suite
"""
import os, sys, json, math, hashlib, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault("TWIGLET_XML", "twiglet_v3_v335ac.xml")
os.environ.setdefault("TWIGLET_PARAMS", os.path.join(ROOT, "params", "reliable.npy"))
os.environ.setdefault("TWIGLET_PARAMS_EFF", os.path.join(ROOT, "params", "efficient.npy"))
os.environ.setdefault("TWIGLET_OUT", os.path.join(ROOT, "results"))
os.environ.setdefault("TWIGLET_SCENE", os.path.join(ROOT, "geometry", "scene_v335ac.npz"))
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
from simlib import params_path, OUT
from manoeuvre import rollout, aggregate, wrap
from seed_registry import FRESH, assert_disjoint
import terrain_fixtures as TF

QUICK = "--quick" in sys.argv
OUTDIR = os.environ["TWIGLET_OUT"]
os.makedirs(OUTDIR, exist_ok=True)
LOCKED = {
    "params/reliable.npy": "d18f884ff5146eb0ed09cb8ab7562337482dd42c669649b4acd90c24ac083754",
    "params/fast.npy": "aeb2c4ba3cd4dbbd0d382272292d09c63d7620422f05b671ac6297fc659c3cad",
    "params/efficient.npy": "4f32549810c671d72c40719e1d19af53f83e8d2ededbe9460db668b891e39093",
    "sim/models/twiglet_v3_v335ac.xml": "5e62e84b4fbc20270d8331274b33190f4e83dfc6a422a95bad45c19afdf6503b",
    "geometry/scene_v335ac.npz": "e2d3009f6c35cfdfcefabf7ec9013ee9193547d5c4d16de37db78f0d07a60aba",
}
# Predeclared before any fresh score is read.
HEADING_GAINS = [(0.6, 0.02), (0.6, 0.08), (1.2, 0.02), (1.2, 0.08), (2.0, 0.05), (2.0, 0.12)]
HEADING_LIMIT = math.radians(7.0)
TURN_DEG = 20.0
TURN_WINDOW = (3.0, 5.5)
LOAD_SCALES = [
    ("reliable", {}),
    ("stride097", {"stride": 0.97}),
    ("f097", {"f": 0.97}),
    ("f_stride097", {"f": 0.97, "stride": 0.97}),
    ("sway097", {"sway": 0.97}),
    ("lift098", {"lift": 0.98}),
    ("kp_pitch090", {"kp_pitch": 0.90}),
    ("ank_off_plus_0.01", {"ank_off": 1.0}),  # scale 1, then add
]
LOAD_ADD = {"ank_off_plus_0.01": {"ank_off": 0.01}}
AMP_PHASE = dict(kind="phase", t_go=0.6, t_stop=6.0, ramp_cycles=1.0)
AMP_ABRUPT = dict(kind="abrupt", t_go=0.6, t_stop=6.0, ramp_cycles=1.0)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def check_locks():
    bad = {}
    for rel, want in LOCKED.items():
        got = sha256(os.path.join(ROOT, rel))
        if got != want:
            bad[rel] = got
    if bad:
        raise SystemExit("locked asset hash mismatch: " + json.dumps(bad))
    assert_disjoint()

def n_of(name):
    start, n, role = FRESH[name]
    if QUICK:
        n = min(n, 2)
    return start, n, role

def heading_spec(delta_deg, kp, kd, t0=None, t1=None):
    a, b = TURN_WINDOW if t0 is None else (t0, t1)
    return dict(kind="feedback", kp=float(kp), kd=float(kd), limit=HEADING_LIMIT,
                t0=float(a), t1=float(b), delta=math.radians(delta_deg))

def make_jobs(x, start, n, **kw):
    base = dict(x=[float(v) for v in x], rand=True, T=10.0,
                command_sign=SIGN, damp_align=DAMP)
    base.update(kw)
    return [dict(base, seed=start + i) for i in range(n)]

def run_pool(jobs):
    if not jobs:
        return []
    with mp.Pool(4) as pool:
        return pool.map(rollout, jobs, chunksize=2)

def compact(rows):
    out = []
    for r in rows:
        h = r.get("heading") or {}
        s = r.get("stop") or {}
        out.append(dict(seed=r["seed"], fell=r["fell"], speed=r["speed"], dx=round(r["dx"], 4), dy=round(r["dy"], 4),
                        main_rms=None if not r.get("load") else round(r["load"]["main_rms"], 4),
                        main_sat=None if not r.get("load") else round(r["load"]["main_sat"], 4),
                        heading_err_rms_deg=h.get("heading_err_rms_deg"),
                        heading_err_final_deg=h.get("heading_err_final_deg"),
                        yaw_change_deg=None if "yaw_change" not in r and "yaw_change" not in h else round(math.degrees(r.get("yaw_change", h.get("yaw_change", 0.0))), 3),
                        straight_crosstrack_rms_m=r.get("straight_crosstrack_rms_m"),
                        speed_before_stop=s.get("speed_before_stop"),
                        speed_after_settle=s.get("speed_after_settle"),
                        tracking_rms_deg=None if not r.get("tracking_rms") else {k: round(math.degrees(v), 2) for k, v in r["tracking_rms"].items()}))
    return out

def pack(name, rows, extra=None):
    ag = aggregate(rows)
    # joints stay in the aggregate; per-seed rows are compact
    body = dict(name=name, aggregate=ag, seeds=compact(rows))
    if extra:
        body.update(extra)
    return body

def scaled(x, name, scales):
    y = np.array(x, float)
    for k, s in scales.items():
        y[W.KEYS.index(k)] *= s
    for k, s in LOAD_ADD.get(name, {}).items():
        y[W.KEYS.index(k)] += s
    clipped = np.clip(y, W.LO, W.HI)
    return clipped, bool(np.any(np.abs(clipped - y) > 1e-12))

def select_heading(table):
    """Highest survival, then lowest heading RMS (deg) on survivors, then smaller kp.
    A gain within 1 fall of the best survival is eligible."""
    ranked = sorted(table, key=lambda r: (-r["succ"], r["heading_err_rms_deg"] if r["heading_err_rms_deg"] is not None else 1e9, abs(r["kp"])))
    best_succ = ranked[0]["succ"]
    eligible = [r for r in ranked if r["succ"] >= best_succ - 1]
    eligible.sort(key=lambda r: (-r["succ"], r["heading_err_rms_deg"] if r["heading_err_rms_deg"] is not None else 1e9, abs(r["kp"])))
    return eligible[0], eligible

def select_load(table):
    """Accept a non-baseline perturbation only if, on the tune seeds, survival is at least
    the reliable count, speed is at least 97% of reliable, and either main RMS drops 2%
    or main saturation drops 10% relative. Lowest saturation, then lowest RMS, wins.
    Held-out seeds are not an input to this function."""
    rel = next(r for r in table if r["name"] == "reliable")
    accepted = []
    for r in table:
        if r["name"] == "reliable":
            continue
        if r["succ"] < rel["succ"]:
            continue
        if r["speed_mps"] is None or rel["speed_mps"] is None or r["speed_mps"] < 0.97 * rel["speed_mps"]:
            continue
        rms_ok = r["main_rms"] is not None and r["main_rms"] <= 0.98 * rel["main_rms"]
        sat_ok = r["main_sat"] is not None and r["main_sat"] <= 0.90 * rel["main_sat"]
        if rms_ok or sat_ok:
            accepted.append(r)
    accepted.sort(key=lambda r: (r["main_sat"], r["main_rms"]))
    return (accepted[0] if accepted else None), rel

def calibrate(x):
    row = rollout(dict(x=[float(v) for v in x], seed=0, rand=False, T=4.0, turn_bias=0.08, calibrate=True))
    ts = np.array(row["cal_trace_t"]); yw = np.unwrap(np.array(row["cal_trace_yaw"])); gz = np.array(row["cal_trace_gz"])
    dy = float(yw[-1] - yw[0])
    command_sign = 1.0 if dy * 0.08 >= 0 else -1.0
    w = np.diff(yw) / np.maximum(np.diff(ts), 1e-6)
    gmid = 0.5 * (gz[:-1] + gz[1:])
    corr = float(np.mean(gmid * w))
    damp_align = 1.0 if corr >= 0 else -1.0
    return dict(bias_rad=0.08, yaw_change_rad=dy, yaw_change_deg=math.degrees(dy), fell=row["fell"],
                command_sign=command_sign, gyro_yaw_correlation=corr, damp_align=damp_align,
                note="Nominal unrandomized trial. command_sign makes +hip-yaw command increase yaw. damp_align makes gyro[2] share the sign of yaw rate before damping is subtracted. This is not a heading-tracking result.")

def verify_baseline(x):
    """Bit-check the new rollout against walk_search.evaluate on flat ground, no overlays."""
    checks = []
    for seed, rand in ((5000, True), (0, False), (16058, True)):
        a = W.evaluate((np.array(x), seed, rand, 10.0))
        b = rollout(dict(x=[float(v) for v in x], seed=seed, rand=rand, T=10.0))
        ok = abs(a["dx"] - b["dx"]) < 1e-6 and abs(a["dy"] - b["dy"]) < 1e-6 and (bool(a["fell"]) == (b["fell"] is not None))
        checks.append(dict(seed=seed, rand=rand, ok=bool(ok), dx_eval=a["dx"], dx_rollout=b["dx"], fell_eval=a["fell"], fell_rollout=b["fell"]))
        if not ok:
            raise SystemExit("rollout diverged from evaluate: " + json.dumps(checks[-1], default=str))
    return checks

def save(name, obj):
    path = os.path.join(OUTDIR, name)
    json.dump(obj, open(path, "w"), indent=1, default=float)
    print("wrote", path, flush=True)
    return path

def main():
    t_all = time.time()
    check_locks()
    x = np.load(params_path(""))
    print("verify rollout vs evaluate", flush=True)
    checks = verify_baseline(x)
    print("calibrate heading sign", flush=True)
    cal = calibrate(x)
    global SIGN, DAMP
    SIGN, DAMP = cal["command_sign"], cal["damp_align"]
    print("calibration", {k: cal[k] for k in ("yaw_change_deg", "command_sign", "damp_align", "fell")}, flush=True)
    report = dict(quick=QUICK, calibration=cal, baseline_rollout_matches_evaluate=checks,
                  randomization="mass +-10%, friction 0.6-1.0, armature/damping +-30%, latency 0-5 steps of 2 ms, backlash 0.4 deg; same functions as walk_search.evaluate",
                  fall="|roll| or |pitch| > 45 deg, or trunk COM height < 0.6 of the settled height; episode.py unchanged",
                  current_proxy="Recorder.current: datasheet idle-to-stall map from |torque|. Not measured current, not a battery.",
                  thermal="no calibrated thermal resistance, temperature, or battery runtime. None is reported.",
                  gains_predeclared=HEADING_GAINS, turn_deg=TURN_DEG, turn_window_s=TURN_WINDOW,
                  load_scales_predeclared=[n for n, _ in LOAD_SCALES])

    # --- heading tune on +20 deg ---
    gains = HEADING_GAINS if not QUICK else HEADING_GAINS[:2]
    hs, hn, _ = n_of("heading_tune")
    tune_rows = []
    for kp, kd in gains:
        rows = run_pool(make_jobs(x, hs, hn, heading=heading_spec(TURN_DEG, kp, kd)))
        ag = aggregate(rows)
        tune_rows.append(dict(kp=kp, kd=kd, succ=ag["succ"], n=ag["n"], fell=ag["fell"],
                              speed_mps=ag["speed_mps"], heading_err_rms_deg=ag["heading_err_rms_deg"],
                              heading_err_final_deg=ag["heading_err_final_deg"],
                              straight_crosstrack_rms_m=ag["straight_crosstrack_rms_m"],
                              yaw_command_at_limit_fraction=ag["yaw_command_at_limit_fraction"],
                              main_rms=ag["main_rms"], main_sat=ag["main_sat"], current_proxy_A=ag["current_proxy_A"]))
        print("heading tune", tune_rows[-1]["kp"], tune_rows[-1]["succ"], tune_rows[-1]["heading_err_rms_deg"], flush=True)
    chosen, eligible = select_heading(tune_rows)
    report["heading_tune"] = dict(seeds=[hs, hs + hn], chosen=chosen, eligible=eligible, table=tune_rows,
                                  rule="max survival, then min heading RMS deg on survivors, then smaller kp; within 1 fall of best survival")

    def held(label, start, n, **kw):
        rows = run_pool(make_jobs(x, start, n, **kw))
        print(label, aggregate(rows)["succ"], "/", n, "speed", aggregate(rows)["speed_mps"], flush=True)
        return pack(label, rows)

    h0, hN, _ = n_of("heading_heldout")
    # full n for the primary +20 command; shorter paired variants use 40 (or 2 if quick)
    n_pair = min(hN, 40 if not QUICK else 2)
    report["heading_heldout_plus20"] = held("heading_feedback_plus20", h0, hN, heading=heading_spec(TURN_DEG, chosen["kp"], chosen["kd"]))
    report["heading_heldout_minus20"] = held("heading_feedback_minus20", h0, n_pair, heading=heading_spec(-TURN_DEG, chosen["kp"], chosen["kd"]))
    report["heading_heldout_plus10"] = held("heading_feedback_plus10", h0, n_pair, heading=heading_spec(10.0, chosen["kp"], chosen["kd"]))
    report["heading_hold"] = held("heading_feedback_hold0", h0, n_pair, heading=heading_spec(0.0, chosen["kp"], chosen["kd"], 0.0, 0.0))
    report["open_loop_same_seeds"] = held("open_loop_turn0", h0, n_pair)
    report["open_loop_bias_pos"] = held("open_loop_yaw_bias_+0.05", h0, n_pair, turn_bias=0.05)
    report["open_loop_bias_neg"] = held("open_loop_yaw_bias_-0.05", h0, n_pair, turn_bias=-0.05)
    report["heading_note"] = "plus20/minus20/plus10/hold are heading feedback. open_loop_yaw_bias is Gait.turn, a fixed hip-yaw offset with no heading error term. Straight crosstrack on a turn trial is not a tracking score; heading error is."

    # --- load screen ---
    ls, ln, _ = n_of("load_tune")
    load_table = []
    load_vecs = {}
    for name, scales in (LOAD_SCALES if not QUICK else LOAD_SCALES[:3]):
        y, did_clip = scaled(x, name, scales)
        load_vecs[name] = y
        rows = run_pool(make_jobs(y, ls, ln))
        ag = aggregate(rows)
        load_table.append(dict(name=name, clipped_to_search_box=did_clip, succ=ag["succ"], n=ag["n"], fell=ag["fell"],
                               speed_mps=ag["speed_mps"], main_rms=ag["main_rms"], main_sat=ag["main_sat"],
                               main_peak_mean=ag["main_peak_mean"], leg_rms=ag["leg_rms"], current_proxy_A=ag["current_proxy_A"],
                               joints=ag["joints"]))
        print("load tune", name, ag["succ"], ag["main_rms"], ag["main_sat"], ag["speed_mps"], flush=True)
    accepted, rel_tune = select_load(load_table)
    report["load_tune"] = dict(seeds=[ls, ls + ln], table=[{k: v for k, v in r.items() if k != "joints"} for r in load_table],
                               accepted=None if accepted is None else accepted["name"],
                               reliable_tune=rel_tune["name"])
    z0, zN, _ = n_of("load_heldout")
    report["load_heldout_reliable"] = held("reliable_on_load_heldout", z0, zN)
    if accepted is not None:
        y = load_vecs[accepted["name"]]
        rows = run_pool(make_jobs(y, z0, zN))
        report["load_heldout_candidate"] = pack("candidate_on_load_heldout", rows, extra=dict(candidate=accepted["name"]))
        np.save(os.path.join(OUTDIR, "load_screen_candidate.npy"), y)
        report["load_candidate_file"] = "results/load_screen_candidate.npy"
        report["load_candidate_promoted"] = False
    else:
        report["load_heldout_candidate"] = None
        report["load_decision"] = "No predeclared perturbation met the tune gate. params/reliable.npy is unchanged. fast_f05 was not re-tuned; the handoff already shows it misses 199/200 on fresh 16000 and 19000."

    f0, fN, _ = n_of("fresh_flat")
    report["fresh_flat_reliable"] = held("reliable_fresh_flat", f0, fN)

    # published 19000 block, reproduction only, via the original evaluator
    if not QUICK:
        print("reproduce reliable 19000-19199", flush=True)
        with mp.Pool(4) as pool:
            R = W.batch([x] * 200, range(19000, 19200), True, pool, T=10.0)
        fell = [19000 + i for i, r in enumerate(R) if r["fell"]]
        spd = float(np.mean([r["dx"] / 10 for r in R if not r["fell"]] or [0]))
        report["historical_reliable_19000"] = dict(succ=200 - len(fell), fell=fell, speed=spd, evaluator="walk_search.evaluate", role="reproduction of a burned block, not a fresh set")
        print("19000", report["historical_reliable_19000"], flush=True)

    # paired load definition check on the published 20-seed window, not used for selection
    rows20 = run_pool(make_jobs(x, 5000, 2 if QUICK else 20))
    report["historical_load_window_5000_5019"] = pack("reliable_5000_window", rows20, extra=dict(
        role="reproduction of the published paired-load window; not a tune set",
        published_reference=dict(main_rms_Nm=0.9981, main_saturation=0.06607, speed_mps=0.2125, seeds="5000-5019")))

    # --- stop / start, isolated, flat ---
    s0, sN, _ = n_of("stop_test")
    report["stop_phase"] = held("phase_aware_stop", s0, sN, T=9.0, amp=AMP_PHASE)
    report["stop_abrupt"] = held("abrupt_stop", s0, sN, T=9.0, amp=AMP_ABRUPT)
    # schedule geometry from one nominal episode
    nom = rollout(dict(x=[float(v) for v in x], seed=0, rand=False, T=9.0, amp=AMP_PHASE, keep_trace=True))
    report["stop_schedule_nominal"] = (nom.get("stop") or {}).get("schedule")
    report["stop_nominal_trace"] = [dict(t=round(p["t"], 3), x=round(p["x"], 4), amp=p["amp"], yaw=round(p["yaw"], 4)) for p in nom["trace"][::5]]

    # --- terrain, labelled, straight gait, no heading overlay ---
    t0, tN, _ = n_of("terrain_test")
    report["terrain_catalogue"] = {k: {kk: vv for kk, vv in meta.items() if kk != "geoms"} | ({"n_geoms": len(meta.get("geoms", []))} ) for k, meta in TF.catalogue().items()}
    for label in ("flat", "gentle_bumps_h4mm", "gentle_ridge_h6mm", "grade_2deg"):
        report["terrain_" + label] = held("terrain_" + label, t0, tN, terrain=label)

    # --- walking head/arm ---
    a0, aN, _ = n_of("headarm_test")
    report["headarm_off"] = held("walk_headarm_off", a0, aN, headarm="none")
    report["headarm_mild"] = held("walk_headarm_mild", a0, aN, headarm="mild")
    report["headarm_standing_script"] = held("walk_headarm_standing_script", a0, aN, headarm="standing_script")

    report["seconds"] = round(time.time() - t_all, 1)
    report["reserved_unused"] = list(FRESH["reserved_unused"])
    report["burned_blocks"] = "5000,6000,7000,8000,9000,11000-15000,16000,17000,18000,19000 (200-seed blocks). Not used to choose gains or load perturbations."
    save("capabilities.json", report)
    # plot traces: nominal heading and a bump snapshot are separate small files
    plot_jobs(x, chosen)
    print("CAPABILITIES_DONE", report["seconds"], flush=True)

def plot_jobs(x, chosen):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plot = os.path.join(OUTDIR, "plots")
    os.makedirs(plot, exist_ok=True)
    href = heading_spec(TURN_DEG, chosen["kp"], chosen["kd"])
    turn = rollout(dict(x=[float(v) for v in x], seed=0, rand=False, T=10.0, heading=href, keep_trace=True,
                        command_sign=SIGN, damp_align=DAMP))
    tr = turn["trace"]
    ts = [p["t"] for p in tr]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot(ts, [math.degrees(p["yaw"]) for p in tr], label="yaw")
    ax.plot(ts, [math.degrees(p["ycmd"]) for p in tr], label="commanded heading", linestyle="--")
    ax.set_xlabel("time (s)"); ax.set_ylabel("yaw (deg)"); ax.legend(); ax.set_title("Nominal heading feedback, +20 deg, no randomization")
    fig.tight_layout(); fig.savefig(os.path.join(plot, "heading_nominal.png"), dpi=120); plt.close()
    phase = rollout(dict(x=[float(v) for v in x], seed=0, rand=False, T=9.0, amp=AMP_PHASE, keep_trace=True))
    abr = rollout(dict(x=[float(v) for v in x], seed=0, rand=False, T=9.0, amp=AMP_ABRUPT, keep_trace=True))
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.plot([p["t"] for p in phase["trace"]], [p["amp"] for p in phase["trace"]], label="phase-aware")
    ax.plot([p["t"] for p in abr["trace"]], [p["amp"] for p in abr["trace"]], label="abrupt cut", linestyle="--")
    ax.set_xlabel("time (s)"); ax.set_ylabel("gait amplitude"); ax.legend(); ax.set_title("Isolated stop/start amplitude, nominal")
    fig.tight_layout(); fig.savefig(os.path.join(plot, "stop_amplitude.png"), dpi=120); plt.close()
    # speed from x
    def spd(trace):
        t = np.array([p["t"] for p in trace]); x_ = np.array([p["x"] for p in trace])
        return 0.5 * (t[:-1] + t[1:]), np.diff(x_) / np.maximum(np.diff(t), 1e-6)
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for tr_, lab in ((phase["trace"], "phase-aware"), (abr["trace"], "abrupt")):
        tm, v = spd(tr_); ax.plot(tm, v, label=lab)
    ax.set_xlabel("time (s)"); ax.set_ylabel("forward speed (m/s)"); ax.legend(); ax.set_title("Nominal forward speed during stop")
    fig.tight_layout(); fig.savefig(os.path.join(plot, "stop_speed.png"), dpi=120); plt.close()
    print("plots", plot, flush=True)

if __name__ == "__main__":
    SIGN, DAMP = 1.0, 1.0
    main()
