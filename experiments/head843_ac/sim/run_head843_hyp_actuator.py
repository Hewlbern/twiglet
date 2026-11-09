"""Hypothetical actuator screen. Not a qualification and not a hardware result.

The model file is sim/models/twiglet_v3_hyp_torque29.xml, a copy. Hip pitch, knee,
and ankle ctrlrange are -2.9 to 2.9 N·m. Hip yaw motors stay at 1.91. The canonical
XML is not opened for writing. A second screen also lets the hip-yaw command reach
±15 deg. The stock soft clip is ±7 deg because the hip bracket meets the neck
cradle, so that second screen is a clearance what-if, not a servo that exists.
"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import episode
import run_head843_earlyrate as E
import run_head843_heading as HH
import run_head843_shortbal_val as V
import run_head843_manoeuvre_b_val as B

HYP = os.path.join(HERE, "models", "twiglet_v3_hyp_torque29.xml")
CANON = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
SL = [{"t0": 2, "t1": 7, "yaw_deg": 20}, {"t0": 7, "t1": 12, "yaw_deg": 0},
      {"t0": 12, "t1": 17, "yaw_deg": -20}, {"t0": 17, "t1": 22, "yaw_deg": 0}]

def heading(**k):
    h = dict(k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True, yaw_alloc="right_stance_onset",
             step_guard=True, stance_roll_support=True, neg_onset_gate=True)
    h.update(k)
    return h

def run(seeds, T, xml, heading_spec=None, stride=None):
    js = E.jobs("early", z, seeds, HH.NOM, T)
    for j in js:
        j["xml"] = xml
        j["keep_trace"] = True
        if heading_spec:
            j["heading"] = heading_spec
        if stride:
            j["stride_scale"] = stride
    return V.Y.run_jobs(js)

def show_straight(label, rows):
    for r in rows:
        print(f"  {label} straight {r['seed']} fell={r['fell']} yaw={math.degrees(r['yaw']):+.2f} dx={r['dx']:.3f}", flush=True)

def show_slew(label, rows, T, t0, t1, deg):
    for r in rows:
        ok, info = B.passed(dict(kind="slew", T=T, t0=t0, t1=t1, delta_deg=deg), r)
        print(f"  {label} slew {r['seed']} {deg:+} ok={ok} fell={r['fell']} {info}", flush=True)

def main():
    if not os.path.exists(HYP):
        raise SystemExit("missing hypothetical xml")
    # Canonical motors must still be 1.91. The copy is the only 2.9 file.
    canon = open(CANON).read()
    if 'ctrlrange="-2.9 2.9"' in canon:
        raise SystemExit("canonical xml was modified")
    out = {"label": "hypothetical_actuator_not_a_hardware_result", "torque_Nm": 2.9,
           "joints": ["hip_pitch", "knee", "ankle"], "hip_yaw_motor_Nm": 1.91}
    print("TORQUE ONLY", flush=True)
    rows = run([270260, 214000, 214001] + list(range(297000, 297008)), 10, HYP)
    show_straight("torque29", rows)
    out["straight"] = [dict(seed=int(r["seed"]), fell=None if r["fell"] is None else round(float(r["fell"]), 3),
                            yaw_deg=round(math.degrees(r["yaw"]), 2)) for r in rows]
    rows = run([271181, 271339, 284200], 24, HYP, heading(kind="route", segments=SL))
    out["slalom"] = []
    for r in rows:
        ok, info = B.slalom_ok(r)
        print(f"  torque29 slalom {r['seed']} ok={ok} fell={r['fell']} {info}", flush=True)
        out["slalom"].append(dict(seed=int(r["seed"]), task=bool(ok), fell=None if r["fell"] is None else round(float(r["fell"]), 3), **info))
    rows = run([270924, 270215], 12.0, HYP, heading(kind="feedback", t0=2.5, t1=8.5, delta=math.radians(-90),
                                                    kp=0.6, kd=0.02, ki=0.0, limit=0.07))
    show_slew("torque29 15dps", rows, 12.0, 2.5, 8.5, -90)
    out["m90_15"] = []
    for r in rows:
        ok, info = B.passed(dict(kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=-90), r)
        out["m90_15"].append(dict(seed=int(r["seed"]), task=bool(ok), fell=None if r["fell"] is None else round(float(r["fell"]), 3), **info))
    rows = run([269737, 269829], 12.0, HYP, heading(kind="feedback", t0=2.5, t1=8.5, delta=math.radians(90),
                                                    kp=0.6, kd=0.02, ki=0.0, limit=0.07))
    show_slew("torque29 15dps", rows, 12.0, 2.5, 8.5, 90)
    out["p90_15"] = []
    for r in rows:
        ok, info = B.passed(dict(kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=90), r)
        out["p90_15"].append(dict(seed=int(r["seed"]), task=bool(ok), fell=None if r["fell"] is None else round(float(r["fell"]), 3), **info))

    print("TORQUE AND WIDER HIP-YAW COMMAND", flush=True)
    # Stock soft clip is ±7 deg. This what-if lets the command reach ±15 deg.
    episode.SOFT["v3"]["left_hip_yaw"] = (-math.radians(15), math.radians(15))
    episode.SOFT["v3"]["right_hip_yaw"] = (-math.radians(15), math.radians(15))
    cap = math.radians(15)
    h15 = dict(hyp_yaw_cap=cap)
    rows = run([270260, 214000], 10, HYP)
    show_straight("wide", rows)
    out["wide_straight"] = [dict(seed=int(r["seed"]), fell=None if r["fell"] is None else round(float(r["fell"]), 3),
                                 yaw_deg=round(math.degrees(r["yaw"]), 2)) for r in rows]
    fresh = list(range(297008, 297016))
    rows = run([270924, 270215] + fresh, 12.0, HYP, heading(kind="feedback", t0=2.5, t1=8.5,
                delta=math.radians(-90), kp=0.6, kd=0.02, ki=0.0, limit=0.07, **h15))
    show_slew("wide 15dps", rows, 12.0, 2.5, 8.5, -90)
    out["wide_m90_15"] = []
    for r in rows:
        ok, info = B.passed(dict(kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=-90), r)
        out["wide_m90_15"].append(dict(seed=int(r["seed"]), task=bool(ok), fell=None if r["fell"] is None else round(float(r["fell"]), 3), **info))
    rows = run([269737, 269829] + list(range(297016, 297024)), 12.0, HYP, heading(
        kind="feedback", t0=2.5, t1=8.5, delta=math.radians(90), kp=0.6, kd=0.02, ki=0.0, limit=0.07, **h15))
    show_slew("wide 15dps", rows, 12.0, 2.5, 8.5, 90)
    out["wide_p90_15"] = []
    for r in rows:
        ok, info = B.passed(dict(kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=90), r)
        out["wide_p90_15"].append(dict(seed=int(r["seed"]), task=bool(ok), fell=None if r["fell"] is None else round(float(r["fell"]), 3), **info))
    json.dump(out, open(os.path.join(ROOT, "results", "head843_hyp_actuator_screen.json"), "w"), indent=1)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
