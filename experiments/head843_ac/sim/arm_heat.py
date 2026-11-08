"""(g) Arm-wave heat test: continuous waving while standing (balance controller on), 30 s per case.
Right arm raised (shoulder 150 deg), elbow waves +-40 deg; left arm swings +-40 deg at the shoulder. Per arm joint: peak / RMS torque vs the
servo's rated continuous torque, and steady copper loss P = (tau_rms / Kt)^2 * R (winding heat; excludes idle electronics).
Usage: python arm_heat.py v3   -> out/arm_heat_v3.json (needs out/results_v3.json from run_tests.py)"""
import sys, os, json, math, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from simlib import *
from episode import run
V = sys.argv[1]
XML = model_path(V)
m = mujoco.MjModel.from_xml_path(XML); d = mujoco.MjData(m); sv = Servo(m); N = sv.names; ix = sv.idx
q0 = stance(N, 0.30, lean=BASE_LEAN[V])
res_f = os.environ.get("TWIGLET_RESULTS", os.path.join(OUT, f"results_{V}.json"))   # run run_tests.py first (balance gains)
g = json.load(open(res_f))["b_balance_gains(kp_ankle,kd_ankle,kp_hip,kp_roll,kd_roll)"]
def bal(t, rpy, gy):
    kpa, kda, kph, kr, krd = g; qq = q0.copy(); a = kpa * rpy[1] + kda * gy[1]; h = kph * rpy[1]
    for s, sg in (("left", 1), ("right", -1)):
        qq[ix[f"{s}_ankle"]] += a; qq[ix[f"{s}_hip_pitch"]] += sg * h; qq[ix[f"{s}_hip_roll"]] += -(kr * rpy[0] + krd * gy[0])
    return qq
out = {"variant": V, "xml": os.path.relpath(XML, HERE)}
for f in (0.5, 0.8, 1.5):
    def pol(t, rpy, gy, f=f):
        qq = bal(t, rpy, gy); a = min(1.0, t / 2.0); sn = math.sin(2 * math.pi * f * t)
        # identical commands on v2 and v3, inside the v3 collision-free set: right arm forward ~horizontal waving +-20 deg at the shoulder
        # and +-10 deg at the elbow; left arm swinging 5..55 deg
        qq[ix["shoulder_R"]] = math.radians(8 + 57 * a + 20 * a * sn); qq[ix["elbow_R"]] = math.radians(20 + 10 * a * sn)
        qq[ix["shoulder_L"]] = math.radians(30 + 25 * a * sn); qq[ix["elbow_L"]] = math.radians(22 + 20 * a * max(0, sn))
        qq[ix["gripper_R"]] = math.radians(30); qq[ix["gripper_L"]] = math.radians(30)
        return qq
    reset(m, d, q0); rec = Recorder(N, sv.stall); tr = {"t": [], "q": []}
    info = run(m, d, sv, pol, 30.0, V, rec=rec, on_step=lambda t, dd: (tr["t"].append(t), tr["q"].append([dd.qpos[sv.qadr[ix[j]]] for j in ("shoulder_R", "elbow_R", "shoulder_L")])))
    T = np.array(rec.tau); tt = np.array(rec.t); sel = tt > 3.0
    q = np.array(tr["q"]); tq = np.array(tr["t"]); qs = q[tq > 3.0]
    rows = {}
    for j in ("shoulder_R", "elbow_R", "gripper_R", "shoulder_L", "elbow_L"):
        i = ix[j]; s32 = bool(sv.s32[i]); P = S32 if s32 else S15
        tau = T[sel, i]; rms = float(np.sqrt((tau ** 2).mean())); pk = float(tau.max())
        rows[j] = dict(servo="STS3032" if s32 else "STS3215", peak_Nm=round(pk, 3), rms_Nm=round(rms, 3), rated_Nm=P["rated"], rms_over_rated=round(rms / P["rated"], 2),
                       peak_over_stall=round(pk / P["stall"], 2), copper_loss_W=round((rms / P["kt"]) ** 2 * P["r"], 3),
                       time_at_stall_pct=round(100 * float((tau >= 0.98 * P["stall"]).mean()), 1))
    amp = {"shoulder_R_pp_deg": round(float(np.degrees(qs[:, 0].max() - qs[:, 0].min())), 1), "elbow_R_pp_deg": round(float(np.degrees(qs[:, 1].max() - qs[:, 1].min())), 1),
           "shoulder_L_pp_deg": round(float(np.degrees(qs[:, 2].max() - qs[:, 2].min())), 1), "commanded_pp_deg": {"shoulder_R": 40.0, "elbow_R": 20.0, "shoulder_L": 50.0}}
    out[f"wave_{f}Hz"] = dict(fell=info["fell"], joints=rows, tracking=amp)
    print(V, f, info["fell"], {k: (v["rms_Nm"], v["rms_over_rated"], v["copper_loss_W"]) for k, v in rows.items()}, amp, flush=True)
json.dump(out, open(os.path.join(OUT, f"arm_heat_{V}.json"), "w"), indent=1)
