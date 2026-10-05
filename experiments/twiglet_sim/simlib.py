"""Shared MuJoCo harness: STS3215 servo model, stance/gait generator, balance feedback, metrics, video."""
import os, math, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__))
# twiglet repo layout: models/ holds every MJCF version, params/ every gait vector, out/ the run outputs (gitignored).
MODELS = os.path.join(HERE, "models")
DEFAULT_MODEL = {"v3": "twiglet_v3_v334_wig344.xml"}     # current robot: body v3.34 + head v3.30 + wig v3.44
OUT = os.environ.get("TWIGLET_OUT", os.path.join(HERE, "out")); os.makedirs(OUT, exist_ok=True)
def model_path(variant="v3"):
    """TWIGLET_XML (absolute, or a file name in models/) overrides; else models/<DEFAULT_MODEL[variant]>, else models/twiglet_<variant>.xml"""
    x = os.environ.get("TWIGLET_XML")
    if x: return x if os.path.isabs(x) or os.path.exists(x) else os.path.join(MODELS, x)
    return os.path.join(MODELS, DEFAULT_MODEL.get(variant, f"twiglet_{variant}.xml"))
def params_path(suf=""):
    """gait params: TWIGLET_PARAMS / TWIGLET_PARAMS_EFF override (path, or a file name in params/); default walk_v3[_eff]_best.npy next to this file"""
    x = os.environ.get("TWIGLET_PARAMS_EFF" if suf else "TWIGLET_PARAMS")
    if x: return x if os.path.isabs(x) or os.path.exists(x) else os.path.join(HERE, "params", x)
    return os.path.join(HERE, f"walk_v3{suf}_best.npy")
STALL, RATED, W0 = 1.91, 0.49, 5.45        # N.m stall @7.4 V, rated (continuous) N.m, no-load rad/s
I_STALL, I_IDLE, VBUS = 2.5, 0.12, 7.4
LEGS = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle"]
# balanced stance: thigh offset (rad) that puts the COM over the sole centres (v2 is nose-heavy: head A + displays + arms forward)
BASE_LEAN = {"v2": 0.17, "stock": 0.0, "opt1": 0.12, "v3": 0.08}
# Feetech STS3032 (arm servos on v3): 4.5 kg.cm = 0.441 N.m stall @6 V, 0.09 s/60deg no-load @6 V (11.6 rad/s), stall 1.2 A, idle 0.15 A,
# rated 1.5 kg.cm = 0.147 N.m (Feetech STS3032 datasheet). Kt ~ 3.5 kg.cm/A = 0.343 N.m/A, terminal resistance 2.8 ohm.
S32 = dict(stall=0.441, w0=11.6, rated=0.147, i_stall=1.2, i_idle=0.15, kt=0.343, r=2.8, vbus=6.0)
# STS3215 at 7.4 V: stall 1.91 N.m (19.5 kg.cm), 2.7 A stall current (Feetech spec), Kt ~ 0.71 N.m/A, R ~ 7.4/2.7 = 2.74 ohm
S15 = dict(stall=STALL, w0=W0, rated=RATED, i_stall=I_STALL, i_idle=I_IDLE, kt=1.91 / 2.7, r=7.4 / 2.7, vbus=VBUS)

class Servo:
    """STS3215 position servo modelled as a PWM-driven DC motor behind the gearbox:
         duty u = clip((Kp*e - Kd*w) / STALL, -1, 1)      (Kp 12 N.m/rad, Kd 0.25 N.m.s/rad, e = deadbanded error, backlash 0.4 deg total)
         tau    = STALL*u - (STALL/W0)*w                  (back-EMF: 0.35 N.m.s/rad; gives the linear torque-speed line at |u| = 1)
       clipped to +-STALL.  Joint armature 0.02 kg.m2, passive damping 0.05, frictionloss 0.05 are in the MJCF.
       Cross-check preset 'odm': the Open Duck Mini's own identified set (kp 9.5, joint damping 1.0, armature 0.01) -> see README."""
    def __init__(self, m, kp=12.0, kd=0.25, backlash_deg=0.4, latency_steps=0, rng=None, backemf=True):
        self.m = m; self.kp, self.kd = kp, kd; self.bl = math.radians(backlash_deg) / 2; self.bemf = STALL / W0 if backemf else 0.0
        self.names = [m.actuator(i).name for i in range(m.nu)]
        self.qadr = np.array([m.jnt_qposadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
        self.vadr = np.array([m.jnt_dofadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.lat = latency_steps; self.buf = []
        self.small = np.array(["antenna" in n for n in self.names])       # stock sg90 antennas
        # per-actuator stall torque from the MJCF ctrlrange (STS3032 arm joints on v3 have +-0.441 N.m)
        self.stall = np.array([float(m.actuator_ctrlrange[i, 1]) if m.actuator_ctrllimited[i] else STALL for i in range(m.nu)])
        self.s32 = self.stall < 1.0
        self.w0 = np.where(self.s32, S32["w0"], W0)
        # same duty-per-radian position loop on both servo types (Kp/STALL); Kd scaled the same way
        self.kpv = self.kp * self.stall / STALL; self.kdv = self.kd * self.stall / STALL
        self.bemfv = (self.stall / self.w0) if backemf else np.zeros(m.nu)
    def torque(self, d, qdes):
        if self.lat:
            self.buf.append(qdes.copy()); qdes = self.buf.pop(0) if len(self.buf) > self.lat else self.buf[0]
        q = d.qpos[self.qadr]; w = d.qvel[self.vadr]
        e = qdes - q; e = np.sign(e) * np.maximum(np.abs(e) - self.bl, 0.0)
        u = np.clip((self.kpv * e - self.kdv * w) / self.stall, -1.0, 1.0)
        tau = np.clip(self.stall * u - self.bemfv * w, -self.stall, self.stall)
        tau[self.small] = np.clip(tau[self.small], -0.15, 0.15)
        return tau

def stance(names, crouch=0.35, roll=0.0, lean=0.0, variant="v2"):
    """Joint targets (rad) for a flat-foot crouch: thigh back by `crouch`, shin forward 2*crouch, ankle keeps the sole flat.
    left hip value = theta1, right hip value = -theta1; knee/ankle same sign both sides."""
    q = np.zeros(len(names)); ix = {n: i for i, n in enumerate(names)}
    th = -crouch + lean
    for s, sg in (("left", 1), ("right", -1)):
        q[ix[f"{s}_hip_pitch"]] = sg * th; q[ix[f"{s}_knee"]] = 2 * crouch; q[ix[f"{s}_ankle"]] = -(th + 2 * crouch) + 0.0
        q[ix[f"{s}_hip_roll"]] = roll
    return q

def body_rpy(d):
    w, x, y, z = d.qpos[3:7]
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(max(-1, min(1, 2 * (w * y - z * x))))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return roll, pitch, yaw

class Gait:
    """Open-loop periodic gait + IMU feedback.  params dict:
    f (Hz), stride (rad thigh amplitude), lift (rad extra fold of swing leg), sway (rad both-leg hip roll), sway_ph (rad),
    crouch, lean, kp_pitch, kd_pitch (ankle), kp_roll, kd_roll (hip roll), turn (rad yaw bias), ramp (s)"""
    def __init__(self, names, p, variant="v2"):
        self.n = names; self.p = p; self.ix = {k: i for i, k in enumerate(names)}; self.v = variant
    def __call__(self, t, rpy, gyro, qbase):
        p = self.p; ix = self.ix; q = qbase.copy()
        a = min(1.0, t / p.get("ramp", 1.0))
        ph = 2 * math.pi * p["f"] * t
        s = math.sin(ph)
        sway = a * p["sway"] * math.sin(ph + p["sway_ph"])
        roll_fb = -(p["kp_roll"] * rpy[0] + p["kd_roll"] * gyro[0])
        pitch_fb = (p["kp_pitch"] * rpy[1] + p["kd_pitch"] * gyro[1])
        for side, sg, sw in (("left", 1, max(0.0, s)), ("right", -1, max(0.0, -s))):
            c = p["crouch"]; lift = a * p["lift"] * sw ** p.get("lift_pow", 1.0)
            stride = a * p["stride"] * (-math.cos(ph) if side == "left" else math.cos(ph))
            th = -c + BASE_LEAN.get(self.v, 0.0) + p["lean"] + stride - lift
            kn = 2 * c + 2 * lift
            an = -(th + kn) + pitch_fb + p.get("ank_off", 0.0)
            q[ix[f"{side}_hip_pitch"]] = sg * th; q[ix[f"{side}_knee"]] = kn; q[ix[f"{side}_ankle"]] = an
            q[ix[f"{side}_hip_roll"]] = sway + roll_fb
            q[ix[f"{side}_hip_yaw"]] = p.get("turn", 0.0)
        return q

def support_margin(m, d):
    """COM ground projection vs convex hull of sole-box corners of feet currently in contact (mm, positive = inside)."""
    from shapely.geometry import Point, MultiPoint
    pts = []
    for i in range(m.ngeom):
        nm = m.geom(i).name
        if not nm.startswith("sole_"): continue
        inc = any((d.contact[k].geom1 == i or d.contact[k].geom2 == i) for k in range(d.ncon))
        if not inc: continue
        R = d.geom_xmat[i].reshape(3, 3); c = d.geom_xpos[i]; h = m.geom_size[i]
        for sx in (-1, 1):
            for sy in (-1, 1): pts.append((c + R @ (h * [sx, sy, -1]))[:2])
    com = d.subtree_com[1][:2]
    if len(pts) < 3: return float("nan"), com
    hull = MultiPoint([tuple(p) for p in pts]).convex_hull
    dist = hull.exterior.distance(Point(*com)) * 1000
    return (dist if hull.contains(Point(*com)) else -dist), com

class Recorder:
    def __init__(self, names, stall=None): self.names = names; self.tau = []; self.t = []; self.stallv = stall
    def add(self, t, tau): self.t.append(t); self.tau.append(np.abs(tau))
    def stats(self):
        T = np.array(self.tau)
        if len(T) == 0: return {}
        return {n: dict(peak=round(float(T[:, i].max()), 3), rms=round(float(np.sqrt((T[:, i] ** 2).mean())), 3),
                        p95=round(float(np.percentile(T[:, i], 95)), 3)) for i, n in enumerate(self.names)}
    def current(self):
        T = np.array(self.tau)
        if self.stallv is None: return float((I_IDLE + (I_STALL - I_IDLE) * np.clip(T / STALL, 0, 1)).sum(1).mean())
        s32 = np.asarray(self.stallv) < 1.0
        I = np.where(s32, S32["i_idle"] + (S32["i_stall"] - S32["i_idle"]) * np.clip(T / S32["stall"], 0, 1),
                     I_IDLE + (I_STALL - I_IDLE) * np.clip(T / STALL, 0, 1))
        return float(I.sum(1).mean())

def load(variant):
    m = mujoco.MjModel.from_xml_path(model_path(variant)); d = mujoco.MjData(m); return m, d

def reset(m, d, q0, settle_z=True):
    mujoco.mj_resetData(m, d)
    sv = Servo(m); d.qpos[sv.qadr] = q0
    mujoco.mj_forward(m, d)
    if settle_z:     # drop the robot so the lowest sole touches the floor
        zs = []
        for i in range(m.ngeom):
            if m.geom(i).name.startswith("sole_"):
                R = d.geom_xmat[i].reshape(3, 3); c = d.geom_xpos[i]; h = m.geom_size[i]
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        for sz in (-1, 1): zs.append((c + R @ (h * [sx, sy, sz]))[2])
        d.qpos[2] -= min(zs) - 0.0005; mujoco.mj_forward(m, d)

def randomize(m, rng, scale=0.1):
    """mass +-scale on every body, floor/sole friction 0.6-1.0, armature/damping +-30 %"""
    m.body_mass[1:] *= rng.uniform(1 - scale, 1 + scale, m.nbody - 1)
    m.geom_friction[:, 0] = rng.uniform(0.6, 1.0)
    m.dof_armature[6:] *= rng.uniform(0.7, 1.3); m.dof_damping[6:] *= rng.uniform(0.7, 1.3)

class Video:
    def __init__(self, m, w=480, h=400, dist=0.95, az=140, el=-12, track=True):
        self.r = mujoco.Renderer(m, h, w); self.cam = mujoco.MjvCamera(); self.cam.distance = dist; self.cam.azimuth = az
        self.cam.elevation = el; self.frames = []; self.track = track
    def grab(self, d):
        if self.track: self.cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.17]
        self.r.update_scene(d, self.cam); self.frames.append(self.r.render().copy())
    def save(self, fn, fps=25):
        import imageio
        if fn.endswith(".gif"): imageio.mimsave(fn, self.frames, duration=1000 / fps, loop=0)
        else: imageio.mimsave(fn, self.frames, fps=fps, codec="libx264", quality=7)
