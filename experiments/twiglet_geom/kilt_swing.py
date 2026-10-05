"""Kilt-swing clearance: FCL contacts between the kilt petals (+ hip ring proxy) and every leg / arm link (logic and pose sets from
body-v3.34-body/measure/kilt_swing.py). Link meshes come from the v3.34 scene, moved by MuJoCo FK of models/twiglet_v3_v334_wig344.xml.
Pose sets:
  sim_gaits          - every 8th physics step (25 Hz) of 10 s walks with both shipped gaits, nominal + 2 randomized seeds (5000, 5001)
  gait120_single_leg - 120 random single-leg poses (hip pitch -60..18, knee 0..100, ankle +-50; yaw/roll soft-clipped)
  gait120_both_legs  - 120 random both-leg poses; gait80_arms_moving - the first 80 of those + random arm poses
  single_leg_stance  - hip-roll weight-shift series
PASS: sim_gaits leg 0 / arm 0, stance 0. The synthetic grids are informative (v3.34b record: single-leg 12, both 1, arms+legs 1).
usage: python kilt_swing.py [--fast]   (--fast: main gait only, nominal + 2 seeds)"""
import os, sys, json, math, random, numpy as np, trimesh, mujoco
import geomlib as G
SIM = os.path.join(os.path.dirname(G.HERE), "twiglet_sim"); sys.path.insert(0, SIM)
FAST = "--fast" in sys.argv; sys.argv = [sys.argv[0], "v3"]
os.environ.setdefault("TWIGLET_XML", "twiglet_v3_v334_wig344.xml")
import walk_search as W
from simlib import load, randomize, Servo, Gait, stance, reset, BASE_LEAN, model_path, params_path
from episode import run
items, _ = G.load_scene(); TM = G.TM
LEGA = ["hip_roll_assembly", "left_roll_to_pitch_assembly", "knee_and_ankle_assembly", "knee_and_ankle_assembly_2", "foot_assembly", "hip_roll_assembly_2",
        "right_roll_to_pitch_assembly", "knee_and_ankle_assembly_3", "knee_and_ankle_assembly_4", "foot_assembly_2"]
ARMA = G.ARMA
def dec(m, n=5000): return G.dec(m, n)
cm = trimesh.collision.CollisionManager()
for ln, n, k, V, F in items:
    if ln == "trunk_assembly" and (n.startswith("kilt_petal") or n == "hip_ring"): cm.add_object(n[-2:] if n.startswith("kilt") else n, TM(V, F))
m = mujoco.MjModel.from_xml_path(model_path("v3")); d = mujoco.MjData(m)
d.qpos[:] = m.qpos0; mujoco.mj_kinematics(m, d); _bt = m.body("trunk_assembly").id; _Rt = d.xmat[_bt].reshape(3, 3); _pt = d.xpos[_bt]; LM = {}
for l in LEGA + ARMA:
    b = m.body(l).id; R = _Rt.T @ d.xmat[b].reshape(3, 3); p = _Rt.T @ (d.xpos[b] - _pt) * 1000.0; T0 = np.eye(4); T0[:3, :3] = R; T0[:3, 3] = p
    mm = dec(trimesh.util.concatenate([TM(V, F) for ln, n, k, V, F in items if ln == l])); mm.apply_transform(np.linalg.inv(T0)); LM[l] = mm
JN = {m.joint(i).name: i for i in range(m.njnt) if m.jnt_type[i] == 3}
REST = {"shoulder_L": 8.0, "shoulder_R": 8.0, "elbow_L": 22.0, "elbow_R": 22.0}
def poses(q):
    qq = dict(REST); qq.update(q); d.qpos[:] = m.qpos0
    for n, v in qq.items():
        if n in JN: d.qpos[m.jnt_qposadr[JN[n]]] = math.radians(v)
    mujoco.mj_kinematics(m, d); bt = m.body("trunk_assembly").id
    Rt = d.xmat[bt].reshape(3, 3); pt = d.xpos[bt]; T = {}
    for l in LM:
        b = m.body(l).id; R = Rt.T @ d.xmat[b].reshape(3, 3); p = Rt.T @ (d.xpos[b] - pt) * 1000.0
        M4 = np.eye(4); M4[:3, :3] = R; M4[:3, 3] = p; T[l] = M4
    return T
CP = []
def check(q):
    T = poses(q); hits = []
    for l, mm in LM.items():
        c, names, cd = cm.in_collision_single(mm, transform=T[l], return_names=True, return_data=True)
        if c: hits.append((l, sorted(names))); CP.extend([(l, sorted(x.names), np.round(x.point, 1).tolist(), {k: round(v, 1) for k, v in q.items()}) for x in cd[:1]])
    return hits
def summarize(tag, qs):
    leg = arm = 0; ex = []; per = {}
    for q in qs:
        h = check(q)
        if any(l in ARMA for l, _ in h): arm += 1
        if any(l in LEGA for l, _ in h): leg += 1
        for l, ns in h:
            for n in ns: per[n] = per.get(n, 0) + 1
        if h and len(ex) < 2: ex.append(h)
    r = dict(poses=len(qs), leg_contacts=leg, arm_contacts=arm, per_part=per, examples=ex); print(tag, {k: r[k] for k in ("poses", "leg_contacts", "arm_contacts", "per_part")}, flush=True); return r
def gait_samples(n=120, seed=1):     # from body-v2/collide_v2.py
    random.seed(seed); out = []
    for i in range(n):
        side = random.choice(["left", "right"]); th = random.uniform(-60, 18); sg = 1 if side == "left" else -1
        out.append({f"{side}_hip_yaw": random.uniform(-10, 10), f"{side}_hip_roll": random.uniform(-10, 10), f"{side}_hip_pitch": sg * th, f"{side}_knee": random.uniform(0, 100), f"{side}_ankle": random.uniform(-50, 50)})
    return out
rep = {"model": os.path.basename(model_path("v3")), "params": [os.path.basename(params_path("")), os.path.basename(params_path("_eff"))]}; gq = []
for suf in (("",) if FAST else ("", "_eff")):
    best = np.load(params_path(suf))
    for seed, rand in ((0, False), (5000, True), (5001, True)):
        p = dict(zip(W.KEYS, best)); p["ramp"] = 1.0; ms, ds = load("v3"); rng = np.random.default_rng(seed)
        if rand: randomize(ms, rng)
        sv = Servo(ms); g = Gait(sv.names, p, "v3"); q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN["v3"]); reset(ms, ds, q0)
        names = [ms.joint(i).name for i in range(ms.njnt)]; adr = [ms.jnt_qposadr[i] for i in range(ms.njnt)]; buf = []
        def on_step(t, dd):
            if int(round(t / 0.005)) % 8 == 0: buf.append({nm: math.degrees(dd.qpos[a]) for nm, a in zip(names, adr) if ms.jnt_type[names.index(nm)] == 3})
        run(ms, ds, sv, lambda t, r, gy: g(t, r, gy, q0), 10.0, "v3", on_step=on_step); gq += buf
rep["sim_gaits"] = summarize("sim gaits", gq)
def soft(q):
    for k in list(q):
        if k.endswith("hip_yaw"): q[k] = max(-7, min(7, q[k]))
        if k.endswith("hip_roll"): q[k] = max(-20, min(20, q[k]))
    return q
rep["gait120_single_leg"] = summarize("gait120 single leg", [soft(q) for q in gait_samples()])
random.seed(3); both = []
for i in range(120):
    a = random.uniform(-18, 18); r = random.uniform(-8, 8); y = random.uniform(-10, 10)
    both.append(soft({"left_hip_pitch": -a - 15, "right_hip_pitch": a + 15, "left_knee": random.uniform(0, 70), "right_knee": random.uniform(0, 70), "left_hip_roll": r,
                      "right_hip_roll": r + random.uniform(-4, 4), "left_hip_yaw": y, "right_hip_yaw": -y, "left_ankle": random.uniform(-40, 40), "right_ankle": random.uniform(-40, 40)}))
rep["gait120_both_legs"] = summarize("gait120 both legs", both)
random.seed(5); ag = []
for i in range(80):
    q = dict(both[i]); q.update({"shoulder_L": random.uniform(-2, 60), "elbow_L": random.uniform(0, 90), "shoulder_R": random.uniform(-2, 60), "elbow_R": random.uniform(0, 90)}); ag.append(q)
rep["gait80_arms_moving"] = summarize("arms+legs", ag)
sl = []
for sg in (1, -1):
    for ph in np.arange(0, 0.31, 0.05):
        r = math.degrees(sg * ph * 0.6); sl.append({"left_hip_roll": r, "right_hip_roll": r, "left_ankle": -r * 0.3, "right_ankle": -r * 0.3})
rep["single_leg_stance"] = summarize("single-leg stance", sl)
rep["contact_points"] = CP[:60]
G.save(f"kilt_swing_v334_wig344{'_fast' if FAST else ''}.json", rep)
