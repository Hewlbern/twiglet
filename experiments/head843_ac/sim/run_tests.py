"""Tests (a) standing/COM margin, (b) push recovery, (c) weight shift, (e) head + arm motions, for 'v2' and 'stock'.
Usage: python run_tests.py v2|stock [--video]   -> results_<variant>.json, plots/videos in this folder."""
import sys, os, json, math, itertools, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from simlib import *
from episode import run, soft_clip, gyro
V = sys.argv[1]; VIDEO = "--video" in sys.argv
CROUCH = {"v2": 0.30, "stock": 0.63, "opt1": 0.63, "v3": 0.30}[V]          # stock: Open Duck Playground home keyframe crouch (hip -0.63, knee ~1.37)
res = {"variant": V, "crouch_rad": CROUCH}
m, d = load(V); sv = Servo(m); N = sv.names; ix = sv.idx
q0 = stance(N, CROUCH, lean=BASE_LEAN[V])
res["total_mass_kg"] = round(float(m.body_mass.sum()), 3)

# ---------------- (a) static standing
def stand_metrics(q, T=3.0):
    reset(m, d, q); rec = Recorder(N, sv.stall)
    info = run(m, d, sv, lambda t, r, g: q, T, V, rec=rec)
    mar, com = support_margin(m, d)
    # fore/aft and lateral margins to the support rectangle of both soles
    xs, ys = [], []
    for i in range(m.ngeom):
        if m.geom(i).name.startswith("sole_"):
            R = d.geom_xmat[i].reshape(3, 3); c = d.geom_xpos[i]; h = m.geom_size[i]
            for sx in (-1, 1):
                for sy in (-1, 1): p = c + R @ (h * [sx, sy, -1]); xs.append(p[0]); ys.append(p[1])
    st = rec.stats()
    return dict(fell=info["fell"], margin_min_mm=round(mar, 1), margin_front_mm=round((max(xs) - com[0]) * 1000, 1),
                margin_back_mm=round((com[0] - min(xs)) * 1000, 1), margin_side_mm=round(min(max(ys) - com[1], com[1] - min(ys)) * 1000, 1),
                support_width_mm=round((max(ys) - min(ys)) * 1000, 1), com_height_mm=round(float(d.subtree_com[1][2]) * 1000, 1),
                tilt_deg=[round(math.degrees(a), 2) for a in body_rpy(d)[:2]],
                static_torque_Nm={n: round(float(abs(d.ctrl[i])), 3) for i, n in enumerate(N) if abs(d.ctrl[i]) > 0.02},
                bus_current_A=round(rec.current(), 2),
                tipping_angle_side_deg=round(math.degrees(math.atan2(min(max(ys) - com[1], com[1] - min(ys)), d.subtree_com[1][2])), 1),
                tipping_angle_front_deg=round(math.degrees(math.atan2(max(xs) - com[0], d.subtree_com[1][2])), 1))
res["a_standing"] = {f"crouch_{c:.2f}": stand_metrics(stance(N, c, lean=BASE_LEAN[V])) for c in sorted({0.1, 0.3, CROUCH, 0.5, 0.63})}
print("a", json.dumps(res["a_standing"][f"crouch_{CROUCH:.2f}"]))
# open-loop COM window: which fore/aft COM offsets (vs sole centre) stand without any feedback (servo compliance only)
win = []
for lean in np.arange(-0.25, 0.46, 0.025):
    q = stance(N, CROUCH, lean=float(lean)); reset(m, d, q)
    sole = [i for i in range(m.ngeom) if m.geom(i).name.startswith("sole")]
    off = (d.subtree_com[1][0] - np.mean([d.geom_xpos[i][0] for i in sole])) * 1000
    info = run(m, d, sv, lambda t, r, g, q=q: q, 3.0, V)
    win.append((round(float(lean), 3), round(float(off), 1), info["fell"] is None))
okw = [w for w in win if w[2]]
res["a_open_loop_com_window_mm"] = dict(stable_offsets=[min(w[1] for w in okw), max(w[1] for w in okw)] if okw else None, sweep=win,
                                        note="COM x minus sole-centre x at q0; stands 3 s with no IMU feedback")
res["a_neutral_stance_no_lean"] = stand_metrics(stance(N, CROUCH, lean=0.0))
print("a window", res["a_open_loop_com_window_mm"]["stable_offsets"], "neutral fell:", res["a_neutral_stance_no_lean"]["fell"])

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
# ---------------- (e) head motions + arm waving / gripper while standing (balance controller on)
def head_arm(t, rpy, g):
    qq = BAL[0](t, rpy, g)
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
BAL = [None]
def e_margin(gains):
    BAL[0] = bal_policy(gains); reset(m, d, q0); mg = []
    inf = run(m, d, sv, head_arm, 12.0, V, on_step=lambda t, dd: mg.append(support_margin(m, dd)[0]) if int(t * 200) % 10 == 0 else None)
    return (-1.0 if inf["fell"] else round(float(np.nanmin(mg)), 1))

# rev C (v3.31): the push-sum objective alone is chaotic w.r.t. tiny mass changes (rev B picked kp_ankle=+0.55, which leans the
# COM 43 mm forward during the head nod -> 22 mm head+arm margin). Pick, among candidates within 10 % of the best push score,
# the one with the largest head+arm (e) margin. The pure push-best set and its margin are recorded too.
res["b_push_best_gains_unfiltered"] = [float(x) for x in best[1]]
# warm-start pool: the gain sets the v3.31 rev A / rev B1 runs selected (push sums are quantised by the bisection, so many sets tie)
for g in ((-0.182, -0.133, -0.586, -1.638, 0.154), (-0.043, -0.108, -0.743, -3.016, 0.112)):
    pol = bal_policy(g); tried.append((sum(max_push(pol, v) for v in DIRS.values()), g))
cands = [best] + sorted([t for t in tried if t[0] >= 0.9 * best[0] and t[1] != best[1]], key=lambda t: -t[0])[:10]
ev = [(e_margin(g), sc, g) for sc, g in cands]
res["b_gain_candidates(e_margin_mm,push_sum,gains)"] = [[a, float(b), [float(x) for x in c]] for a, b, c in ev]
res["e_margin_with_push_best_gains_mm"] = ev[0][0]
best = (max(ev, key=lambda t: (t[0], t[1]))[1], max(ev, key=lambda t: (t[0], t[1]))[2])
print("gain cands", ev)
res["b_balance_gains(kp_ankle,kd_ankle,kp_hip,kp_roll,kd_roll)"] = [float(x) for x in best[1]]
bal = bal_policy(best[1])
res["b_push_with_controller_Ns"] = {k: max_push(bal, v) for k, v in DIRS.items()}
print("b ctrl", res["b_push_with_controller_Ns"], best[1])
if VIDEO:
    vid = Video(m, dist=1.0, az=120, el=-10, track=False); vid.cam.lookat[:] = [0, 0, 0.18]
    reset(m, d, q0)
    for k, (ex, ey) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
        mp = list(res["b_push_with_controller_Ns"].values())[k] * 0.85 / 0.1
        run(m, d, sv, bal, 2.0, V, push=(0.3, 0.1, mp * ex, mp * ey), video=vid)
    vid.save(os.path.join(OUT, f"push_recovery_{V}.gif"), fps=25)
    try: vid.save(os.path.join(OUT, f"push_recovery_{V}.mp4"), fps=25)
    except Exception as e: print("mp4 failed", e)

# ---------------- (c) side-to-side weight shift (both-leg hip roll sine, no ankle roll on this robot)
def foot_loads():
    L = R = 0.0; f6 = np.zeros(6)
    for k in range(d.ncon):
        c = d.contact[k]; n1, n2 = m.geom(c.geom1).name, m.geom(c.geom2).name
        mujoco.mj_contactForce(m, d, k, f6)
        if "sole_foot_assembly_2" in (n1, n2): R += f6[0]
        elif "sole_foot_assembly" in (n1, n2): L += f6[0]
    return L, R
shift = {}
for A in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3):
    reset(m, d, q0); mins = [1.0, 1.0]; comy = []
    def pol(t, rpy, g, A=A):
        qq = q0.copy(); r = A * math.sin(2 * math.pi * 0.4 * t) * min(1, t / 1.0)
        qq[ix["left_hip_roll"]] += r; qq[ix["right_hip_roll"]] += r; return qq
    def on(t, dd):
        if t < 1.0: return
        L, R = foot_loads(); tot = L + R + 1e-9; mins[0] = min(mins[0], L / tot); mins[1] = min(mins[1], R / tot); comy.append(dd.subtree_com[1][1])
    info = run(m, d, sv, pol, 6.0, V, on_step=on)
    shift[f"{A:.2f}"] = dict(fell=info["fell"], min_load_frac_L=round(mins[0], 3), min_load_frac_R=round(mins[1], 3),
                             com_y_pp_mm=round((max(comy) - min(comy)) * 1000, 1) if comy else None)
res["c_weight_shift_sine_both_hip_roll_0.4Hz"] = shift; print("c sine", shift)
# quasi-static single-support attempt: roll both hips by phi (pelvis/trunk leans over the left foot), then fold the right leg
def single_support(phi, sgn):
    reset(m, d, q0); last = {}
    def pol(t, rpy, g):
        qq = bal(t, rpy, g) if t > 99 else q0.copy()
        r = sgn * phi * min(1, t / 1.5); qq[ix["left_hip_roll"]] += r; qq[ix["right_hip_roll"]] += r
        f = 0.25 * min(1, max(0, (t - 1.5) / 1.0))      # fold right leg: thigh back f, knee +2f -> foot rises
        qq[ix["right_hip_pitch"]] += f; qq[ix["right_knee"]] += 2 * f; qq[ix["right_ankle"]] += -f
        return qq
    def on(t, dd):
        L, R = foot_loads(); last["L"] = L / (L + R + 1e-9); last["tilt"] = math.degrees(body_rpy(dd)[0])
    info = run(m, d, sv, pol, 4.5, V, on_step=on)
    return dict(fell=info["fell"], left_load_frac=round(last.get("L", 0), 3), trunk_roll_deg=round(last.get("tilt", 0), 1))
ss = {}
for sgn in (1, -1):
    for phi in (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3):
        ss[f"sgn{sgn:+d}_phi{phi:.2f}"] = single_support(phi, sgn)
res["c_single_support_attempt"] = ss
ok = [(k, v) for k, v in ss.items() if v["fell"] is None and v["left_load_frac"] > 0.97]
res["c_single_support_min_phi"] = min(ok, key=lambda kv: float(kv[0].split("phi")[1]))[0] if ok else None
print("c single", res["c_single_support_min_phi"], ss)

BAL[0] = bal
reset(m, d, q0); rec = Recorder(N, sv.stall); margins = []
vid = Video(m, dist=1.0, az=140, el=-10, track=False) if VIDEO else None
if vid: vid.cam.lookat[:] = [0, 0, 0.2]
info = run(m, d, sv, head_arm, 12.0, V, rec=rec, video=vid, on_step=lambda t, dd: margins.append(support_margin(m, dd)[0]) if int(t * 200) % 10 == 0 else None)
if vid: vid.save(os.path.join(OUT, f"head_arms_{V}.gif"), fps=20)
st = rec.stats()
res["e_head_arm_motion"] = dict(fell=info["fell"], min_support_margin_mm=round(float(np.nanmin(margins)), 1),
                                torque={n: st[n] for n in N if any(k in n for k in ("neck", "head", "shoulder", "elbow", "gripper", "ankle", "hip_pitch"))})
print("e", info["fell"], round(float(np.nanmin(margins)), 1), {n: st[n]["peak"] for n in N if "neck" in n or "shoulder" in n or "head" in n})
json.dump(res, open(os.path.join(OUT, f"results_{V}.json"), "w"), indent=1, default=float)
print("wrote results", V)
