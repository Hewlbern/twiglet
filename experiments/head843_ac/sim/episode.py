"""Episode runner shared by the tests and the gait search."""
import math, numpy as np, mujoco
from simlib import Servo, body_rpy, support_margin, Recorder, reset, stance, Gait, load, randomize
# soft limits (rad) applied to commands; v2 from collide_v2 (thigh forward <= 20 deg, ankle +-50 deg: boot vs shin)
R = math.radians
# soft limits (rad) applied to every command.  From collide_v2 free ranges (see ../collide_report.json):
#  thigh forward <= 12 deg (stock leg_spacer vs pitch-servo contact, identical on the stock ODM), ankle -65..+47 (shin vs foot, stock parts)
#  v2 only: single-leg inward hip roll <= 9 deg (boots 43 mm apart), neck pitch -5..+15, head pitch -45..+22, shoulder -12..+103, elbow -20..+103
LEG = {"left_hip_pitch": (R(-70), R(12)), "right_hip_pitch": (R(-12), R(70)), "left_ankle": (R(-65), R(47)), "right_ankle": (R(-65), R(47))}
SOFT = {"v2": dict(LEG, left_hip_roll=(R(-20), R(20)), right_hip_roll=(R(-20), R(20)), neck_pitch=(R(-5), R(15)), head_pitch=(R(-45), R(22)),
                   shoulder_L=(R(-12), R(103)), shoulder_R=(R(-12), R(103)), elbow_L=(R(-20), R(103)), elbow_R=(R(-20), R(103))),
        "stock": dict(LEG), "opt1": dict(LEG),
        # v3 (../collide_report.json): hip yaw +-7 (hip bracket vs neck-servo cradle when combined with roll), hip roll +-20, neck -1..+4 and head roll +-5 (head sits on the
        # shoulders like the photo), head pitch -34..+5, head yaw free; shoulder 0..84, elbow 2..120 with the coupled rule below, gripper 0..60
        "v3": dict(LEG, left_hip_yaw=(R(-7), R(7)), right_hip_yaw=(R(-7), R(7)), left_hip_roll=(R(-15), R(20)), right_hip_roll=(R(-20), R(15)),   # v3.2: outward roll 15 (arm gripper vs hip bracket at 17 with 13 deg splay)
                   neck_pitch=(R(-1), R(3)), head_pitch=(R(-34), R(3)), head_roll=(R(-5), R(5)),   # v3.6: 210 mm head, collision-free -34..+3; v3.5: neck-pitch joint removed (fixed post), head pitch collision-free -40..+6 -> soft -38..+4; v3.3: 180 mm head raised 6 mm + neck column: collision-free for neck+head fwd <= 3 combined -> head fwd 0 (v3.2: 3/3)
                   shoulder_L=(R(-5), R(84)), shoulder_R=(R(-5), R(84)), elbow_L=(R(0), R(120)), elbow_R=(R(0), R(120)), gripper_L=(R(0), R(60)), gripper_R=(R(0), R(60)))}
DIFF_ROLL_MAX = {"v2": R(9), "stock": R(25), "opt1": R(25), "v3": R(12)}
def soft_clip(names, q, variant):
    for n, (lo, hi) in SOFT[variant].items():
        if n in names: i = names.index(n); q[i] = min(max(q[i], lo), hi)
    if variant == "v3":                 # coupled arm limits (forearm/fingers vs head collar, gripper vs hip bracket)
        for sd in ("L", "R"):
            if f"shoulder_{sd}" in names:
                i, j = names.index(f"shoulder_{sd}"), names.index(f"elbow_{sd}")
                q[j] = min(max(q[j], R(25) - q[i]), max(0.0, min(R(110), R(105) - q[i])))      # v3.2 coupled rule: 25 - shoulder <= elbow <= 105 - shoulder (gripper vs hip bracket / chin collar)
    if "left_hip_roll" in names:        # differential (splay) hip roll limit: feet/boots collide on v2
        i, j = names.index("left_hip_roll"), names.index("right_hip_roll"); dmax = DIFF_ROLL_MAX[variant]
        dlt = q[i] - q[j]
        if abs(dlt) > dmax: mid = (q[i] + q[j]) / 2; q[i] = mid + math.copysign(dmax / 2, dlt); q[j] = mid - math.copysign(dmax / 2, dlt)
    return q
def gyro(m, d):
    a = m.sensor("imu_gyro").adr[0]; return d.sensordata[a:a + 3].copy()
def run(m, d, sv, policy, T, variant, push=None, video=None, rec=None, ctrl_dt=0.02, fps=25, on_step=None, fall_tilt=45):
    """policy(t, rpy, gyro) -> q targets (servo order). push = (t0, dur, fx, fy). Returns dict."""
    nsub = int(round(ctrl_dt / m.opt.timestep)); tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly")
    z0 = d.subtree_com[tb][2]; x0 = d.qpos[0]; y0 = d.qpos[1]
    qdes = policy(0.0, body_rpy(d), gyro(m, d)); steps = int(T / m.opt.timestep); fell = None; next_frame = 0.0
    for k in range(steps):
        t = k * m.opt.timestep
        if k % nsub == 0: qdes = soft_clip(sv.names, policy(t, body_rpy(d), gyro(m, d)), variant)
        if push is not None:
            t0, dur, fx, fy = push
            d.xfrc_applied[tb, :3] = [fx, fy, 0] if t0 <= t < t0 + dur else [0, 0, 0]
        tau = sv.torque(d, qdes); d.ctrl[:] = tau
        mujoco.mj_step(m, d)
        if rec is not None and k % 5 == 0: rec.add(t, tau)
        if on_step is not None and k % 5 == 0: on_step(t, d)
        if video is not None and t >= next_frame: video.grab(d); next_frame += 1.0 / fps
        r, p, _ = body_rpy(d)
        if fell is None and (abs(r) > math.radians(fall_tilt) or abs(p) > math.radians(fall_tilt) or d.subtree_com[tb][2] < 0.6 * z0):
            fell = t
            if video is None: break
    r, p, yaw = body_rpy(d)
    return dict(fell=fell, dx=d.qpos[0] - x0, dy=d.qpos[1] - y0, yaw=yaw, t=T if fell is None else fell)
