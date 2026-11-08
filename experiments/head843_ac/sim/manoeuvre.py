"""Isolated manoeuvre helpers. The baseline gait, randomization, and fall test are unchanged
when no schedule, heading controller, terrain, or head/arm overlay is requested.

Heading feedback is not the gait's constant `turn` bias. A bias trial sets Gait.turn and is
labelled open_loop_yaw_bias. Static pose clearance is not computed here.
"""
import math
import os
import numpy as np
import mujoco
from simlib import (
    Servo, Gait, stance, reset, load, randomize, Recorder, body_rpy, BASE_LEAN, LEGS, STALL,
    S32, S15,
)
from episode import run, soft_clip, gyro

SAT_MAIN = 1.90  # N.m, same threshold as the AC load report (stall is 1.91)

def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi

def is_main(name):
    return any(s in name for s in ("hip_pitch", "knee", "ankle")) and "hip_roll" not in name and "hip_yaw" not in name

class PhaseAmp:
    """Amplitude envelope that starts and stops on double-support edges.

    A double-support edge is sin(2*pi*f*t) == 0, where both swing lifts are zero.
    The ramp itself is linear in time over `ramp_cycles` gait cycles and is not a claim
    about motor torque.
    """
    def __init__(self, f, t_go, t_stop, ramp_cycles=1.0):
        self.f = float(f)
        self.t_go = float(t_go)
        self.t_stop = float(t_stop)
        self.ramp_cycles = float(ramp_cycles)
        self.ramp_T = self.ramp_cycles / self.f
        self.t_go_edge = self.edge_at_or_after(self.t_go)
        self.t_stop_edge = self.edge_at_or_after(self.t_stop)

    def edge_at_or_after(self, t):
        k = int(math.ceil(t * 2.0 * self.f - 1e-12))
        return k / (2.0 * self.f)

    def info(self):
        def s(t):
            return math.sin(2.0 * math.pi * self.f * t)
        return dict(t_go_cmd=self.t_go, t_stop_cmd=self.t_stop, t_go_edge=self.t_go_edge,
                    t_stop_edge=self.t_stop_edge, ramp_s=self.ramp_T, ramp_cycles=self.ramp_cycles,
                    sin_at_go_edge=s(self.t_go_edge), sin_at_stop_edge=s(self.t_stop_edge))

    def __call__(self, t, ph):
        go, stop, rT = self.t_go_edge, self.t_stop_edge, self.ramp_T
        if t < go:
            return 0.0
        if rT > 0 and t < go + rT:
            return (t - go) / rT
        if t < stop:
            return 1.0
        if rT > 0 and t < stop + rT:
            return max(0.0, 1.0 - (t - stop) / rT)
        return 0.0

class AbruptStop:
    """Same phase-aware start as PhaseAmp, then amplitude is cut at t_stop even mid-swing."""
    def __init__(self, f, t_go, t_stop, ramp_cycles=1.0):
        self.base = PhaseAmp(f, t_go, 1.0e6, ramp_cycles)
        self.t_stop = float(t_stop)
        self.f = float(f)

    def info(self):
        d = self.base.info()
        d["t_stop_cmd"] = self.t_stop
        d["t_stop_edge"] = self.t_stop
        d["sin_at_stop_cut"] = math.sin(2.0 * math.pi * self.f * self.t_stop)
        d["phase_aware_stop"] = False
        return d

    def __call__(self, t, ph):
        if t >= self.t_stop:
            return 0.0
        return self.base(t, ph)

class BaselineStartThenStop:
    """Original 1 s time ramp, then a stop. Isolates the stop from the phase-aware start hold.

    kind 'phase' waits for a double-support edge. kind 'abrupt' cuts at t_stop.
    """
    def __init__(self, f, t_stop, ramp_cycles=1.0, how="phase", start_ramp=1.0):
        self.f = float(f)
        self.t_stop = float(t_stop)
        self.start_ramp = float(start_ramp)
        self.how = how
        self.ramp_T = float(ramp_cycles) / self.f
        k = int(math.ceil(self.t_stop * 2.0 * self.f - 1e-12))
        self.t_stop_edge = k / (2.0 * self.f)

    def info(self):
        t_cut = self.t_stop_edge if self.how == "phase" else self.t_stop
        return dict(start="baseline_time_ramp", how=self.how, t_stop_cmd=self.t_stop,
                    t_stop_edge=self.t_stop_edge, t_cut=t_cut, ramp_s=self.ramp_T if self.how == "phase" else 0.0,
                    sin_at_stop_edge=math.sin(2 * math.pi * self.f * self.t_stop_edge),
                    sin_at_cut=math.sin(2 * math.pi * self.f * t_cut),
                    phase_aware_stop=self.how == "phase",
                    sin_at_stop_cut=None if self.how == "phase" else math.sin(2 * math.pi * self.f * self.t_stop))

    def __call__(self, t, ph):
        a = min(1.0, t / self.start_ramp) if self.start_ramp > 0 else 1.0
        t_cut = self.t_stop_edge if self.how == "phase" else self.t_stop
        if t < t_cut:
            return a
        if self.how == "phase" and self.ramp_T > 0 and t < t_cut + self.ramp_T:
            return max(0.0, 1.0 - (t - t_cut) / self.ramp_T)
        return 0.0

class SmoothWalk:
    """Raised-cosine amplitude from t=0. No motionless wait.

    phase0 shifts the gait so a double-support edge (sin = 0) falls at mid-rise.
    The stop, if requested, begins at the next double-support edge at or after t_stop
    and falls with a raised cosine over one gait cycle. The earlier wait-then-start
    schedule is a different class and is not this one.
    """
    def __init__(self, f, dur=1.2, t_stop=None, ramp_cycles=1.0):
        self.f = float(f)
        self.dur = float(dur)
        self.t_stop = None if t_stop is None else float(t_stop)
        self.ramp_T = float(ramp_cycles) / self.f
        self.phase0 = wrap(-2.0 * math.pi * self.f * (self.dur / 2.0))
        if self.t_stop is None:
            self.t_stop_edge = None
        else:
            shift = self.phase0 / (2.0 * math.pi)
            k = int(math.ceil(2.0 * (self.t_stop * self.f + shift) - 1e-12))
            self.t_stop_edge = (k / 2.0 - shift) / self.f

    def info(self):
        mid = self.dur / 2.0
        ph = 2.0 * math.pi * self.f * mid + self.phase0
        out = dict(kind="smooth_walk", dur_s=self.dur, phase0=self.phase0,
                   sin_at_mid_rise=math.sin(ph), ramp_s=self.ramp_T if self.t_stop is not None else 0.0,
                   phase_aware_stop=self.t_stop is not None, motionless_wait=False)
        if self.t_stop is not None:
            out.update(t_stop_cmd=self.t_stop, t_stop_edge=self.t_stop_edge, t_cut=self.t_stop_edge,
                       sin_at_stop_edge=math.sin(2.0 * math.pi * self.f * self.t_stop_edge + self.phase0))
        return out

    def _rise(self, t):
        if t <= 0.0:
            return 0.0
        if t >= self.dur:
            return 1.0
        u = t / self.dur
        return 0.5 - 0.5 * math.cos(math.pi * u)

    def __call__(self, t, ph):
        a = self._rise(t)
        if self.t_stop_edge is None or t < self.t_stop_edge:
            return a
        if self.ramp_T > 0 and t < self.t_stop_edge + self.ramp_T:
            u = (t - self.t_stop_edge) / self.ramp_T
            return a * (0.5 + 0.5 * math.cos(math.pi * u))
        return 0.0

def make_amp(spec, f):
    if not spec:
        return None
    kind = spec["kind"]
    if kind == "phase":
        return PhaseAmp(f, spec["t_go"], spec["t_stop"], spec.get("ramp_cycles", 1.0))
    if kind == "abrupt":
        return AbruptStop(f, spec["t_go"], spec["t_stop"], spec.get("ramp_cycles", 1.0))
    if kind in ("baseline_then_phase_stop", "baseline_then_abrupt_stop"):
        how = "phase" if "phase" in kind else "abrupt"
        return BaselineStartThenStop(f, spec["t_stop"], spec.get("ramp_cycles", 1.0), how=how)
    if kind == "smooth_walk":
        return SmoothWalk(f, spec.get("dur", 1.2), spec.get("t_stop"), spec.get("ramp_cycles", 1.0))
    if kind == "restart":
        return RestartAmp(f, spec["cycles"], spec.get("ramp_s", 1.0), spec.get("ramp_cycles", 1.0))
    raise ValueError(kind)

class RestartAmp:
    """One or more walks. Each cycle rises on the baseline 1 s ramp and stops on a double-support edge.

    The phase-aware start that waited motionless, then rose in one cycle, is not used.
    That start rolled over before the stop was reached. A later cycle is a restart, not a new episode.
    """
    def __init__(self, f, cycles, ramp_s=1.0, ramp_cycles=1.0):
        self.f = float(f)
        self.cycles = [(float(a), float(b)) for a, b in cycles]
        self.ramp_s = float(ramp_s)
        self.ramp_T = float(ramp_cycles) / self.f

    def _edge(self, t):
        k = int(math.ceil(t * 2.0 * self.f - 1e-12))
        return k / (2.0 * self.f)

    def info(self):
        stops = [self._edge(b) for _, b in self.cycles]
        return dict(kind="restart", cycles=self.cycles, t_cut=stops[0] if stops else None,
                    t_stop_edge=stops[0] if stops else None, ramp_s=self.ramp_T,
                    phase_aware_stop=True, n_cycles=len(self.cycles))

    def __call__(self, t, ph):
        amp = 0.0
        for t_go, t_stop in self.cycles:
            stop_edge = self._edge(t_stop)
            if t < t_go:
                continue
            if self.ramp_s > 0.0 and t < t_go + self.ramp_s:
                amp = max(amp, (t - t_go) / self.ramp_s)
            elif t < stop_edge:
                amp = 1.0
            elif self.ramp_T > 0.0 and t < stop_edge + self.ramp_T:
                amp = max(amp, max(0.0, 1.0 - (t - stop_edge) / self.ramp_T))
        return amp

def _smooth(t, t0, dur):
    if t <= t0:
        return 0.0
    if dur <= 0 or t >= t0 + dur:
        return 1.0
    u = (t - t0) / dur
    return u * u * (3.0 - 2.0 * u)

def apply_coord(q, names, t, rpy, phase, spec, yaw=0.0, yaw0=0.0, gyro=None):
    """Gait-phase head and arm motion with a floor on the IMU scale.

    The scale never falls below scale_min, and the arms sit on a raised pose,
    so a healthy walk does not collapse to the zero joint targets.
    Optional kp_sh / kp_head add a clipped heading-error bias on the same
    joints. Hip yaw is left to the gait. The sine amplitude is not reduced.
    """
    ix = {n: i for i, n in enumerate(names)}
    a = _smooth(t, spec.get("t0", 0.4), spec.get("dur", 1.4))
    tilt = math.hypot(rpy[0], rpy[1])
    atten = 1.0
    if spec.get("k_imu", 0.0) > 0:
        atten = 1.0 - float(spec["k_imu"]) * max(0.0, tilt - float(spec.get("tilt0", 0.06)))
        atten = min(1.0, max(float(spec.get("scale_min", 0.55)), atten))
    g = a * atten
    arm_phase = float(spec.get("arm_phase", 0.0))
    head_phase = float(spec.get("head_phase", arm_phase))
    sp = math.sin(phase + arm_phase)
    cp = math.cos(phase + arm_phase)
    sph = math.sin(phase + head_phase)
    cph = math.cos(phase + head_phase)
    err = wrap(yaw0 + float(spec.get("yaw_hold", 0.0)) - yaw)
    lim_sh = float(spec.get("couple_lim_sh", 0.09))
    lim_h = float(spec.get("couple_lim_head", 0.08))
    bias_sh = max(-lim_sh, min(lim_sh, float(spec.get("kp_sh", 0.0)) * err))
    bias_h = max(-lim_h, min(lim_h, float(spec.get("kp_head", 0.0)) * err))
    sh0 = float(spec.get("sh0", 22.0))
    el0 = float(spec.get("el0", 30.0))
    q[ix["shoulder_L"]] = math.radians(sh0 + spec["A_sh"] * g * sp) + bias_sh
    q[ix["shoulder_R"]] = math.radians(sh0 - spec["A_sh"] * g * sp) - bias_sh
    q[ix["elbow_L"]] = math.radians(el0 + spec.get("A_el", 5.0) * g * cp)
    q[ix["elbow_R"]] = math.radians(el0 - spec.get("A_el", 5.0) * g * cp)
    q[ix["gripper_L"]] = math.radians(spec.get("grip", 18.0))
    q[ix["gripper_R"]] = math.radians(spec.get("grip", 18.0))
    q[ix["head_yaw"]] = math.radians(spec["Y_yaw"] * g * sph) + bias_h
    q[ix["head_pitch"]] = math.radians(spec.get("pitch0", -4.0) + spec["Y_pitch"] * g * cph)
    q[ix["head_roll"]] = math.radians(spec.get("Y_roll", 1.5) * g * cph - spec.get("k_roll", 0.25) * math.degrees(rpy[0]))
    # Torso lean with the feet kept flat: same construction as crouch in the gait.
    # Positive body_lean moves the hips toward a deeper crouch as the arms rise.
    lean = (float(spec.get("body_lean", 0.0)) + float(spec.get("k_pitch", 0.0)) * rpy[1]) * g
    lean = max(-0.08, min(0.05, lean))
    if lean:
        q[ix["left_hip_pitch"]] -= lean
        q[ix["right_hip_pitch"]] += lean
        q[ix["left_ankle"]] += lean
        q[ix["right_ankle"]] += lean
    yaw_ff = float(spec.get("yaw_ff", 0.0))
    if yaw_ff:
        q[ix["left_hip_yaw"]] = yaw_ff * sp
        q[ix["right_hip_yaw"]] = yaw_ff * sp
    if spec.get("balance"):
        gy = gyro if gyro is not None else (0.0, 0.0, 0.0)
        _support_balance(q, ix, phase, rpy, gy, spec, g)
        pitch_window_recover(q, ix, phase, rpy, gy, spec, g)
        early_transfer(q, ix, phase, rpy, gy, spec, g)
        rate_capture(q, ix, phase, rpy, gy, spec, g)
    return q, dict(envelope=a, atten=atten, gain=g, yaw_err=err, bias_sh=bias_sh, bias_h=bias_h)

def _clip(v, lim):
    return max(-lim, min(lim, v))

def _support_balance(q, ix, phase_leg, rpy, gyro, spec, g):
    """Stance-leg and swing-foot response. Does not change the arm sine.

    Left leg swings when sin(phase_leg) > 0. A positive pitch, the sign measured
    while arms-forward walks tip, moves the swing foot forward: left hip pitch
    increases, right hip pitch decreases. k_hip uses the same joint map as body_lean
    and is applied on the stance leg only.
    """
    s = math.sin(phase_leg)
    wL, wR = max(s, 0.0), max(-s, 0.0)
    stL, stR = 1.0 - wL, 1.0 - wR
    pitch, roll = rpy[1], rpy[0]
    gp, gr = float(gyro[1]), float(gyro[0])
    place = _clip(spec.get("k_place", 0.0) * pitch + spec.get("d_place", 0.0) * gp, 0.10) * g
    q[ix["left_hip_pitch"]] += place * wL
    q[ix["right_hip_pitch"]] -= place * wR
    if spec.get("pre_toe"):
        # Same 0.10 rad placement, started in the last part of stance so the
        # hip is already moving at toe-off. The clip is not raised.
        if s < 0.0:
            pre_L = max(0.0, min(1.0, (s + 0.40) / 0.40))
            pre_R = 0.0
        else:
            pre_L = 0.0
            pre_R = max(0.0, min(1.0, (-s + 0.40) / 0.40))
        q[ix["left_hip_pitch"]] += place * pre_L
        q[ix["right_hip_pitch"]] -= place * pre_R
    hip = _clip(spec.get("k_hip", 0.0) * pitch + spec.get("d_hip", 0.0) * gp, 0.08) * g
    q[ix["left_hip_pitch"]] -= hip * stL
    q[ix["right_hip_pitch"]] += hip * stR
    q[ix["left_ankle"]] += hip * stL
    q[ix["right_ankle"]] += hip * stR
    ank = _clip(spec.get("k_ank", 0.0) * pitch + spec.get("d_ank", 0.0) * gp, 0.06) * g
    q[ix["left_ankle"]] += ank * stL
    q[ix["right_ankle"]] += ank * stR
    # Positive k_lat steps the swing foot toward -y when roll is positive and toward +y
    # when roll is negative. Both fresh arms-forward falls in the 51500-51523 probe had
    # roll about -43 deg, which drops the +y side; positive k_lat places the foot that way.
    lat = _clip(spec.get("k_lat", 0.0) * roll + spec.get("d_lat", 0.0) * gr, 0.08) * g
    q[ix["left_hip_roll"]] += lat * wL
    q[ix["right_hip_roll"]] += lat * wR
    # Wider stance: left foot toward +y, right foot toward -y. Differential, not a lean.
    width = max(-0.05, min(0.05, float(spec.get("step_width", 0.0)))) * g
    q[ix["left_hip_roll"]] -= width
    q[ix["right_hip_roll"]] += width
    # Extra pelvis roll, same sign as the gait's existing hip-roll feedback.
    extra = _clip(spec.get("k_roll_extra", 0.0) * roll + spec.get("d_roll_extra", 0.0) * gr, 0.08) * g
    q[ix["left_hip_roll"]] -= extra
    q[ix["right_hip_roll"]] -= extra
    # Load the stance foot when roll rate is toward the swing side.
    # Left swing is sin>0. Trunk toward the stance foot is -y during left swing
    # and +y during right swing, which is a hip-roll change of -swing_sign.
    swing_sign = 1.0 if s >= 0.0 else -1.0
    toward = max(0.0, -swing_sign * gr) + float(spec.get("k_load_pos", 2.0)) * max(0.0, -swing_sign * roll)
    load = _clip(float(spec.get("k_load", 0.0)) * toward, 0.07) * g
    q[ix["left_hip_roll"]] += -swing_sign * load
    q[ix["right_hip_roll"]] += -swing_sign * load

def _pitch_auth_summary(samples):
    """Diagnostic only. Does not feed the controller."""
    if not samples:
        return None
    fwd = math.radians(12.0)

    def cross(deg):
        thr = math.radians(deg)
        for s in samples:
            if s["pitch"] < -thr:
                return s
        return None

    out = {}
    for deg in (3, 5, 8, 12):
        s = cross(deg)
        key = str(deg)
        if s is None:
            out["t" + key] = None
            continue
        depth = max(abs(s["cmdL"] - s["preL"]), abs(s["cmdR"] - s["preR"]))
        clipL, clipR = s.get("clipL", s["cmdL"]), s.get("clipR", s["cmdR"])
        out["t" + key] = round(s["t"], 3)
        out["rate" + key] = round(math.degrees(s["gp"]), 2)
        out["depth" + key] = round(depth, 4)
        out["dL" + key] = round(math.degrees(s["cmdL"] - s["preL"]), 2)
        out["dR" + key] = round(math.degrees(s["cmdR"] - s["preR"]), 2)
        out["s" + key] = round(math.sin(s["ph"]), 2)
        out["soft" + key] = bool(abs(clipL - s["cmdL"]) > 0.002 or abs(clipR - s["cmdR"]) > 0.002)
        if "qL" in s:
            out["trk" + key] = round(math.degrees(max(abs(clipL - s["qL"]), abs(clipR - s["qR"]))), 2)
            out["eL" + key] = round(math.degrees(clipL - s["qL"]), 2)
            out["eR" + key] = round(math.degrees(clipR - s["qR"]), 2)
            out["tau" + key] = round(max(abs(s["tauL"]), abs(s["tauR"])), 3)
            out["tauLs" + key] = round(s["tauL"], 3)
            out["tauRs" + key] = round(s["tauR"], 3)
    band = [s for s in samples if s["pitch"] < -math.radians(5.0)]
    if band:
        depths = [max(abs(s["cmdL"] - s["preL"]), abs(s["cmdR"] - s["preR"])) for s in band]
        out["n_band"] = len(band)
        out["frac_capped"] = float(np.mean([d >= 0.059 for d in depths]))
        out["med_depth"] = float(np.median(depths))
        taus = [max(abs(s["tauL"]), abs(s["tauR"])) for s in band if "tauL" in s]
        if taus:
            out["frac_tau190"] = float(np.mean([t >= 1.90 for t in taus]))
            out["med_tau"] = float(np.median(taus))
        soft = [abs(s.get("clipL", s["cmdL"]) - s["cmdL"]) > 0.002 or abs(s.get("clipR", s["cmdR"]) - s["cmdR"]) > 0.002 for s in band]
        out["frac_soft"] = float(np.mean(soft))
        margins = [min(fwd - s.get("clipL", s["cmdL"]), s.get("clipR", s["cmdR"]) + fwd) for s in band]
        out["med_fwd_margin_deg"] = float(math.degrees(np.median(margins)))
    return out

def short_step_balance(q, ix, phase, rpy, gyro, yaw0, spec, g):
    """Backward-pitch catch and a heading trim for the short-step gait.

    The 22 nominal misses reach about -16° of pitch while roll is still a few
    degrees. Survivors with yaw already past 15° stay near -2° of pitch.
    The catch moves the stance thigh forward and the swing foot less forward,
    only while pitch is negative and still falling. Heading uses the stance
    leg and is trained here; the long-stride yaw gains are not reused.
    Cap is fixed at 0.06 rad. No sole force.
    """
    sb = spec.get("short_balance")
    if not sb:
        return
    pitch, gp = float(rpy[1]), float(gyro[1])
    on = float(sb.get("pitch_on", 0.10))
    # The late gate is the frozen law. rate_on is absent on that checkpoint, so
    # the early branch stays off and the 0.06 rad cap is unchanged.
    late = pitch < -on and gp < 0.0
    rate_on = float(sb.get("rate_on", 0.0))
    early = rate_on > 0.0 and (not late) and pitch < -float(sb.get("early_on", on)) and gp < -rate_on
    if late or early:
        if late:
            raw = float(sb.get("k_pitch", 0.0)) * (-pitch - on) + float(sb.get("k_rate", 0.0)) * (-gp)
        else:
            raw = (float(sb.get("k_rate", 0.0)) + float(sb.get("k_rate_early", 0.0))) * (-gp)
        depth = min(0.06, max(0.0, raw)) * g * float(sb.get("pitch_sign", 1.0))
        s = math.sin(phase)
        wL, wR = max(s, 0.0), max(-s, 0.0)
        stL, stR = 1.0 - wL, 1.0 - wR
        q[ix["left_hip_pitch"]] += depth * (stL - wL)
        q[ix["right_hip_pitch"]] += depth * (wR - stR)
    ky = float(sb.get("k_yaw", 0.0))
    if ky:
        yerr = wrap(yaw0 - float(rpy[2]))
        u = max(-0.03, min(0.03, ky * yerr))
        s = math.sin(phase)
        if s <= 0.0:
            q[ix["left_hip_yaw"]] = max(-0.07, min(0.07, q[ix["left_hip_yaw"]] + u))
        else:
            q[ix["right_hip_yaw"]] = max(-0.07, min(0.07, q[ix["right_hip_yaw"]] + u))

def stance_redistribute(q, ix, phase, spec, g, d, qadr):
    """Move stance hip and knee together so the ankle command is not pushed further.

    Fires only when the stance ankle command is already more negative than the
    joint by err_on. That is the direction whose torque sits on the -1.91 N·m
    rail. Knee and hip change by the same amount with opposite effect on the
    flat-sole sum, so this law does not add an ankle command. No sole force
    and no actuator-torque feedback.
    """
    st = spec.get("stance_share")
    if not st:
        return
    # Whichever ankle command is already past the joint in the saturated
    # negative direction. Phase is not a proxy for that event.
    err_l = float(q[ix["left_ankle"]] - d.qpos[qadr[ix["left_ankle"]]])
    err_r = float(q[ix["right_ankle"]] - d.qpos[qadr[ix["right_ankle"]]])
    if err_l <= err_r:
        side, err = "left", err_l
    else:
        side, err = "right", err_r
    if err > -float(st.get("err_on", 0.10)):
        return
    depth = min(float(st.get("depth", 0.08)), float(st.get("k", 1.0)) * (-err - float(st.get("err_on", 0.10))))
    depth *= g * float(st.get("sign", 1.0))
    if side == "left":
        q[ix["left_hip_pitch"]] -= depth
        q[ix["left_knee"]] += depth
        ia = ix["left_ankle"]
    else:
        q[ix["right_hip_pitch"]] += depth
        q[ix["right_knee"]] += depth
        ia = ix["right_ankle"]
    ease = float(st.get("ease", 0.0))
    if ease > 0.0:
        # Command moves toward the joint. Duty falls. Torque is not increased.
        q[ia] += min(ease, 0.5 * (-err - float(st.get("err_on", 0.10))))
    st["n"] = int(st.get("n", 0)) + 1

def rate_capture(q, ix, phase, rpy, gyro, spec, g):
    """Swing-foot offset from forward pitch rate, with its own cap.

    The existing placement clip mixes pitch angle and pitch rate, so a rising
    angle uses up the clip and the rate term disappears. This channel uses only
    the IMU pitch rate, only while that rate is forward, and only on the leg
    that is swinging. It does not add a stance-ankle command. Hip room at
    swing onset on fresh frozen walks is about 34°, so a cap near 0.10 rad
    stays inside the forward stop. No sole force and no COM state.
    """
    rc = spec.get("rate_capture")
    if not rc:
        return
    gp = float(gyro[1])
    if gp <= float(rc.get("rate_on", 0.25)):
        return
    depth = min(float(rc.get("cap", 0.08)), float(rc.get("k", 0.12)) * (gp - float(rc.get("rate_on", 0.25))))
    depth *= g
    if depth <= 0.0:
        return
    s = math.sin(phase)
    if s > 0.05:
        q[ix["left_hip_pitch"]] += depth
        q[ix["left_knee"]] = max(0.20, q[ix["left_knee"]] - depth)
    elif s < -0.05:
        q[ix["right_hip_pitch"]] -= depth
        q[ix["right_knee"]] = max(0.20, q[ix["right_knee"]] - depth)
    else:
        return
    rc["n"] = int(rc.get("n", 0)) + 1

def early_transfer(q, ix, phase, rpy, gyro, spec, g):
    """Put the swing foot down early once forward pitch is past the transient.

    Survivors in the replay peak near 11°. The falls that follow keep a
    positive pitch rate and the lateral gap then runs from about 10–30 mm to
    about 180 mm in under half a second. At the start of that burst the swing
    hip still has forward room, so the foot can land before the gap opens.
    This shortens swing lift. It does not raise a torque limit.
    """
    et = spec.get("early")
    if not et:
        return 0.0
    pitch, gp = float(rpy[1]), float(gyro[1])
    on = float(et.get("pitch_on", 0.21))
    rate = float(et.get("rate_on", 0.30))
    if pitch < on or gp < rate:
        return 0.0
    depth = min(float(et.get("depth", 0.10)), float(et.get("k", 1.0)) * (pitch - on))
    depth *= g
    if depth <= 0.0:
        return 0.0
    s = math.sin(phase)
    wL, wR = max(s, 0.0), max(-s, 0.0)
    stL, stR = 1.0 - wL, 1.0 - wR
    if s > 0.05:
        q[ix["left_knee"]] = max(0.15, q[ix["left_knee"]] - 2.0 * depth)
        q[ix["left_hip_pitch"]] += depth
        q[ix["left_ankle"]] += depth
    elif s < -0.05:
        q[ix["right_knee"]] = max(0.15, q[ix["right_knee"]] - 2.0 * depth)
        q[ix["right_hip_pitch"]] -= depth
        q[ix["right_ankle"]] += depth
    else:
        depth = 0.0
    # Hip takes the pitch the ankle is already holding. Ankle command moves
    # off the negative stop. Stall torque is unchanged.
    hip_d = float(et.get("hip", 0.0)) * g
    if hip_d:
        q[ix["left_hip_pitch"]] += hip_d * stL
        q[ix["right_hip_pitch"]] -= hip_d * stR
        q[ix["left_ankle"]] += hip_d * stL
        q[ix["right_ankle"]] += hip_d * stR
    et["n"] = int(et.get("n", 0)) + 1
    return depth

def pitch_window_recover(q, ix, phase, rpy, gyro, spec, g):
    """Extra swing-foot placement only after pitch or roll leaves the survivor band.

    On the frozen-gait falls, forward pitch reaches 8° before roll does, and
    0.3 s before the height drop the swing foot is still about 100 mm from the
    COM while the existing placement clips are already full. Survivors do not
    sit in this band. The cruise gains are unchanged outside it.
    """
    rec = spec.get("recover")
    if not rec:
        return
    s = math.sin(phase)
    wL, wR = max(s, 0.0), max(-s, 0.0)
    pitch, roll = float(rpy[1]), float(rpy[0])
    gp, gr = float(gyro[1]), float(gyro[0])
    pitch_on = float(rec.get("pitch_on", 0.16))
    if pitch > pitch_on and gp > 0.0:
        raw = float(rec.get("k_pitch", 0.0)) * (pitch - pitch_on) + float(rec.get("k_prate", 0.0)) * gp
        extra = _clip(raw, float(rec.get("place_cap", 0.08))) * g
        q[ix["left_hip_pitch"]] += extra * wL
        q[ix["right_hip_pitch"]] -= extra * wR
    roll_on = float(rec.get("roll_on", 0.14))
    if abs(roll) > roll_on and roll * gr > 0.0:
        raw = float(rec.get("k_roll", 0.0)) * roll
        extra = _clip(raw, float(rec.get("lat_cap", 0.06))) * g
        q[ix["left_hip_roll"]] += extra * wL
        q[ix["right_hip_roll"]] += extra * wR

def contact_hip_recover(q, m, d, ix, gyro, k, g):
    """Move the foot that is actually carrying load under a lateral fall.

    Positive hip-roll rate on a loaded left foot is not the case we want.
    Measured falls roll negative while the left sole still holds the weight, and
    a decrease in left hip roll moves that foot toward +y. q += k * roll_rate * share
    does that when k > 0. The airborne foot is left alone. Bounded to ±0.08 rad.
    """
    if not k:
        return 0.0, 0.0
    L = R = 0.0
    f6 = np.zeros(6)
    for i in range(d.ncon):
        c = d.contact[i]
        n1, n2 = m.geom(c.geom1).name, m.geom(c.geom2).name
        mujoco.mj_contactForce(m, d, i, f6)
        if "sole_foot_assembly_2" in (n1, n2):
            R += f6[0]
        elif "sole_foot_assembly" in (n1, n2):
            L += f6[0]
    tot = L + R + 1e-6
    rr = float(gyro[0])
    dL = _clip(k * rr * (L / tot), 0.08) * g
    dR = _clip(k * rr * (R / tot), 0.08) * g
    q[ix["left_hip_roll"]] += dL
    q[ix["right_hip_roll"]] += dR
    return L, R

def sole_forces(m, d):
    L = R = 0.0
    f6 = np.zeros(6)
    for i in range(d.ncon):
        c = d.contact[i]
        n1, n2 = m.geom(c.geom1).name, m.geom(c.geom2).name
        mujoco.mj_contactForce(m, d, i, f6)
        if "sole_foot_assembly_2" in (n1, n2):
            R += f6[0]
        elif "sole_foot_assembly" in (n1, n2):
            L += f6[0]
    return L, R

def advance_swing(t, rpy, gyro, spec, hint, m, d, p):
    """Bring the swing foot down earlier when one sole has collapsed.

    The lead is a phase offset in radians, capped at 0.6, and it decays once
    both feet are loaded again. It does not change the no-overlay gait.
    """
    k = float(spec.get("k_phase", 0.0))
    if not k:
        return
    if hint.get("pt") is None:
        hint["pmass"] = float(np.sum(m.body_mass))
        hint["plead"] = 0.0
    dt = 0.0 if hint.get("pt") is None else max(0.0, t - hint["pt"])
    hint["pt"] = t
    L, R = sole_forces(m, d)
    w = hint["pmass"] * 9.81
    loaded, other = max(L, R), min(L, R)
    trigger = (abs(rpy[0]) > 0.10 and abs(gyro[0]) > 0.8
               and loaded > 0.45 * w and other < 0.12 * max(loaded, 1e-6))
    if trigger:
        hint["plead"] = min(0.6, hint["plead"] + k * dt)
    else:
        hint["plead"] = max(0.0, hint["plead"] - 1.5 * dt)
    p["phase0"] = hint["plead"]

def _residual_scale(tau):
    """1 when the ankle is well below stall, 0 at 1.80 N·m and above."""
    a = abs(float(tau))
    if a >= 1.80:
        return 0.0
    if a <= 1.20:
        return 1.0
    return (1.80 - a) / 0.60

def stance_ankle_cmd(q, m, d, ix, rpy, gyro, spec, hint, t):
    """Pitch command on the ankles that are actually on the ground.

    Force share fades the command through double support and leaves an airborne
    ankle at zero. Residual scale shuts the command off as |torque| approaches
    stall. The position limit stays at 0.05 rad. No-overlay walking never calls this.
    """
    probe = spec.get("ank_probe")
    k = float(spec.get("k_stance_ank", 0.0))
    kd = float(spec.get("d_stance_ank", 0.0))
    ki = float(spec.get("i_stance_ank", 0.0))
    ank_arm = float(spec.get("ank_arm", 0.0))
    if probe is None and k == 0.0 and kd == 0.0 and ki == 0.0 and ank_arm == 0.0:
        return
    if "ank_mass" not in hint:
        hint["ank_mass"] = float(np.sum(m.body_mass))
        hint["ank_i"] = 0.0
        hint["ank_t"] = None
        hint["ank_n"] = 0
        hint["ank_clamp"] = 0
        hint["ank_sat"] = 0
    L, R = sole_forces(m, d)
    tot = L + R
    w = hint["ank_mass"] * 9.81
    if tot < 0.20 * w:
        share_L = share_R = 0.0
    else:
        share_L = L / tot
        share_R = R / tot
    ids = hint.get("ank_ids")
    if ids is None:
        ids = {
            "L": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "left_ankle"),
            "R": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "right_ankle"),
        }
        hint["ank_ids"] = ids
    tauL = float(d.actuator_force[ids["L"]])
    tauR = float(d.actuator_force[ids["R"]])
    scL = _residual_scale(tauL)
    scR = _residual_scale(tauR)
    lim = float(spec.get("ank_lim", 0.05))
    sgn = float(spec.get("ank_sign", 1.0))
    pitch = float(rpy[1])
    pr = float(gyro[1])
    dz = float(spec.get("ank_deadzone", 0.0))
    if abs(pitch) <= dz:
        err_pitch = 0.0
    else:
        err_pitch = math.copysign(abs(pitch) - dz, pitch)
    dt = 0.0 if hint["ank_t"] is None else max(0.0, t - hint["ank_t"])
    hint["ank_t"] = t
    if ank_arm:
        # Known arm-rise load, on the planted foot only. Not a pitch-error loop.
        u = max(-lim, min(lim, ank_arm * _smooth(t, float(spec.get("t0", 0.4)), float(spec.get("dur", 1.4)))))
    elif probe is not None:
        u = max(-lim, min(lim, float(probe)))
    else:
        err = err_pitch
        raw_pd = sgn * (k * err + kd * pr)
        raw = raw_pd + sgn * ki * hint["ank_i"]
        loaded = share_L * scL + share_R * scR
        # Stop integrating once the command is saturated in the correcting direction,
        # or both loaded ankles are already at the residual limit.
        pushing = abs(raw) >= lim - 1e-9 and (raw * err * sgn) > 0.0
        if loaded < 0.05 and (share_L + share_R) > 0.5:
            pushing = True
        if not pushing:
            ilim = float(spec.get("ank_ilim", 0.30))
            if dz > 0.0 and abs(pitch) <= dz:
                hint["ank_i"] *= max(0.0, 1.0 - 4.0 * dt)
            else:
                hint["ank_i"] = max(-ilim, min(ilim, hint["ank_i"] + err * dt))
            raw = raw_pd + sgn * ki * hint["ank_i"]
        u = max(-lim, min(lim, raw))
    q[ix["left_ankle"]] += u * share_L * scL
    q[ix["right_ankle"]] += u * share_R * scR
    hint["ank_n"] += 1
    if share_L + share_R > 0.5 and (share_L * scL + share_R * scR) < 0.05:
        hint["ank_sat"] += 1
    if abs(u) >= lim - 1e-9:
        hint["ank_clamp"] += 1

def _torque_room(tau, q_direction):
    """1 when commanding q_direction will not push an already-stalled hip."""
    signed = q_direction * float(tau)
    if signed <= 1.20:
        return 1.0
    if signed >= 1.75:
        return 0.0
    return (1.75 - signed) / 0.55

def apply_mass_edit(m, edit):
    """In-memory hypothetical mass or COM change. Does not write the canonical XML.

    inertia 'with_mass' scales the stored principal moments by the mass ratio
    (uniform-density assumption on that one lumped body). 'fixed' leaves the
    inertia tensor alone, which is mass removed at the existing COM. Neither
    is a printable shell.
    """
    for name, spec in edit.items():
        bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, name)
        if bid < 0:
            raise KeyError(name)
        old = float(m.body_mass[bid])
        if "mass_delta" in spec:
            new = old + float(spec["mass_delta"])
            if new <= 0.0:
                raise ValueError(name)
            if spec.get("inertia", "fixed") == "with_mass":
                m.body_inertia[bid] *= new / old
            m.body_mass[bid] = new
        if "ipos_x" in spec:
            m.body_ipos[bid][0] += float(spec["ipos_x"])

def plan_fore_aft(q, m, d, ix, rpy, gyro, spec, hint, t, ph, f):
    """Historical experiment, off unless historical_fore_aft is set.

    Foot target chosen at the start of stance, about half a step before toe-off.

    The offset is ramped through the second half of stance and held in the air.
    It replaces the reactive swing-foot pitch term when k_plan is set. Hip pitch
    is scaled down when that joint is already near stall in the commanded
    direction. An optional stance-ankle posture uses the same latched prediction
    and only the loaded foot's residual. No-overlay walking never calls this.
    """
    k = float(spec.get("k_plan", 0.0))
    if not k:
        return
    if "plan_ready" not in hint:
        hint["plan_ready"] = True
        hint["plan_pos"] = None
        hint["planL"] = 0.0
        hint["planR"] = 0.0
        hint["hatL"] = 0.0
        hint["hatR"] = 0.0
        hint["plan_n"] = 0
        hint["plan_abs"] = 0.0
        hint["pitch_hist"] = []
        hint["plan_ids"] = {
            "hL": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "left_hip_pitch"),
            "hR": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "right_hip_pitch"),
            "aL": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "left_ankle"),
            "aR": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "right_ankle"),
        }
    hint["pitch_hist"].append((t, float(rpy[1])))
    if len(hint["pitch_hist"]) > 40:
        hint["pitch_hist"] = hint["pitch_hist"][-40:]
    two_pi = 2.0 * math.pi
    ph = ph % two_pi
    pos = math.sin(ph) > 0.0
    prev = hint["plan_pos"]
    ids = hint["plan_ids"]
    if prev is None:
        hint["plan_pos"] = pos
    elif pos != prev:
        hint["plan_pos"] = pos
        # Entering stance: left when sin becomes negative, right when sin becomes positive.
        side = "L" if not pos else "R"
        cap = float(spec.get("plan_cap", 0.08))
        if spec.get("plan_from_arms"):
            # The arm rise is known before the body pitches. Map that schedule
            # onto a forward foot shift, capped at plan_cap.
            arm = _smooth(t, float(spec.get("t0", 0.4)), float(spec.get("dur", 1.4)))
            pitch_hat = arm
            delta = max(-cap, min(cap, cap * arm))
        else:
            # Half-step average, not pitch rate. Step-frequency pitch rate saturates
            # a constant-rate prediction and commands a full foot shift every step.
            hist = [p for (tt, p) in hint["pitch_hist"] if t - tt <= 0.30]
            pitch_hat = float(np.mean(hist)) if hist else float(rpy[1])
            dz = float(spec.get("plan_deadzone", 0.05))
            if abs(pitch_hat) <= dz:
                pitch_hat = 0.0
            else:
                pitch_hat = math.copysign(abs(pitch_hat) - dz, pitch_hat)
            delta = max(-cap, min(cap, k * pitch_hat))
        tau = float(d.actuator_force[ids["hL"] if side == "L" else ids["hR"]])
        # Positive delta moves the foot forward: left hip +, right hip -.
        q_dir = (1.0 if delta >= 0.0 else -1.0) if side == "L" else (-1.0 if delta >= 0.0 else 1.0)
        delta *= _torque_room(tau, q_dir)
        hint["plan" + side] = delta
        hint["hat" + side] = pitch_hat
    def progress(side):
        if side == "L":
            if ph >= math.pi:
                return (ph - math.pi) / math.pi
            return None
        if ph < math.pi:
            return ph / math.pi
        return None
    def ramp(prog):
        if prog is None:
            return 1.0
        if prog < 0.35:
            return 0.0
        x = (prog - 0.35) / 0.65
        return x * x * (3.0 - 2.0 * x)
    wL, wR = ramp(progress("L")), ramp(progress("R"))
    q[ix["left_hip_pitch"]] += hint["planL"] * wL
    q[ix["right_hip_pitch"]] -= hint["planR"] * wR
    hint["plan_n"] += 1
    hint["plan_abs"] += abs(hint["planL"]) * wL + abs(hint["planR"]) * wR
    ka = float(spec.get("k_plan_ank", 0.0))
    if not ka:
        return
    L, R = sole_forces(m, d)
    tot = L + R
    if "plan_mass" not in hint:
        hint["plan_mass"] = float(np.sum(m.body_mass))
    if tot < 0.20 * hint["plan_mass"] * 9.81:
        return
    for side, share, key, hat in (
        ("L", L / tot, "aL", hint["hatL"]),
        ("R", R / tot, "aR", hint["hatR"]),
    ):
        prog = progress(side)
        if prog is None or prog < 0.10 or prog > 0.60:
            continue
        tau = float(d.actuator_force[ids[key]])
        u = max(-0.04, min(0.04, -ka * hat))
        # Negative u fights a positive pitch prediction. Residual uses that torque sign.
        q_dir = -1.0 if u < 0.0 else 1.0
        q[ix["left_ankle" if side == "L" else "right_ankle"]] += u * share * _torque_room(tau, q_dir)

def yaw_command(t, yaw0, t0, t1, delta):
    if t <= t0:
        return yaw0
    if t >= t1:
        return yaw0 + delta
    u = (t - t0) / max(t1 - t0, 1e-9)
    return yaw0 + u * delta

def route_yaw(t, yaw0, spec):
    """Piecewise heading. Each segment ramps from the previous offset to yaw_deg.

    Offsets are degrees from the yaw at reset. Before the first segment the
    target is that reset yaw. There is no world rotation.
    """
    prev = 0.0
    for seg in spec.get("segments") or []:
        target = math.radians(float(seg["yaw_deg"]))
        t0, t1 = float(seg["t0"]), float(seg["t1"])
        if t < t0:
            return yaw0 + prev
        if t >= t1:
            prev = target
            continue
        u = (t - t0) / max(t1 - t0, 1e-9)
        return yaw0 + prev + u * (target - prev)
    return yaw0 + prev

def heading_reference(t, yaw0, href):
    """Yaw the hold laws should track. With no schedule this is the reset yaw."""
    if not href:
        return yaw0, None
    kind = href.get("kind")
    if kind == "feedback":
        ycmd = yaw_command(t, yaw0, href["t0"], href["t1"], href["delta"])
        return ycmd, ycmd
    if kind == "route":
        ycmd = route_yaw(t, yaw0, href)
        return ycmd, ycmd
    return yaw0, None

def apply_headarm(q, names, t, mode):
    """Overwrite head and arm targets only. Leg targets from the gait stay in place."""
    if not mode or mode == "none":
        return q
    ix = {n: i for i, n in enumerate(names)}
    if mode == "mild":
        a = min(1.0, max(0.0, (t - 1.0) / 1.0))
        sn = math.sin(2.0 * math.pi * 0.4 * t)
        cs = math.cos(2.0 * math.pi * 0.4 * t)
        q[ix["head_pitch"]] = math.radians(-8.0 + 6.0 * a * sn)
        q[ix["head_yaw"]] = math.radians(18.0 * a * math.sin(2.0 * math.pi * 0.25 * t))
        q[ix["head_roll"]] = math.radians(3.0 * a * math.sin(2.0 * math.pi * 0.3 * t))
        q[ix["shoulder_R"]] = math.radians(28.0 + 8.0 * a * sn)
        q[ix["elbow_R"]] = math.radians(32.0 + 6.0 * a * cs)
        q[ix["gripper_R"]] = math.radians(20.0)
        q[ix["shoulder_L"]] = math.radians(28.0 - 8.0 * a * sn)
        q[ix["elbow_L"]] = math.radians(32.0)
        q[ix["gripper_L"]] = math.radians(20.0)
        return q
    if mode == "mild_posthoc":
        # Chosen after the predeclared mild command fell on 25000-25039. Not a held-out claim.
        a = min(1.0, max(0.0, (t - 1.5) / 1.5))
        sn = math.sin(2.0 * math.pi * 0.25 * t)
        q[ix["head_pitch"]] = math.radians(-3.0 + 2.0 * a * sn)
        q[ix["head_yaw"]] = math.radians(6.0 * a * math.sin(2.0 * math.pi * 0.2 * t))
        q[ix["head_roll"]] = math.radians(1.5 * a * sn)
        q[ix["shoulder_R"]] = math.radians(18.0 + 4.0 * a * sn)
        q[ix["elbow_R"]] = math.radians(28.0)
        q[ix["gripper_R"]] = math.radians(15.0)
        q[ix["shoulder_L"]] = math.radians(18.0 - 4.0 * a * sn)
        q[ix["elbow_L"]] = math.radians(28.0)
        q[ix["gripper_L"]] = math.radians(15.0)
        return q
    if mode == "standing_script":
        # The standing head/arm script from run_tests.py, composed onto the walk.
        # It is not a new gait. Soft limits in episode.soft_clip still apply.
        seg = t % 12.0
        a = min(1.0, t / 2.0)
        q[ix["head_pitch"]] = -math.radians(34) * max(0.0, math.sin(2 * math.pi * seg / 6)) + math.radians(4) * max(0.0, -math.sin(2 * math.pi * seg / 6))
        q[ix["head_yaw"]] = math.radians(90) * math.sin(2 * math.pi * t / 4.0) * (1 if seg > 6 else 0.5)
        q[ix["head_roll"]] = math.radians(15) * math.sin(2 * math.pi * t / 2.5)
        q[ix["shoulder_R"]] = math.radians(8 + 62 * a + 10 * a * math.sin(2 * math.pi * 1.5 * t))
        q[ix["elbow_R"]] = math.radians(20 + 8 * math.sin(2 * math.pi * 1.5 * t))
        q[ix["gripper_R"]] = math.radians(30 + 30 * math.sin(2 * math.pi * 1.0 * t))
        q[ix["shoulder_L"]] = math.radians(30 + 25 * math.sin(2 * math.pi * 0.5 * t))
        q[ix["elbow_L"]] = math.radians(22 + 20 * max(0.0, math.sin(2 * math.pi * 0.5 * t)))
        q[ix["gripper_L"]] = math.radians(30 + 30 * math.sin(2 * math.pi * 0.7 * t))
        return q
    raise ValueError(mode)

def _model(terrain):
    if not terrain or terrain == "flat":
        return load("v3")
    from terrain_fixtures import compile_model
    m, _meta = compile_model(terrain)
    return m, mujoco.MjData(m)

def _loads(rec, names, stall):
    T = np.array(rec.tau) if rec.tau else np.zeros((0, len(names)))
    joints = {}
    if len(T) == 0:
        return joints, {}
    for i, n in enumerate(names):
        col = T[:, i]
        thr = SAT_MAIN if stall[i] >= 1.5 else 0.98 * float(stall[i])
        joints[n] = dict(rms=float(np.sqrt((col ** 2).mean())), peak=float(col.max()),
                         sat=float((col >= thr).mean()), sat_threshold_Nm=float(thr),
                         stall_Nm=float(stall[i]))
    main = [n for n in names if is_main(n)]
    leg = [n for n in names if any(j in n for j in LEGS)]
    summary = dict(
        main_rms=float(np.mean([joints[n]["rms"] for n in main])),
        main_sat=float(np.mean([joints[n]["sat"] for n in main])),
        main_peak=float(np.max([joints[n]["peak"] for n in main])),
        leg_rms=float(np.mean([joints[n]["rms"] for n in leg])),
        current_proxy_A=float(rec.current()),
        n_samples=int(len(T)),
        sample_dt_s=0.01,
    )
    return joints, summary

def _heading_metrics(trace, spec, fell):
    if not trace or spec is None or spec.get("kind") != "feedback":
        return {}
    ts = np.array([p["t"] for p in trace])
    yaw = np.array([p["yaw"] for p in trace])
    ycmd = np.array([p["ycmd"] for p in trace])
    err = np.array([wrap(c - y) for c, y in zip(ycmd, yaw)])
    x = np.array([p["x"] for p in trace]); y = np.array([p["y"] for p in trace])
    t0, t1 = spec["t0"], spec["t1"]
    # After the slew, cross-track is vs the ray along the commanded heading from the position at t1.
    post = ts >= t1
    pre = ts <= t0
    def ct(mask, heading, x0, y0):
        if mask.sum() < 2:
            return None
        lx, ly = -math.sin(heading), math.cos(heading)
        return (x[mask] - x0) * lx + (y[mask] - y0) * ly
    # position nearest t1
    i1 = int(np.argmin(np.abs(ts - t1)))
    heading_final_cmd = ycmd[-1]
    cross_post = ct(post, heading_final_cmd, x[i1], y[i1])
    i0 = int(np.argmin(np.abs(ts - min(ts))))
    cross_pre = ct(pre, ycmd[0], x[i0], y[i0])
    band = math.radians(5.0)
    after = np.where((ts >= t1) & (np.abs(err) < band))[0]
    return dict(
        heading_err_rms=float(np.sqrt((err ** 2).mean())),
        heading_err_peak=float(np.max(np.abs(err))),
        heading_err_final=float(err[-1]),
        heading_err_rms_deg=float(np.degrees(np.sqrt((err ** 2).mean()))),
        heading_err_final_deg=float(np.degrees(err[-1])),
        yaw_change=float(wrap(yaw[-1] - yaw[0])),
        yaw_change_deg=float(np.degrees(wrap(yaw[-1] - yaw[0]))),
        time_to_5deg_after_slew=None if len(after) == 0 else float(ts[after[0]] - t1),
        crosstrack_rms_before_slew_m=None if cross_pre is None else float(np.sqrt((cross_pre ** 2).mean())),
        crosstrack_rms_after_slew_m=None if cross_post is None else float(np.sqrt((cross_post ** 2).mean())),
        in_band_fraction_after_slew=float((np.abs(err[post]) < band).mean()) if post.any() else None,
        fell_before_end=fell is not None,
    )

def _stop_metrics(trace, amp_obj):
    if not trace or amp_obj is None:
        return {}
    info = amp_obj.info()
    ts = np.array([p["t"] for p in trace])
    x = np.array([p["x"] for p in trace]); y = np.array([p["y"] for p in trace])
    if len(ts) < 3:
        return dict(schedule=info)
    dt = np.diff(ts)
    spd = np.hypot(np.diff(x), np.diff(y)) / np.maximum(dt, 1e-6)
    tm = 0.5 * (ts[:-1] + ts[1:])
    def mean_in(t_a, t_b):
        m = (tm >= t_a) & (tm < t_b)
        return None if not np.any(m) else float(spd[m].mean())
    stop_t = info.get("t_cut", info.get("t_stop_edge", info.get("t_stop_cmd")))
    phase_stop = info.get("phase_aware_stop", "sin_at_stop_cut" not in info)
    ramp = float(info.get("ramp_s") or 0.0) if phase_stop else 0.0
    end_settle = stop_t + ramp + 0.4
    return dict(
        schedule=info,
        speed_before_stop=mean_in(stop_t - 1.0, stop_t),
        speed_after_settle=mean_in(max(end_settle, stop_t + 0.3), ts[-1] + 1e-6),
        disp_after_stop_m=float(np.hypot(x[-1] - x[int(np.argmin(np.abs(ts - stop_t)))],
                                          y[-1] - y[int(np.argmin(np.abs(ts - stop_t)))])),
    )

def rollout(job):
    """One episode. job is a plain dict so it can cross a process boundary."""
    x = np.array(job["x"], float)
    seed = int(job["seed"]); rand = bool(job.get("rand", True)); T = float(job.get("T", 10.0))
    from walk_search import KEYS
    p = dict(zip(KEYS, x)); p["ramp"] = 1.0
    # Scratch candidate only. Absent on the no-overlay path, so reliable.npy is untouched.
    if job.get("demand"):
        scale = float(job["demand"])
        p["f"] *= scale
        p["stride"] *= scale
    if job.get("stride_scale"):
        p["stride"] *= float(job["stride_scale"])
    if job.get("turn_bias") is not None:
        p["turn"] = float(job["turn_bias"])
    f = p["f"]
    amp = make_amp(job.get("amp"), f)
    if amp is not None:
        p["amp_fn"] = amp
        if getattr(amp, "phase0", None):
            p["phase0"] = float(amp.phase0)
    xml_override = job.get("xml")
    prev_xml = os.environ.get("TWIGLET_XML")
    if xml_override:
        os.environ["TWIGLET_XML"] = xml_override
    try:
        m, d = _model(job.get("terrain"))
    finally:
        if xml_override:
            if prev_xml is None:
                os.environ.pop("TWIGLET_XML", None)
            else:
                os.environ["TWIGLET_XML"] = prev_xml
    if job.get("mass_edit"):
        apply_mass_edit(m, job["mass_edit"])
    rng = np.random.default_rng(seed)
    lat = 0
    if rand:
        randomize(m, rng)
        lat = int(rng.integers(0, 6))
    sv = Servo(m, latency_steps=lat)
    g = Gait(sv.names, p, "v3")
    q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN["v3"])
    reset(m, d, q0)
    yaw0 = body_rpy(d)[2]
    href = job.get("heading")
    sign = float(job.get("command_sign", 1.0))
    damp_align = float(job.get("damp_align", 1.0))
    head_mode = job.get("headarm")
    want = bool(job.get("keep_trace"))
    want_q = bool(job.get("trace_q"))
    need_state = bool(want or href or amp is not None or job.get("calibrate") or job.get("measure_path"))
    trace = []
    qtrace = []
    cmd_track = []
    track_err = []
    motion_buf = []
    hint = {"i": 0.0, "t": None, "yi": 0.0, "yt": None, "sprev": None,
            "margin": {"n": 0, "clip": 0, "pitch": []},
            "ptail_n": 0, "ptail_gt8": 0, "ptail_gt10": 0, "ptail_max": 0.0}
    gains = []
    path = {"xy": None, "s": 0.0}
    last_rpy = [0.0, 0.0, 0.0]
    names = sv.names
    jn = [m.joint(i).name for i in range(m.njnt)]
    jadr = [int(m.jnt_qposadr[i]) for i in range(m.njnt)]
    hinge = [i for i in range(m.njnt) if m.jnt_type[i] == 3]

    def policy(t, rpy, gy):
        if isinstance(head_mode, dict) and head_mode.get("k_phase"):
            advance_swing(t, rpy, gy, head_mode, hint, m, d, p)
        q = g(t, rpy, gy, q0)
        y_ref, ycmd = heading_reference(t, yaw0, href)
        err = None if ycmd is None else wrap(ycmd - rpy[2])
        # The qualified walk holds yaw at reset. A heading schedule is the only
        # case that moves that target. The old slew writer is not applied on
        # top of the coord hold, because that hold replaces hip yaw.
        coord_hold = isinstance(head_mode, dict) and head_mode.get("kind") == "coord"
        if href and href.get("kind") == "feedback" and not coord_hold:
            dt = 0.0 if hint["t"] is None else max(0.0, t - hint["t"])
            hint["t"] = t
            ilim = float(href.get("ilim", 0.35))
            hint["i"] = max(-ilim, min(ilim, hint["i"] + err * dt))
            gyro_as_yaw = damp_align * gy[2]
            u = sign * (href["kp"] * err + float(href.get("ki", 0.0)) * hint["i"] - href["kd"] * gyro_as_yaw)
            lim = href["limit"]
            u = max(-lim, min(lim, u))
            q[sv.idx["left_hip_yaw"]] = u
            q[sv.idx["right_hip_yaw"]] = u
        ph_now = 2.0 * math.pi * f * t + float(p.get("phase0") or 0.0)
        if job.get("pitch_tail") or job.get("margin"):
            ap = abs(float(rpy[1]))
            hint["ptail_n"] += 1
            if ap > math.radians(8.0):
                hint["ptail_gt8"] += 1
            if ap > math.radians(10.0):
                hint["ptail_gt10"] += 1
            if ap > hint["ptail_max"]:
                hint["ptail_max"] = ap
            if float(rpy[1]) < hint.get("ptail_min", 0.0):
                hint["ptail_min"] = float(rpy[1])
        if job.get("margin"):
            s_now = math.sin(ph_now)
            prev_s = hint["sprev"]
            if prev_s is not None and (s_now > 0.0) != (prev_s > 0.0):
                hint["margin"]["pitch"].append(abs(float(rpy[1])))
            hint["sprev"] = s_now
            if isinstance(head_mode, dict):
                raw_place = float(head_mode.get("k_place", 0.0)) * float(rpy[1]) + float(head_mode.get("d_place", 0.0)) * float(gy[1])
                hint["margin"]["n"] += 1
                if abs(raw_place) >= 0.10:
                    hint["margin"]["clip"] += 1
        if isinstance(head_mode, dict) and head_mode.get("kind") == "coord":
            q, cg = apply_coord(q, names, t, rpy, ph_now, head_mode, yaw=rpy[2], yaw0=y_ref, gyro=gy)
            if head_mode.get("stance_share"):
                stance_redistribute(q, sv.idx, ph_now, head_mode, cg["gain"], d, sv.qadr)
            gains.append(cg["gain"])
            ki = float(head_mode.get("slow_yaw_ki", 0.0))
            # A moving heading schedule is tracked by a common-mode hip yaw below.
            # The reset-hold integrator saturates against that turn, so it stays frozen.
            scheduling = bool(href and (href.get("track_both") or href.get("track_settle")) and ycmd is not None)
            if ki and not scheduling:
                dt = 0.0 if hint["yt"] is None else max(0.0, t - hint["yt"])
                hint["yt"] = t
                yerr = wrap(y_ref - rpy[2])
                ilim = float(head_mode.get("slow_yaw_ilim", 0.4))
                ulim = float(head_mode.get("slow_yaw_ulim", 0.02))
                s = math.sin(ph_now)
                if head_mode.get("phase_yaw") and abs(s) > 0.05:
                    # Same sign on both feet. A positive hip-yaw command yaws the body
                    # negative in both stances, but the sin>0 half is several times stronger.
                    # Scale that half so one step does not kick the heading.
                    scale = 0.15 if s > 0.0 else 1.0
                    raw = scale * sign * ki * hint["yi"]
                elif head_mode.get("phase_yaw"):
                    raw = 0.0
                else:
                    raw = sign * ki * hint["yi"]
                # Output anti-windup. The ±0.02 rad clip is hit while |yi| is still
                # below ilim (0.02/0.12 = 0.167). Holding yi there avoids a long unwind.
                pushing = head_mode.get("anti_windup") and abs(raw) >= ulim - 1e-12 and (yerr * raw) > 0.0
                if not pushing:
                    hint["yi"] = max(-ilim, min(ilim, hint["yi"] + yerr * dt))
                    if head_mode.get("phase_yaw") and abs(s) > 0.05:
                        scale = 0.15 if s > 0.0 else 1.0
                        raw = scale * sign * ki * hint["yi"]
                    elif not head_mode.get("phase_yaw"):
                        raw = sign * ki * hint["yi"]
                u = max(-ulim, min(ulim, raw))
                q[sv.idx["left_hip_yaw"]] = u
                q[sv.idx["right_hip_yaw"]] = u
            ks = float(head_mode.get("k_support_yaw", 0.0))
            if ks:
                # Heading error on the foot that is actually down. Airborne share is ~0.
                # Proportional, so it does not wind up. Command per foot stays inside ±0.04 rad.
                yerr_s = wrap(y_ref - rpy[2])
                if "sup_ids" not in hint:
                    hint["sup_ids"] = True
                    hint["sup_mass"] = float(np.sum(m.body_mass))
                Lf, Rf = sole_forces(m, d)
                tot = Lf + Rf
                wgt = hint["sup_mass"] * 9.81
                if tot < 0.20 * wgt:
                    shL = shR = 0.0
                else:
                    shL, shR = Lf / tot, Rf / tot
                lim_s = float(head_mode.get("support_yaw_lim", 0.04))
                u_s = max(-lim_s, min(lim_s, ks * yerr_s))
                q[sv.idx["left_hip_yaw"]] = max(-0.07, min(0.07, q[sv.idx["left_hip_yaw"]] + u_s * shL))
                q[sv.idx["right_hip_yaw"]] = max(-0.07, min(0.07, q[sv.idx["right_hip_yaw"]] + u_s * shR))
            ky = float(head_mode.get("k_yaw_phase", 0.0))
            if ky:
                # Zero-mean hip yaw at the arm-wave phase. The slow integral
                # remains the only DC trim. Total command stays inside ±0.05 rad.
                add = max(-0.03, min(0.03, ky * math.sin(ph_now + float(head_mode.get("arm_phase", 1.2)))))
                for jn in ("left_hip_yaw", "right_hip_yaw"):
                    q[sv.idx[jn]] = max(-0.05, min(0.05, q[sv.idx[jn]] + add))
            if head_mode.get("short_balance"):
                if job.get("pitch_auth"):
                    hint["pa_preL"] = float(q[sv.idx["left_hip_pitch"]])
                    hint["pa_preR"] = float(q[sv.idx["right_hip_pitch"]])
                short_step_balance(q, sv.idx, ph_now, rpy, gy, y_ref, head_mode, cg["gain"])
                if href and href.get("track_settle") and ycmd is not None and not href.get("track_both"):
                    terr = wrap(ycmd - float(rpy[2]))
                    kp = float(href.get("k_yaw_p", 0.45))
                    extra = max(-0.08, min(0.08, kp * terr))
                    side = "left_hip_yaw" if math.sin(ph_now) <= 0.0 else "right_hip_yaw"
                    q[sv.idx[side]] = max(-0.12, min(0.12, q[sv.idx[side]] + extra))
                if href and href.get("track_both") and ycmd is not None:
                    prev, pt = hint.get("ycmd_prev"), hint.get("ycmd_t")
                    hint["ycmd_prev"], hint["ycmd_t"] = ycmd, t
                    rate = 0.0 if prev is None or pt is None or t <= pt else wrap(ycmd - prev) / (t - pt)
                    terr = wrap(ycmd - float(rpy[2]))
                    kp = float(href.get("k_yaw_p", 0.25))
                    kff = float(href.get("k_yaw_ff", 0.20))
                    # Positive hip yaw yaws the body the other way. The slow-yaw
                    # command sign is -1 for that reason. Both hips get this value.
                    u = max(-0.10, min(0.10, -(kp * terr + kff * rate)))
                    q[sv.idx["left_hip_yaw"]] = u
                    q[sv.idx["right_hip_yaw"]] = u
                else:
                    kff = float(href.get("k_yaw_ff", 0.0)) if href else 0.0
                    if kff and ycmd is not None:
                        prev, pt = hint.get("ycmd_prev"), hint.get("ycmd_t")
                        hint["ycmd_prev"], hint["ycmd_t"] = ycmd, t
                        if prev is not None and pt is not None and t > pt:
                            rate = wrap(ycmd - prev) / (t - pt)
                            uff = max(-0.08, min(0.08, kff * rate))
                            side = "left_hip_yaw" if math.sin(ph_now) <= 0.0 else "right_hip_yaw"
                            q[sv.idx[side]] = max(-0.10, min(0.10, q[sv.idx[side]] + uff))
                if job.get("pitch_auth"):
                    hint.setdefault("pauth", []).append(dict(
                        t=float(t), pitch=float(rpy[1]), gp=float(gy[1]), ph=float(ph_now),
                        preL=hint["pa_preL"], preR=hint["pa_preR"],
                        cmdL=float(q[sv.idx["left_hip_pitch"]]), cmdR=float(q[sv.idx["right_hip_pitch"]]),
                    ))
            ya = head_mode.get("yaw_add")
            if ya:
                # State-distributed heading. Applied after the arm-phase clip so
                # that clip cannot erase it. k_support_yaw above is unchanged.
                yamp = float(ya.get("amp", 0.0))
                if ya.get("from_error"):
                    yerr_a = wrap(y_ref - rpy[2])
                    yamp = max(-float(ya.get("lim", 0.04)), min(float(ya.get("lim", 0.04)), float(ya.get("k", 0.0)) * yerr_a))
                fade = float(ya.get("roll_fade", 0.0))
                if fade > 0.0:
                    yamp *= max(0.0, 1.0 - abs(float(rpy[0])) / fade)
                if ya.get("hold_upright") and abs(float(rpy[0])) > float(ya.get("roll_hold", 0.10)) and float(rpy[0]) * float(gy[0]) > 0.0:
                    yamp = 0.0
                if "sup_mass" not in hint:
                    hint["sup_mass"] = float(np.sum(m.body_mass))
                Lf, Rf = sole_forces(m, d)
                tot = Lf + Rf
                wgt = hint["sup_mass"] * 9.81
                if tot < 0.20 * wgt:
                    shL = shR = 0.0
                else:
                    shL, shR = Lf / tot, Rf / tot
                where = ya.get("where", "stance")
                if where == "split":
                    w_st = float(ya.get("w_stance", 0.35))
                    w_sw = float(ya.get("w_swing", 0.65))
                elif where == "swing":
                    w_st, w_sw = 0.0, float(ya.get("w_swing", 1.0))
                else:
                    w_st, w_sw = float(ya.get("w_stance", 1.0)), float(ya.get("w_swing", 0.0))
                q[sv.idx["left_hip_yaw"]] = max(-0.07, min(0.07, q[sv.idx["left_hip_yaw"]] + yamp * (w_st * shL + w_sw * shR)))
                q[sv.idx["right_hip_yaw"]] = max(-0.07, min(0.07, q[sv.idx["right_hip_yaw"]] + yamp * (w_st * shR + w_sw * shL)))
            kc = float(head_mode.get("k_contact", 0.0))
            if kc:
                contact_hip_recover(q, m, d, sv.idx, gy, kc, 1.0)
            if head_mode.get("ank_probe") is not None or head_mode.get("k_stance_ank") or head_mode.get("d_stance_ank") or head_mode.get("i_stance_ank") or head_mode.get("ank_arm"):
                stance_ankle_cmd(q, m, d, sv.idx, rpy, gy, head_mode, hint, t)
            # Historical only. The recommended frozen path does not set this flag.
            # k_plan alone does not move the feet.
            if head_mode.get("historical_fore_aft") and head_mode.get("k_plan"):
                plan_fore_aft(q, m, d, sv.idx, rpy, gy, head_mode, hint, t, ph_now, f)
            lp = head_mode.get("latch_probe")
            if lp:
                # Identification only. A constant hip-roll offset is latched on the
                # swing leg at the sin zero crossing and held until the next crossing.
                s = math.sin(ph_now)
                pos = s > 0.0
                if hint.get("prev_swing_pos") is None:
                    hint["prev_swing_pos"] = pos
                elif pos != hint["prev_swing_pos"]:
                    hint["prev_swing_pos"] = pos
                    hint["latch_side"] = "left" if pos else "right"
                    hint["latch"] = float(lp.get("amp", 0.0))
                if hint.get("latch_side"):
                    q[sv.idx[hint["latch_side"] + "_hip_roll"]] += hint["latch"]
            yp = head_mode.get("yaw_probe")
            if yp:
                kind = yp.get("kind")
                yp_amp = float(yp.get("amp", 0.0))
                s = math.sin(ph_now)
                if kind == "hip_both":
                    q[sv.idx["left_hip_yaw"]] = yp_amp
                    q[sv.idx["right_hip_yaw"]] = yp_amp
                elif kind == "hip_stance":
                    # Stance is the leg whose swing weight is zero.
                    q[sv.idx["left_hip_yaw"]] = yp_amp if s <= 0.0 else 0.0
                    q[sv.idx["right_hip_yaw"]] = yp_amp if s > 0.0 else 0.0
                elif kind == "step_diff":
                    # Same-sign hip pitch moves the two feet in opposite x.
                    q[sv.idx["left_hip_pitch"]] += yp_amp
                    q[sv.idx["right_hip_pitch"]] += yp_amp
        else:
            q = apply_headarm(q, names, t, head_mode)
        if job.get("trunk_stats"):
            if hint.get("tr_z0") is None:
                tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly")
                hint["tr_id"] = tb
                hint["tr_z0"] = float(d.subtree_com[tb][2])
                hint["tr_roll"] = 0.0
                hint["tr_zmin"] = hint["tr_z0"]
                hint["tr_n"] = 0
                hint["tr_r8"] = 0
            hint["tr_n"] += 1
            hint["tr_roll"] = max(hint["tr_roll"], abs(float(rpy[0])))
            zc = float(d.subtree_com[hint["tr_id"]][2])
            if zc < hint["tr_zmin"]:
                hint["tr_zmin"] = zc
            if abs(float(rpy[0])) > math.radians(8.0):
                hint["tr_r8"] += 1
        last_rpy[0], last_rpy[1], last_rpy[2] = rpy
        clipped = soft_clip(list(names), q.copy(), "v3")
        if job.get("pitch_auth") and hint.get("pauth"):
            rec = hint["pauth"][-1]
            if abs(rec["t"] - t) < 1e-9:
                iL, iR = names.index("left_hip_pitch"), names.index("right_hip_pitch")
                rec["clipL"] = float(clipped[iL]); rec["clipR"] = float(clipped[iR])
        if head_mode and head_mode != "none":
            cmd_track.append((t, {n: float(clipped[names.index(n)]) for n in ("head_pitch", "head_yaw", "head_roll", "shoulder_L", "elbow_L", "shoulder_R", "elbow_R")}))
        if need_state or head_mode:
            x, y = float(d.qpos[0]), float(d.qpos[1])
            if path["xy"] is not None:
                path["s"] += math.hypot(x - path["xy"][0], y - path["xy"][1])
            path["xy"] = (x, y)
        if job.get("capture") or job.get("ankle_audit"):
            hint["cap_cmd"] = {n: float(clipped[names.index(n)]) for n in (
                "left_hip_roll", "right_hip_roll", "left_hip_pitch", "right_hip_pitch",
                "left_hip_yaw", "right_hip_yaw", "left_ankle", "right_ankle",
                "left_knee", "right_knee")}
        if need_state:
            trace.append(dict(t=t, x=float(d.qpos[0]), y=float(d.qpos[1]), z=float(d.qpos[2]),
                              yaw=float(rpy[2]), roll=float(rpy[0]), pitch=float(rpy[1]),
                              gz=float(gy[2]),
                              ycmd=None if ycmd is None else float(ycmd),
                              yerr=None if err is None else float(err),
                              amp=None if amp is None else float(amp(t, 2 * math.pi * f * t)),
                              hip_yaw=float(clipped[names.index("left_hip_yaw")])))
        if job.get("track_ankle"):
            hint["trk_n"] = hint.get("trk_n", 0) + 1
            bad = negb = False
            for an in ("left_ankle", "right_ankle"):
                ia = sv.idx[an]
                e_an = float(clipped[ia] - d.qpos[sv.qadr[ia]])
                if abs(e_an) > 0.12:
                    bad = True
                if e_an < -0.12:
                    negb = True
            if bad:
                hint["trk_big"] = hint.get("trk_big", 0) + 1
            if negb:
                hint["trk_neg"] = hint.get("trk_neg", 0) + 1
        return q

    cap_samples = []
    audit = []
    if job.get("capture") or job.get("ankle_audit"):
        tb_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly")
        sole_ids = {
            "L": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "sole_foot_assembly"),
            "R": mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "sole_foot_assembly_2"),
        }
        cap_q = {n: int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)])
                 for n in ("left_hip_roll", "right_hip_roll", "left_hip_pitch", "right_hip_pitch",
                           "left_hip_yaw", "right_hip_yaw")}
        cap_act = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, n)
                   for n in ("left_hip_roll", "right_hip_roll", "left_hip_pitch", "right_hip_pitch",
                             "left_hip_yaw", "right_hip_yaw", "left_ankle", "right_ankle")}

    def on_step(t, dd):
        if job.get("pitch_auth") and hint.get("pauth") and abs(t / 0.02 - round(t / 0.02)) < 1e-6:
            rec = hint["pauth"][-1]
            if "qL" not in rec and abs(rec["t"] - t) < 0.03:
                iL, iR = sv.idx["left_hip_pitch"], sv.idx["right_hip_pitch"]
                rec["qL"] = float(dd.qpos[sv.qadr[iL]])
                rec["qR"] = float(dd.qpos[sv.qadr[iR]])
                rec["tauL"] = float(dd.actuator_force[iL])
                rec["tauR"] = float(dd.actuator_force[iR])
        if job.get("capture") and hint.get("cap_cmd") is not None and abs(t / 0.01 - round(t / 0.01)) < 1e-8:
            rpy_s = body_rpy(dd)
            gy_s = gyro(m, dd)
            Ls, Rs = sole_forces(m, dd)
            com = dd.subtree_com[tb_id]
            cap_samples.append(dict(
                t=round(float(t), 4),
                roll=float(rpy_s[0]), pitch=float(rpy_s[1]), yaw=float(rpy_s[2]),
                rr=float(gy_s[0]), pr=float(gy_s[1]), yr=float(gy_s[2]),
                comx=float(com[0]), comy=float(com[1]), comz=float(com[2]),
                Lw=float(Ls), Rw=float(Rs),
                cmd=dict(hint["cap_cmd"]),
                ach={n: float(dd.qpos[cap_q[n]]) for n in cap_q},
                tauYawL=float(dd.actuator_force[cap_act["left_hip_yaw"]]),
                tauYawR=float(dd.actuator_force[cap_act["right_hip_yaw"]]),
                tauL=float(dd.actuator_force[cap_act["left_hip_roll"]]),
                tauR=float(dd.actuator_force[cap_act["right_hip_roll"]]),
                hipL=float(dd.actuator_force[cap_act["left_hip_pitch"]]),
                hipR=float(dd.actuator_force[cap_act["right_hip_pitch"]]),
                ankL=float(dd.actuator_force[cap_act["left_ankle"]]),
                ankR=float(dd.actuator_force[cap_act["right_ankle"]]),
                footL=(float(dd.geom_xpos[sole_ids["L"]][0]), float(dd.geom_xpos[sole_ids["L"]][1])),
                footR=(float(dd.geom_xpos[sole_ids["R"]][0]), float(dd.geom_xpos[sole_ids["R"]][1])),
            ))
        if job.get("ankle_audit") and hint.get("cap_cmd") is not None and abs(t / 0.02 - round(t / 0.02)) < 1e-8:
            for side, aname in (("L", "left_ankle"), ("R", "right_ankle")):
                ia = sv.idx[aname]
                jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, aname)
                qadr = int(m.jnt_qposadr[jid]); dadr = int(m.jnt_dofadr[jid])
                axis = np.array(dd.xaxis[jid], float)
                anchor = np.array(dd.xanchor[jid], float)
                moment = 0.0; fn = 0.0; arm = 0.0; ncon = 0
                f6 = np.zeros(6)
                for ci in range(dd.ncon):
                    c = dd.contact[ci]
                    n1, n2 = m.geom(c.geom1).name, m.geom(c.geom2).name
                    sole = "sole_foot_assembly_2" if side == "R" else "sole_foot_assembly"
                    if sole == "sole_foot_assembly" and "sole_foot_assembly_2" in (n1, n2):
                        continue
                    if sole not in (n1, n2):
                        continue
                    mujoco.mj_contactForce(m, dd, ci, f6)
                    R = dd.contact[ci].frame.reshape(3, 3)
                    force = R.T @ f6[:3]
                    r = np.array(c.pos, float) - anchor
                    moment += float(np.dot(np.cross(r, force), axis))
                    fn += float(f6[0]); arm += float(np.linalg.norm(r[:2])); ncon += 1
                audit.append(dict(
                    t=round(float(t), 3), side=side,
                    tau=float(dd.actuator_force[ia]), ctrl=float(dd.ctrl[ia]),
                    gear=float(m.actuator_gear[ia, 0]),
                    w=float(dd.qvel[dadr]), q=float(dd.qpos[qadr]),
                    qdes=float(hint["cap_cmd"][aname]),
                    moment=moment, fn=fn, ncon=ncon,
                    pitch=float(body_rpy(dd)[1]),
                    s=float(math.sin(2.0 * math.pi * f * t)),
                ))
        if want_q and abs(t / 0.02 - round(t / 0.02)) < 1e-8:
            qtrace.append(dict(t=t, q={jn[i]: float(dd.qpos[jadr[i]]) for i in hinge}))
        if cmd_track and abs(t / 0.02 - round(t / 0.02)) < 1e-8:
            tc, cq = cmd_track[-1]
            if abs(tc - t) < 0.03:
                meas = {}
                for n, c in cq.items():
                    mv = float(dd.qpos[jadr[jn.index(n)]])
                    meas[n] = mv
                    track_err.append((n, c - mv))
                if t >= 2.0:
                    motion_buf.append(meas)

    rec = Recorder(sv.names, sv.stall)
    info = run(m, d, sv, policy, T, "v3", rec=rec, push=tuple(job["push"]) if job.get("push") else None,
               on_step=on_step if (want_q or head_mode or job.get("capture") or job.get("ankle_audit")) else None)
    joints, load = _loads(rec, names, sv.stall)
    # state samples for metrics even when the full trace was not requested
    if not want:
        # a cheap second pass is avoided: policy already can record if we set a light trace.
        pass
    out = dict(seed=seed, fell=info["fell"], dx=float(info["dx"]), dy=float(info["dy"]),
               yaw=float(info["yaw"]), t_end=float(info["t"]), T=T, speed=(float(info["dx"]) / T) if info["fell"] is None else None,
               load=load, joints=joints, terrain=job.get("terrain") or "flat",
               headarm=(head_mode.get("name") if isinstance(head_mode, dict) else (head_mode or "none")),
               yaw_change=float(wrap(info["yaw"] - yaw0)),
               path_m=float(path["s"]),
               path_speed=(float(path["s"]) / T) if info["fell"] is None else None,
               roll_end=float(last_rpy[0]), pitch_end=float(last_rpy[1]))
    if isinstance(head_mode, dict) and isinstance(head_mode.get("early"), dict):
        out["early_n"] = int(head_mode["early"].get("n", 0))
    if isinstance(head_mode, dict) and isinstance(head_mode.get("rate_capture"), dict):
        out["capture_n"] = int(head_mode["rate_capture"].get("n", 0))
    if isinstance(head_mode, dict) and isinstance(head_mode.get("stance_share"), dict):
        out["stance_n"] = int(head_mode["stance_share"].get("n", 0))
    if hint.get("tr_z0"):
        out["trunk"] = dict(
            roll_max_deg=float(math.degrees(hint["tr_roll"])),
            height_min=float(hint["tr_zmin"] / hint["tr_z0"]),
            frac_roll8=float(hint["tr_r8"] / hint["tr_n"]) if hint.get("tr_n") else None,
        )
    if href and href.get("kind") == "feedback":
        out["heading"] = _heading_metrics(trace, href, info["fell"])
        out["yaw0"] = float(yaw0)
    if job.get("turn_bias") is not None:
        out["yaw_change"] = float(wrap(info["yaw"] - yaw0))
        out["open_loop_yaw_bias"] = float(job["turn_bias"])
    if amp is not None:
        out["stop"] = _stop_metrics(trace, amp)
    if motion_buf:
        pp, mean = {}, {}
        for n in motion_buf[0]:
            col = np.array([s[n] for s in motion_buf])
            pp[n] = round(math.degrees(float(col.max() - col.min())), 2)
            mean[n] = round(math.degrees(float(col.mean())), 2)
        out["motion_pp_deg"] = pp
        out["motion_mean_deg"] = mean
        out["coord_gain_mean"] = float(np.mean(gains)) if gains else None
    if track_err:
        by = {}
        for n, e in track_err:
            by.setdefault(n, []).append(e)
        out["tracking_rms"] = {n: float(np.sqrt(np.mean(np.square(v)))) for n, v in by.items()}
    if job.get("calibrate"):
        out["cal_trace_yaw"] = [p["yaw"] for p in trace]
        out["cal_trace_t"] = [p["t"] for p in trace]
        out["cal_trace_gz"] = [p["gz"] for p in trace]
    if want:
        out["trace"] = trace
    if want_q:
        out["qtrace"] = qtrace
    if job.get("calibrate"):
        out["cal_yaw0"] = float(yaw0)
        out["cal_yaw1"] = float(info["yaw"])
    if job.get("capture"):
        out["capture"] = cap_samples
    if job.get("ankle_audit"):
        out["ankle_audit"] = audit
    if job.get("track_ankle") and hint.get("trk_n"):
        out["ankle_track"] = dict(
            frac_abs=float(hint.get("trk_big", 0) / hint["trk_n"]),
            frac_neg=float(hint.get("trk_neg", 0) / hint["trk_n"]),
        )
    if job.get("pitch_auth"):
        out["pitch_auth"] = _pitch_auth_summary(hint.get("pauth") or [])
    if job.get("margin"):
        mrg = hint["margin"]
        out["margin"] = dict(n=int(mrg["n"]), clip=int(mrg["clip"]), pitch=[float(v) for v in mrg["pitch"]])
    if job.get("pitch_tail") or job.get("margin"):
        ntail = int(hint["ptail_n"])
        out["pitch_tail"] = dict(
            n=ntail,
            frac_gt8=float(hint["ptail_gt8"] / ntail) if ntail else None,
            frac_gt10=float(hint["ptail_gt10"] / ntail) if ntail else None,
            max_deg=float(math.degrees(hint["ptail_max"])),
            min_deg=float(math.degrees(hint.get("ptail_min", 0.0))),
        )
    if hint.get("plan_n"):
        out["plan_stats"] = dict(
            mean_abs=float(hint["plan_abs"] / hint["plan_n"]),
            planL=float(hint.get("planL") or 0.0),
            planR=float(hint.get("planR") or 0.0),
        )
    if hint.get("ank_n"):
        out["ank_stats"] = dict(
            n=int(hint["ank_n"]),
            frac_clamped=float(hint["ank_clamp"] / hint["ank_n"]),
            frac_no_residual=float(hint["ank_sat"] / hint["ank_n"]),
            integ=float(hint.get("ank_i") or 0.0),
        )
    if need_state and len(trace) >= 2:
        xs = np.array([p["x"] for p in trace]); ys = np.array([p["y"] for p in trace])
        lx, ly = -math.sin(yaw0), math.cos(yaw0)
        cross = (xs - xs[0]) * lx + (ys - ys[0]) * ly
        out["straight_crosstrack_rms_m"] = float(np.sqrt(np.mean(cross ** 2)))
        out["straight_final_lateral_m"] = float(cross[-1])
        if href and href.get("kind") == "feedback":
            lim = float(href["limit"])
            hy = np.array([abs(p["hip_yaw"]) for p in trace])
            out["heading"]["yaw_command_at_limit_fraction"] = float(np.mean(np.abs(hy - lim) < 1e-4))
    return out

def rollout_with_state(job):
    """Rollout that keeps the state trace, for plots."""
    job = dict(job)
    job["keep_trace"] = True
    return rollout(job)

def aggregate(rows, T=None):
    n = len(rows)
    fell = [r["seed"] for r in rows if r["fell"] is not None]
    surv = [r for r in rows if r["fell"] is None]
    def mean(key, src):
        vals = [r[key] for r in src if r.get(key) is not None]
        return None if not vals else float(np.mean(vals))
    speeds = [r["dx"] / r["T"] for r in surv]
    loads = [r["load"] for r in surv if r.get("load")]
    joint_names = list(surv[0]["joints"]) if surv and surv[0].get("joints") else []
    joints = {}
    for name in joint_names:
        block = [r["joints"][name] for r in surv if r.get("joints")]
        joints[name] = dict(rms=float(np.mean([b["rms"] for b in block])),
                            peak_mean=float(np.mean([b["peak"] for b in block])),
                            peak_max=float(np.max([b["peak"] for b in block])),
                            sat=float(np.mean([b["sat"] for b in block])),
                            sat_threshold_Nm=block[0]["sat_threshold_Nm"],
                            stall_Nm=block[0]["stall_Nm"])
    head = [r.get("heading") or {} for r in surv]
    def hmean(k):
        vals = [h[k] for h in head if h.get(k) is not None]
        return None if not vals else float(np.mean(vals))
    stop = [r.get("stop") or {} for r in surv]
    def smean(k):
        vals = [s[k] for s in stop if isinstance(s.get(k), (int, float))]
        return None if not vals else float(np.mean(vals))
    return dict(
        n=n, succ=n - len(fell), fell=fell,
        speed_mps=None if not speeds else float(np.mean(speeds)),
        dy_mean_m=mean("dy", surv),
        main_rms=None if not loads else float(np.mean([L["main_rms"] for L in loads])),
        main_sat=None if not loads else float(np.mean([L["main_sat"] for L in loads])),
        main_peak_mean=None if not loads else float(np.mean([L["main_peak"] for L in loads])),
        leg_rms=None if not loads else float(np.mean([L["leg_rms"] for L in loads])),
        current_proxy_A=None if not loads else float(np.mean([L["current_proxy_A"] for L in loads])),
        joints=joints,
        heading_err_rms_deg=hmean("heading_err_rms_deg"),
        heading_err_final_deg=hmean("heading_err_final_deg"),
        heading_err_peak_deg=None if not head else float(np.mean([np.degrees(h["heading_err_peak"]) for h in head if h.get("heading_err_peak") is not None] or [np.nan])),
        crosstrack_after_m=hmean("crosstrack_rms_after_slew_m"),
        crosstrack_before_m=hmean("crosstrack_rms_before_slew_m"),
        in_band_after=hmean("in_band_fraction_after_slew"),
        time_to_5deg=hmean("time_to_5deg_after_slew"),
        yaw_change_deg=None if not surv else float(np.degrees(np.mean([
            (r.get("heading") or {}).get("yaw_change", r.get("yaw_change", 0.0)) for r in surv]))),
        straight_crosstrack_rms_m=mean("straight_crosstrack_rms_m", surv),
        straight_final_lateral_m=mean("straight_final_lateral_m", surv),
        entered_5deg_fraction=(None if not any("heading_err_rms" in (r.get("heading") or {}) for r in surv)
                               else float(np.mean([(r.get("heading") or {}).get("time_to_5deg_after_slew") is not None
                                                   for r in surv if "heading_err_rms" in (r.get("heading") or {})]))),
        yaw_command_at_limit_fraction=hmean("yaw_command_at_limit_fraction"),
        tracking_rms=(None if not any(r.get("tracking_rms") for r in surv) else {
            n: float(np.mean([r["tracking_rms"][n] for r in surv if r.get("tracking_rms") and n in r["tracking_rms"]]))
            for n in next(r["tracking_rms"] for r in surv if r.get("tracking_rms"))
        }),
        speed_before_stop=smean("speed_before_stop"),
        speed_after_settle=smean("speed_after_settle"),
        disp_after_stop_m=smean("disp_after_stop_m"),
        load_on="survivors_only",
        note="Fallen episodes are excluded from speed and load means. Saturation is the fraction of 0.01 s |torque| samples at or above 1.90 N.m on STS3215 joints.",
    )
