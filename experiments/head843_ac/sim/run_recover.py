"""Contact-aware hip recovery and phase-aware yaw, trained separately.

Contact train 63000-63079. Heading train is 20 s on 63400-63439.
A candidate is frozen only if it clears its own predeclared gate.
Held-out, when used: 64000-64199 and 65000-65199 for a contact winner,
63600-63799 (20 s) for a heading winner. Fresh no-overlay check is 67000-67199.
Known falls 61047 and 61073 are diagnosed and never used as a training set.

  python run_recover.py
"""
import os, sys, json, math, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
os.environ.setdefault("TWIGLET_SCENE", os.path.join(ROOT, "geometry", "scene_v335ac.npz"))
_MODE = sys.argv[-1] if len(sys.argv) > 1 else ""
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
import run_balance as B
from manoeuvre import _model
from simlib import Servo, Gait, stance, reset, randomize, body_rpy, BASE_LEAN, params_path
from episode import run as episode_run, gyro
import mujoco

CONTACT_TRAIN = (63000, 80)
HEAD_TRAIN = (63400, 40)
HEAD_HELD = (63600, 200)
HELD_A = (64000, 200)
HELD_B = (65000, 200)
FLAT = (67000, 200)
PUSH = (67200, 40)
BASE_FALLS = (61047, 61073)

def base(**kw):
    s = B.arm(name="base", balance=True, body_lean=-0.02, k_place=0.6, d_place=0.05, k_hip=-0.25,
              k_lat=0.45, d_lat=0.05, k_roll_extra=0.30, d_roll_extra=0.04,
              slow_yaw_ki=0.12, slow_yaw_ulim=0.02, slow_yaw_ilim=0.5,
              k_load=0.0, k_contact=0.0, phase_yaw=False, anti_windup=False)
    s.update(kw)
    return s

CONTACT = [
    base(name="current"),
    base(name="contact12", k_contact=0.12),
    base(name="contact24", k_contact=0.24),
    base(name="contact_no_extra", k_contact=0.16, k_roll_extra=0.0, d_roll_extra=0.0),
]
HEADING = [
    base(name="current"),
    base(name="antiwindup", anti_windup=True),
    base(name="phase_scale", phase_yaw=True),
    base(name="aw_ulim008", anti_windup=True, slow_yaw_ulim=0.008),
]

def pose_ok(r):
    return ((r["shoulder_pp"] or 0) >= 14 and (r["head_yaw_pp"] or 0) >= 12
            and (r["shoulder_mean"] or 0) >= 18)

def yaw_dist(rows):
    ys = np.degrees([r["yaw_change"] for r in rows])
    return dict(n=int(len(ys)),
                median=float(np.median(ys)),
                p10=float(np.percentile(ys, 10)),
                p90=float(np.percentile(ys, 90)),
                min=float(ys.min()), max=float(ys.max()),
                frac_exceeding_15deg=float(np.mean(np.abs(ys) > 15)),
                frac_abs_gt_8=float(np.mean(np.abs(ys) > 8)))

def hip_sat(rows):
    fr = []
    for r in rows:
        tr = r.get("trace") or []
        if not tr:
            continue
        hy = np.array([abs(p["hip_yaw"]) for p in tr])
        fr.append(float(np.mean(hy >= 0.0195)))
    if not fr:
        return None
    return dict(median=float(np.median(fr)), max=float(np.max(fr)))

def slim(s):
    d = {k: v for k, v in s.items() if k != "fell"}
    d["fell_n"] = len(s.get("fell") or [])
    d["fell"] = s.get("fell") or []
    return d

def soles(m, d):
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

def diagnose_baseline(seed):
    """Replay one no-overlay fall. Do not use the result to pick a gain."""
    from walk_search import KEYS
    x = np.array(B.X, float)
    p = dict(zip(KEYS, x)); p["ramp"] = 1.0
    m, d = _model(None)
    rng = np.random.default_rng(seed)
    randomize(m, rng)
    lat = int(rng.integers(0, 6))
    sv = Servo(m, latency_steps=lat)
    g = Gait(sv.names, p, "v3")
    q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN["v3"])
    reset(m, d, q0)
    mass = float(np.sum(m.body_mass))
    z0 = float(d.subtree_com[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "trunk_assembly")][2])
    snaps = []
    names = ("left_hip_roll", "right_hip_roll", "left_ankle", "right_ankle", "left_hip_yaw", "right_hip_yaw")
    qadr = {n: int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in names}
    act = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in names}
    cmd = {"q": None}

    def policy(t, rpy, gy):
        q = g(t, rpy, gy, q0)
        cmd["q"] = q
        return q

    def on_step(t, dd):
        if int(round(t / 0.02)) % 2:
            return
        rpy = body_rpy(dd)
        gy = gyro(m, dd)
        L, R = soles(m, dd)
        q = cmd["q"]
        snaps.append(dict(
            t=round(t, 3),
            roll=round(float(np.degrees(rpy[0])), 2),
            pitch=round(float(np.degrees(rpy[1])), 2),
            rr=round(float(gy[0]), 3), pr=round(float(gy[1]), 3),
            sin=round(float(math.sin(2 * math.pi * p["f"] * t)), 3),
            Lw=round(L / (mass * 9.81), 3), Rw=round(R / (mass * 9.81), 3),
            z=round(float(dd.subtree_com[0][2]) if False else float(dd.qpos[2]), 3),
            hipL_err=round(float(q[sv.names.index("left_hip_roll")] - dd.qpos[qadr["left_hip_roll"]]), 3),
            hipR_err=round(float(q[sv.names.index("right_hip_roll")] - dd.qpos[qadr["right_hip_roll"]]), 3),
            ankL=round(float(dd.actuator_force[act["left_ankle"]]), 3),
            ankR=round(float(dd.actuator_force[act["right_ankle"]]), 3),
        ))

    info = episode_run(m, d, sv, policy, 10.0, "v3", on_step=on_step)
    roll_hit = next((s for s in snaps if abs(s["roll"]) >= 10), None)
    pitch_hit = next((s for s in snaps if abs(s["pitch"]) >= 10), None)
    return dict(seed=seed, fell=info["fell"], dx=round(float(info["dx"]), 3),
                z0=round(z0, 3), roll_onset=roll_hit, pitch_onset=pitch_hit)

def phase_sign_check():
    """Unrandomized seed 0, 6 s. Body yaw and achieved hip yaw by support half.

    Positive command is the direction the frozen integral uses when yaw has
    drifted positive (command_sign -1 times a negative integrated error).
    """
    from walk_search import KEYS
    x = np.array(B.X, float)
    p = dict(zip(KEYS, x)); p["ramp"] = 1.0
    out = {}
    laws = (
        ("hold0", lambda s: 0.0),
        ("plus_both", lambda s: 0.02),
        ("minus_both", lambda s: -0.02),
        ("plus_weak_only", lambda s: 0.02 if s <= 0.0 else 0.0),
        ("plus_strong_only", lambda s: 0.02 if s > 0.0 else 0.0),
        ("scale_strong", lambda s: 0.02 * (0.15 if s > 0.0 else 1.0)),
    )
    for name, law in laws:
        m, d = _model(None)
        sv = Servo(m, latency_steps=0)
        g = Gait(sv.names, p, "v3")
        q0 = stance(sv.names, p["crouch"], lean=BASE_LEAN["v3"])
        reset(m, d, q0)
        yaw0 = body_rpy(d)[2]
        iy = sv.names.index("left_hip_yaw")
        iy2 = sv.names.index("right_hip_yaw")
        qadr = int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "left_hip_yaw")])
        buckets = {"weak": [], "strong": []}

        def policy(t, rpy, gy, law=law):
            q = g(t, rpy, gy, q0)
            s = math.sin(2 * math.pi * p["f"] * t)
            u = law(s)
            q[iy] = u
            q[iy2] = u
            return q

        def on_step(t, dd):
            if t < 1.0:
                return
            s = math.sin(2 * math.pi * p["f"] * t)
            key = "strong" if s > 0.0 else "weak"
            buckets[key].append(float(dd.qpos[qadr]))

        info = episode_run(m, d, sv, policy, 6.0, "v3", on_step=on_step)
        out[name] = dict(
            fell=info["fell"],
            yaw_deg=round(float(np.degrees(info["yaw"] - yaw0)), 2),
            achieved_weak=round(float(np.mean(buckets["weak"])), 4) if buckets["weak"] else None,
            achieved_strong=round(float(np.mean(buckets["strong"])), 4) if buckets["strong"] else None,
        )
    return out

def run_jobs(js):
    with mp.Pool(4) as pool:
        return pool.map(B.rollout, js, chunksize=2)

def score(name, head, start, n, T=10.0, trace=False):
    rows = run_jobs(B.jobs(start, n, T=T, headarm=head, command_sign=-1.0, keep_trace=trace))
    s = B.summarize(rows)
    s["name"] = name
    s["yaw_dist"] = yaw_dist(rows)
    if trace:
        s["hip_sat"] = hip_sat(rows)
    B.show(name, s)
    print("  yaw", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s["yaw_dist"].items()}, flush=True)
    return s, rows

def main():
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6 or bool(a["fell"]) != (b["fell"] is not None):
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 6), flush=True)
    sign = phase_sign_check()
    print("phase_sign", sign, flush=True)
    falls = [diagnose_baseline(s) for s in BASE_FALLS]
    for row in falls:
        print("basefall", row["seed"], "fell", row["fell"],
              "roll", row["roll_onset"], "pitch", row["pitch_onset"], flush=True)
    with mp.Pool(4) as pool:
        R = W.batch([np.array(B.X)] * FLAT[1], range(FLAT[0], FLAT[0] + FLAT[1]), True, pool, T=10.0)
    fell = [FLAT[0] + i for i, r in enumerate(R) if r["fell"]]
    spd = float(np.mean([r["dx"] / 10 for r in R if not r["fell"]] or [0]))
    print("flat", FLAT, FLAT[1] - len(fell), round(spd, 4), fell, flush=True)
    if FLAT[1] - len(fell) < 197:
        raise SystemExit("flat regression")

    contact_table = []
    for sp in CONTACT:
        s, _ = score("contact " + sp["name"], sp, CONTACT_TRAIN[0], CONTACT_TRAIN[1])
        contact_table.append(s)
    cur_c = contact_table[0]
    contact_kept = [r for r in contact_table if pose_ok(r) and abs(r["yaw_all"]) <= 8
                    and r["succ"] >= cur_c["succ"] + 3
                    and (r["progress_all"] or 0) >= (cur_c["progress_all"] or 0) - 0.01]
    contact_winner = None
    if contact_kept:
        contact_winner = max(contact_kept, key=lambda r: (r["succ"], r["progress_all"] or 0, -abs(r["yaw_all"])))
    print("CONTACT", None if contact_winner is None else contact_winner["name"], flush=True)

    head_table = []
    for sp in HEADING:
        s, _ = score("head " + sp["name"], sp, HEAD_TRAIN[0], HEAD_TRAIN[1], T=20.0, trace=True)
        head_table.append(s)
    cur_h = head_table[0]
    head_kept = []
    for r in head_table[1:]:
        drop = cur_h["yaw_dist"]["frac_exceeding_15deg"] - r["yaw_dist"]["frac_exceeding_15deg"]
        med_ok = abs(r["yaw_dist"]["median"]) <= abs(cur_h["yaw_dist"]["median"]) + 2.0
        if (pose_ok(r) and r["succ"] >= cur_h["succ"] - 2 and drop >= 0.15 and med_ok
                and r["yaw_dist"]["frac_exceeding_15deg"] < cur_h["yaw_dist"]["frac_exceeding_15deg"]):
            head_kept.append(r)
    head_winner = None
    if head_kept:
        head_winner = min(head_kept, key=lambda r: (r["yaw_dist"]["frac_exceeding_15deg"], abs(r["yaw_dist"]["median"])))
    print("HEADING", None if head_winner is None else head_winner["name"], flush=True)

    rep = dict(
        identity_dx=float(b["dx"]),
        phase_sign_check=sign,
        baseline_falls=falls,
        flat=dict(seeds=list(FLAT), succ=FLAT[1] - len(fell), speed=spd, fell=fell),
        contact_train_seeds=list(CONTACT_TRAIN),
        heading_train_seeds=list(HEAD_TRAIN),
        contact_rule="pose gates, |yaw_all|<=8, at least +3/80 survival vs current, progress within 0.01 m/s",
        heading_rule="20 s; pose gates; survival within 2; fraction exceeding ±15 deg drops by at least 0.15; |median| not worse by more than 2 deg",
        contact_train=[slim(r) for r in contact_table],
        heading_train=[slim(r) for r in head_table],
        contact_chosen=None if contact_winner is None else contact_winner["name"],
        heading_chosen=None if head_winner is None else head_winner["name"],
    )

    if contact_winner is not None:
        sp = next(g for g in CONTACT if g["name"] == contact_winner["name"])
        cur = CONTACT[0]
        wave = B.arm(name="wave")
        for tag, start in (("heldA", HELD_A[0]), ("heldB", HELD_B[0])):
            rep[tag + "_winner"] = slim(score(tag + " " + sp["name"], sp, start, 200)[0])
            rep[tag + "_current"] = slim(score(tag + " current", cur, start, 200)[0])
            rep[tag + "_wave"] = slim(score(tag + " wave", wave, start, 200)[0])
            rep[tag + "_walk"] = slim(score(tag + " walk", None, start, 200)[0])
        wA, wB = rep["heldA_winner"], rep["heldB_winner"]
        cA, cB = rep["heldA_current"], rep["heldB_current"]
        if (wA["succ"] > cA["succ"] and wB["succ"] >= cB["succ"]
                and wA["succ"] >= 196 and wB["succ"] >= 196
                and abs(wA["yaw_all"]) <= 8 and abs(wB["yaw_all"]) <= 8):
            push = (4.0, 0.1, 0.0, 2.0)
            rep["push"] = slim(B.summarize(run_jobs(B.jobs(PUSH[0], PUSH[1], headarm=sp, command_sign=-1.0, push=push))))
            rep["push_walk"] = slim(B.summarize(run_jobs(B.jobs(PUSH[0], PUSH[1], push=push))))
            B.show("push", rep["push"])
            B.show("push walk", rep["push_walk"])

    if head_winner is not None:
        sp = next(g for g in HEADING if g["name"] == head_winner["name"])
        cur = HEADING[0]
        sW, _ = score("head held " + sp["name"], sp, HEAD_HELD[0], HEAD_HELD[1], T=20.0, trace=True)
        sC, _ = score("head held current", cur, HEAD_HELD[0], HEAD_HELD[1], T=20.0, trace=True)
        rep["heading_held_winner"] = slim(sW)
        rep["heading_held_current"] = slim(sC)
        rep["heading_held_seeds"] = list(HEAD_HELD)

    rep["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(ROOT, "results", "recover.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, "in", rep["seconds"], flush=True)

def phase_main():
    """Swing-phase lead. Selection block is 68000-68079 unless current falls fewer than 4,
    in which case 68400-68479 is the selection block. Both current scores are kept.
    """
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6:
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 6), flush=True)
    grid = [
        base(name="current"),
        base(name="phase2", k_phase=2.0),
        base(name="phase4", k_phase=4.0),
    ]
    blocks = [(68000, 80), (68400, 80)]
    tables = []
    for start, n in blocks:
        table = []
        for sp in grid:
            s, _ = score("phase %d %s" % (start, sp["name"]), sp, start, n)
            table.append(s)
        tables.append(table)
        if table[0]["n"] - table[0]["succ"] >= 4:
            break
    select = tables[-1]
    cur = select[0]
    kept = [r for r in select[1:] if pose_ok(r) and abs(r["yaw_all"]) <= 8
            and r["succ"] >= cur["succ"] + 3
            and (r["progress_all"] or 0) >= (cur["progress_all"] or 0) - 0.01]
    winner = max(kept, key=lambda r: (r["succ"], r["progress_all"] or 0)) if kept else None
    print("PHASE", None if winner is None else winner["name"], flush=True)
    rep = dict(
        identity_dx=float(b["dx"]),
        blocks=[[slim(r) for r in table] for table in tables],
        chosen=None if winner is None else winner["name"],
        rule="pose gates, |yaw_all|<=8, +3 survival vs current on the selection block, progress within 0.01",
    )
    if winner is not None:
        sp = next(g for g in grid if g["name"] == winner["name"])
        wave = B.arm(name="wave")
        for tag, start in (("heldA", 69000), ("heldB", 70000)):
            rep[tag + "_winner"] = slim(score(tag + " " + sp["name"], sp, start, 200)[0])
            rep[tag + "_current"] = slim(score(tag + " current", grid[0], start, 200)[0])
            rep[tag + "_wave"] = slim(score(tag + " wave", wave, start, 200)[0])
            rep[tag + "_walk"] = slim(score(tag + " walk", None, start, 200)[0])
    rep["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(ROOT, "results", "phase_lead.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, rep["seconds"], flush=True)

if __name__ == "__main__":
    if _MODE == "phase":
        phase_main()
    else:
        main()
