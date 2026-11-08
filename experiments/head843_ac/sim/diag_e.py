"""diag (rev C): head+arm test (e) only, with balance gains either searched as in run_tests.py or fixed from argv.
Usage: python diag_e.py v3 [g1,g2,g3,g4,g5] -> prints min margin, when, feet in contact, COM; writes diag_e_<tag>.json"""

import sys, os, json, math, itertools, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from simlib import *
from episode import run, soft_clip, gyro
V = sys.argv[1]; VIDEO = "--video" in sys.argv
CROUCH = {"v2": 0.30, "stock": 0.63, "opt1": 0.63, "v3": 0.30}[V]          # stock: Open Duck Playground home keyframe crouch (hip -0.63, knee ~1.37)
res = {"variant": V, "crouch_rad": CROUCH}
m = mujoco.MjModel.from_xml_path(model_path(V)); d = mujoco.MjData(m); sv = Servo(m); N = sv.names; ix = sv.idx
q0 = stance(N, CROUCH, lean=BASE_LEAN[V])
res["total_mass_kg"] = round(float(m.body_mass.sum()), 3)

# ---------------- (b) push recovery
def bal_policy(gains, q=q0):
    kpa, kda, kph, kr, krd = gains
    def pol(t, rpy, g):
        qq = q.copy(); a = kpa * rpy[1] + kda * g[1]; h = kph * rpy[1]
        for s, sg in (("left", 1), ("right", -1)):
            qq[ix[f"{s}_ankle"]] += a; qq[ix[f"{s}_hip_pitch"]] += sg * h
            qq[ix[f"{s}_hip_roll"]] += -(kr * rpy[0] + krd * g[0])
        return qq
    return pol
def survives(pol, fx, fy, dur=0.1):
    reset(m, d, q0); run(m, d, sv, pol, 0.5, V)
    info = run(m, d, sv, pol, 2.5, V, push=(0.0, dur, fx, fy)); return info["fell"] is None
def max_push(pol, direction, hi=60.0):
    lo_, hi_ = 0.0, hi
    ex, ey = direction
    if survives(pol, hi * ex, hi * ey): return hi * 0.1
    for _ in range(8):
        mid = (lo_ + hi_) / 2
        if survives(pol, mid * ex, mid * ey): lo_ = mid
        else: hi_ = mid
    return round(lo_ * 0.1, 3)     # N.s (0.1 s pulse)
DIRS = {"forward": (1, 0), "backward": (-1, 0), "left": (0, 1), "right": (0, -1)}
GA = [a for a in sys.argv[2:] if "," in a]
if GA: best = (0, tuple(float(x) for x in GA[0].split(",")))
else:
    none = bal_policy((0, 0, 0, 0, 0))
    res["b_push_no_controller_Ns"] = {k: max_push(none, v) for k, v in DIRS.items()}
    print("b none", res["b_push_no_controller_Ns"])
    # small random search for balance gains (sign-agnostic), objective = sum of the 4 max pushes
    rng = np.random.default_rng(0); best = (sum(res["b_push_no_controller_Ns"].values()), (0, 0, 0, 0, 0)); tried = []
    for it in range(28):
        g = tuple(np.round(rng.uniform([-2, -0.2, -1.0, -2, -0.2], [2, 0.2, 1.0, 2, 0.2]), 3))
        if it >= 14: g = tuple(np.round(np.array(best[1]) + rng.normal(0, [0.4, 0.04, 0.2, 0.4, 0.04]), 3))
        pol = bal_policy(g); sc = sum(max_push(pol, v) for v in DIRS.values()); tried.append((sc, g))
        if sc > best[0]: best = (sc, g)
    res["b_balance_gains(kp_ankle,kd_ankle,kp_hip,kp_roll,kd_roll)"] = [float(x) for x in best[1]]
bal = bal_policy(best[1]); print("gains", best[1], flush=True)
# ---------------- (e) head motions + arm waving / gripper while standing (balance controller on)
def head_arm(t, rpy, g):
    qq = bal(t, rpy, g)
    seg = t % 12.0
    if "head_yaw" in ix:
        if "neck_pitch" in ix:
            qq[ix["neck_pitch"]] = math.radians(65) * max(0, math.sin(2 * math.pi * seg / 6)) - math.radians(20) * max(0, -math.sin(2 * math.pi * seg / 6))
            qq[ix["head_pitch"]] = math.radians(10) * math.sin(2 * math.pi * t / 3.0)
        else:   # v3.5: no neck-pitch joint -> the head-pitch servo does the full nod (soft-clipped to -38..+4)
            qq[ix["head_pitch"]] = -math.radians(34) * max(0, math.sin(2 * math.pi * seg / 6)) + math.radians(4) * max(0, -math.sin(2 * math.pi * seg / 6))
        qq[ix["head_yaw"]] = math.radians(90) * math.sin(2 * math.pi * t / 4.0) * (1 if seg > 6 else 0.5)
        qq[ix["head_roll"]] = math.radians(15) * math.sin(2 * math.pi * t / 2.5)
    if "shoulder_L" in ix and V == "v3":     # v3: head sits on the shoulders -> no overhead wave; wave with the arm forward (collision-free set)
        a = min(1, t / 2)
        qq[ix["shoulder_R"]] = math.radians(8 + 62 * a + 10 * a * math.sin(2 * math.pi * 1.5 * t)); qq[ix["elbow_R"]] = math.radians(20 + 8 * math.sin(2 * math.pi * 1.5 * t))
        qq[ix["gripper_R"]] = math.radians(30 + 30 * math.sin(2 * math.pi * 1.0 * t))
        qq[ix["shoulder_L"]] = math.radians(30 + 25 * math.sin(2 * math.pi * 0.5 * t)); qq[ix["elbow_L"]] = math.radians(22 + 20 * max(0, math.sin(2 * math.pi * 0.5 * t)))
        qq[ix["gripper_L"]] = math.radians(30 + 30 * math.sin(2 * math.pi * 0.7 * t))
    elif "shoulder_L" in ix:
        qq[ix["shoulder_R"]] = math.radians(8 + 142 * min(1, t / 2))
        qq[ix["elbow_R"]] = math.radians(70 + 40 * math.sin(2 * math.pi * 1.5 * t))
        qq[ix["gripper_R"]] = math.radians(30 + 30 * math.sin(2 * math.pi * 1.0 * t))
        qq[ix["shoulder_L"]] = math.radians(8 + 40 * math.sin(2 * math.pi * 0.5 * t)); qq[ix["elbow_L"]] = math.radians(22 + 50 * max(0, math.sin(2 * math.pi * 0.5 * t)))
        qq[ix["gripper_L"]] = math.radians(30 + 30 * math.sin(2 * math.pi * 0.7 * t))
    return qq
reset(m, d, q0); rec = Recorder(N, sv.stall); margins = []; DG = []
def diag_rec(t, dd):
    mg, com = support_margin(m, dd); margins.append(mg)
    feet = sorted({m.geom(i).name for k in range(dd.ncon) for i in (dd.contact[k].geom1, dd.contact[k].geom2) if m.geom(i).name.startswith("sole_")})
    DG.append((round(t, 3), round(float(mg), 1) if mg == mg else None, len(feet), [round(float(x) * 1000, 1) for x in com]))
vid = Video(m, dist=1.0, az=140, el=-10, track=False) if VIDEO else None
if vid: vid.cam.lookat[:] = [0, 0, 0.2]
info = run(m, d, sv, head_arm, 12.0, V, rec=rec, video=vid, on_step=lambda t, dd: diag_rec(t, dd) if int(t * 200) % 10 == 0 else None)
if vid: vid.save(os.path.join(OUT, f"head_arms_{V}.gif"), fps=20)
st = rec.stats()
res["e_head_arm_motion"] = dict(fell=info["fell"], min_support_margin_mm=round(float(np.nanmin(margins)), 1),
                                torque={n: st[n] for n in N if any(k in n for k in ("neck", "head", "shoulder", "elbow", "gripper", "ankle", "hip_pitch"))})
print("e", info["fell"], round(float(np.nanmin(margins)), 1), {n: st[n]["peak"] for n in N if "neck" in n or "shoulder" in n or "head" in n})
import numpy as _np
i = int(_np.nanargmin(margins)); print("min margin", round(float(_np.nanmin(margins)), 1), "at", DG[i], flush=True)
both = [x for x in DG if x[2] >= 2 and x[1] is not None]; print("min margin with >=2 sole geoms in contact", min(x[1] for x in both) if both else None)
low = sorted([x for x in DG if x[1] is not None], key=lambda x: x[1])[:8]; print("lowest samples", low)
tag = "_".join(sys.argv[1:]).replace(",", "_")[:60]
json.dump(dict(gains=list(best[1]), min_margin=float(_np.nanmin(margins)), series=DG), open(os.path.join(OUT, f"diag_e_{tag}.json"), "w"))
