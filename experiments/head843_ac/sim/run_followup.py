"""Follow-up trials that do not replace the predeclared capability results.

- grade_2deg is re-run after the ramp was corrected so its top front edge is on the floor.
  The curb version is not reported.
- Stop variants with the original time-ramp start separate the stop from the phase-aware start hold.
- Open-loop path metrics on heading seeds 26000-26039 (same seeds as the hold comparison).
- mild_posthoc head/arm on 29000-29019, chosen after 25000-25039 failed. 29020-29199 stay unused.
- Dynamic clearance on recorded joint trajectories.
"""
import os, sys, json, math, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault("TWIGLET_XML", os.path.join(HERE, "models", "twiglet_v3_v335ac.xml"))
os.environ.setdefault("TWIGLET_PARAMS", os.path.join(ROOT, "params", "reliable.npy"))
os.environ.setdefault("TWIGLET_SCENE", os.path.join(ROOT, "geometry", "scene_v335ac.npz"))
sys.argv = [sys.argv[0], "v3"]
from manoeuvre import rollout, aggregate
from simlib import params_path, Video, load, Servo, Gait, stance, reset, BASE_LEAN, body_rpy
import mujoco
import terrain_fixtures as TF

SIGN, DAMP = -1.0, 1.0
X = [float(v) for v in np.load(params_path(""))]
OUT = os.path.join(ROOT, "results")

def jobs(start, n, **kw):
    base = dict(x=X, rand=True, T=10.0, command_sign=SIGN, damp_align=DAMP)
    base.update(kw)
    return [dict(base, seed=start + i) for i in range(n)]

def run(js):
    with mp.Pool(4) as pool:
        return pool.map(rollout, js, chunksize=2)

def pack(name, rows, extra=None):
    body = dict(name=name, aggregate=aggregate(rows), seeds=[
        dict(seed=r["seed"], fell=r["fell"], speed=r["speed"],
             straight_crosstrack_rms_m=r.get("straight_crosstrack_rms_m"),
             yaw_change_deg=None if r.get("yaw_change") is None else round(math.degrees(r["yaw_change"]), 3),
             speed_before_stop=(r.get("stop") or {}).get("speed_before_stop"),
             speed_after_settle=(r.get("stop") or {}).get("speed_after_settle"),
             disp_after_stop_m=(r.get("stop") or {}).get("disp_after_stop_m"),
             tracking_rms=r.get("tracking_rms"),
             main_rms=None if not r.get("load") else r["load"].get("main_rms"),
             main_sat=None if not r.get("load") else r["load"].get("main_sat"))
        for r in rows])
    if extra:
        body.update(extra)
    ag = body["aggregate"]
    print(name, f"{ag['succ']}/{ag['n']}", "speed", ag.get("speed_mps"),
          "straight", ag.get("straight_crosstrack_rms_m"), "yaw", ag.get("yaw_change_deg"),
          "stop_after", ag.get("speed_after_settle"), "before", ag.get("speed_before_stop"), flush=True)
    return body

def render_frames():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plot = os.path.join(OUT, "plots")
    os.makedirs(plot, exist_ok=True)
    from episode import run as ep_run, gyro
    cases = [
        ("flat_walk", "flat", None, 3.0),
        ("bumps", "gentle_bumps_h4mm", None, 2.2),
        ("grade", "grade_2deg", None, 4.0),
        ("head_mild_posthoc", "flat", "mild_posthoc", 4.0),
    ]
    for name, terrain, head, T in cases:
        if terrain == "flat":
            m, d = load("v3")
        else:
            m, _ = TF.compile_model(terrain)
            d = mujoco.MjData(m)
        sv = Servo(m)
        p = dict(zip(__import__("walk_search").KEYS, X)); p["ramp"] = 1.0
        g = Gait(sv.names, p, "v3")
        q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN["v3"])
        reset(m, d, q0)
        from manoeuvre import apply_headarm
        def pol(t, rpy, gy, head=head):
            q = g(t, rpy, gy, q0)
            return apply_headarm(q, sv.names, t, head)
        ep_run(m, d, sv, pol, T, "v3")
        r = mujoco.Renderer(m, 420, 640)
        cam = mujoco.MjvCamera(); cam.distance = 1.15; cam.azimuth = 135; cam.elevation = -18
        cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.15]
        r.update_scene(d, cam)
        plt.imsave(os.path.join(plot, f"frame_{name}.png"), r.render())
        print("frame", name, "x", round(float(d.qpos[0]), 3), flush=True)

def clearance():
    import clearance_dyn as C
    print("building clearance meshes", flush=True)
    t0 = time.time()
    ctx = C.build(os.environ["TWIGLET_SCENE"])
    print("mesh build", round(time.time() - t0, 1), "faces", ctx["face_counts"].get("head_assembly"), "priority", len(ctx["priority"]), flush=True)
    from simlib import model_path
    xml = os.environ["TWIGLET_XML"]
    if not os.path.isabs(xml):
        xml = model_path("v3")
    frame = C.frame_spotcheck(os.environ["TWIGLET_SCENE"], xml)
    print("frame", frame, flush=True)
    cap = json.load(open(os.path.join(OUT, "capabilities.json")))
    survivors = [r["seed"] for r in cap["headarm_mild"]["seeds"] if r["fell"] is None]
    trials = [("walk_nominal", dict(seed=0, rand=False, T=8.0, headarm="none"))]
    if survivors:
        trials.append(("walk_mild_survivor", dict(seed=survivors[0], rand=True, T=8.0, headarm="mild")))
    trials.append(("walk_mild_posthoc_nominal", dict(seed=0, rand=False, T=8.0, headarm="mild_posthoc")))
    out_trials = []
    for label, kw in trials:
        row = rollout(dict(x=X, command_sign=SIGN, damp_align=DAMP, trace_q=True, **kw))
        samples = [s["q"] for s in row["qtrace"]][::2]
        print(label, "fell", row["fell"], "samples", len(samples), flush=True)
        ev = C.evaluate_trajectory(ctx, samples, samples[0], label, hz=25.0)
        ev["sim_fell"] = row["fell"]
        ev["seed"] = kw["seed"]
        ev["randomized"] = kw["rand"]
        series = ev.pop("min_distance_series_mm")
        ev["series_len"] = len(series)
        ev["series_decimated"] = series[::2]
        out_trials.append(ev)
        print(label, "new", ev["new_contact_pair_count"], "min_mm", ev["min_distance_mm"], ev["min_distance_pair"], flush=True)
    rep = dict(
        geometry_claim="Does not verify locked F4/G3/D9 or wig v6b0. Those ids are not mesh names in scene_v335ac.npz.",
        scene_source=ctx["meta_source"],
        lock_name_hits=ctx["lock_name_hits"],
        head_part_names=ctx["part_names_head"],
        excluded_sim_visuals=ctx["excluded"],
        kinematic_neighbors=ctx["neighbors"],
        priority_pairs=ctx["priority"],
        decimation=ctx["how"],
        face_counts=ctx["face_counts"],
        frame_spotcheck_mm=frame,
        sampling="25 Hz simulated joint angles plus one linear joint-space midpoint. Not a continuous swept volume.",
        stance_exclusion="pairs already colliding on the first recorded pose are listed and are not counted as new.",
        trials=out_trials,
    )
    json.dump(rep, open(os.path.join(OUT, "clearance_dynamic.json"), "w"), indent=1, default=float)
    print("clearance wrote", flush=True)
    return rep

def main():
    print("grade placement", TF.grade_placement(), flush=True)
    nom = rollout(dict(x=X, seed=0, rand=False, T=10.0, terrain="grade_2deg"))
    print("nominal corrected grade", nom["fell"], round(nom["dx"], 3), flush=True)
    rep = {}
    rep["grade_2deg_corrected"] = pack("grade_2deg_top_flush", run(jobs(24000, 40, terrain="grade_2deg")),
                                      extra=dict(placement=TF.grade_placement(),
                                                 note="Replaces the curb-like first grade. Same seeds 24000-24039. Bumps and ridge were not re-run."))
    rep["stop_baseline_start_phase"] = pack("baseline_start_phase_stop", run(jobs(
        23000, 20, T=9.0, amp=dict(kind="baseline_then_phase_stop", t_stop=6.0, ramp_cycles=1.0))))
    rep["stop_baseline_start_abrupt"] = pack("baseline_start_abrupt_stop", run(jobs(
        23000, 20, T=9.0, amp=dict(kind="baseline_then_abrupt_stop", t_stop=6.0, ramp_cycles=1.0))))
    rep["open_loop_path"] = pack("open_loop_path_26000", run(jobs(26000, 40, measure_path=True)),
                                extra=dict(note="Same seeds as heading_hold. No heading feedback. straight_crosstrack is vs the initial heading, which is the comparison for heading_hold, not for a commanded turn."))
    rep["headarm_mild_posthoc"] = pack("mild_posthoc_29000", run(jobs(29000, 20, headarm="mild_posthoc")),
                                      extra=dict(seeds_note="29000-29019 chosen after seeing 25000-25039. 29020-29199 unused. Not a predeclared test."))
    json.dump(rep, open(os.path.join(OUT, "followup.json"), "w"), indent=1, default=float)
    print("followup sims done", flush=True)
    render_frames()
    clearance()

if __name__ == "__main__":
    main()
