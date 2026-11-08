"""Reachable swing-foot identification and paired yaw-authority identification.

Diagnostic falls are already-known coordinated-wave misses. They are not a
training set. Fresh identification seeds are 71200-71205 (hip-roll latch),
71400-71405 (nominal swings), and 71600-71607 (yaw pairs). No controller is
selected here.

  python run_reach.py
"""
import os, sys, json, math
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
import run_balance as B
import run_recover as R
from simlib import params_path

DIAG = [58012, 58028, 58035, 58062, 58125, 68011, 68013, 68017]
NOMINAL = list(range(71400, 71406))
REACH = list(range(71200, 71206))
YAW = list(range(71600, 71608))

def half_cycles(samples):
    """Full half steps from one sin zero crossing to the next. Touchdown is the
    first loaded sample after the sole has actually been airborne."""
    if len(samples) < 5:
        return []
    w = float(np.median([s["Lw"] + s["Rw"] for s in samples])) or 1.0
    f = 2.214965
    cuts = [0]
    prev = math.sin(2 * math.pi * f * samples[0]["t"]) > 0
    for i, s in enumerate(samples):
        pos = math.sin(2 * math.pi * f * s["t"]) > 0
        if pos != prev:
            cuts.append(i)
            prev = pos
    cuts.append(len(samples))
    out = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 4:
            continue
        seg = samples[a:b]
        pos = math.sin(2 * math.pi * f * seg[0]["t"]) > 0
        side = "L" if pos else "R"
        joint = "left_hip_roll" if side == "L" else "right_hip_roll"
        force = "Lw" if side == "L" else "Rw"
        foot = "footL" if side == "L" else "footR"
        air = [s for s in seg if s[force] < 0.15 * w]
        if len(air) < 3:
            continue
        td = next((s for s in seg if s["t"] > air[-1]["t"] and s[force] > 0.40 * w), None)
        end = td or air[-1]
        s0 = seg[0]
        dt = seg[1]["t"] - s0["t"]
        vy = (seg[1]["comy"] - s0["comy"]) / dt if dt > 0 else 0.0
        cmds = [s["cmd"][joint] for s in air]
        taus = [abs(s["tauL"] if side == "L" else s["tauR"]) for s in air]
        out.append(dict(
            t=round(s0["t"], 3), side=side,
            dur=round(end["t"] - s0["t"], 3),
            air=round(air[-1]["t"] - air[0]["t"], 3),
            roll0=round(math.degrees(s0["roll"]), 2),
            rr0=round(s0["rr"], 3),
            pitch0=round(math.degrees(s0["pitch"]), 2),
            vy0=round(vy, 3),
            cmd_air=round(float(np.mean(cmds)), 4),
            ach0=round(s0["ach"][joint], 4),
            ach_end=round(end["ach"][joint], 4),
            foot_y=round(end[foot][1] - end["comy"], 4),
            tau_peak=round(float(max(taus)), 3),
        ))
    return out

def fall_mode(samples, fell):
    """Which angle reaches 10° first on a coordinated-wave fall. Not a contact test."""
    if fell is None:
        return None
    pitch = next((s for s in samples if abs(math.degrees(s["pitch"])) >= 10 and s["t"] <= fell), None)
    roll = next((s for s in samples if abs(math.degrees(s["roll"])) >= 10 and s["t"] <= fell), None)
    def brief(s):
        if s is None:
            return None
        return dict(t=round(s["t"], 3), pitch=round(math.degrees(s["pitch"]), 1),
                    roll=round(math.degrees(s["roll"]), 1), rr=round(s["rr"], 2))
    kind = "none"
    if pitch and (roll is None or pitch["t"] <= roll["t"]):
        kind = "pitch_first"
    elif roll:
        kind = "roll_first"
    return dict(kind=kind, pitch=brief(pitch), roll=brief(roll))

def summarize_swings(rows, label):
    sw = []
    for r in rows:
        sw.extend(half_cycles(r.get("capture") or []))
    if not sw:
        return dict(label=label, n=0)
    gap = np.array([s["cmd_air"] - s["ach_end"] for s in sw])
    return dict(
        label=label, n=len(sw),
        air_med=float(np.median([s["air"] for s in sw])),
        cmd_minus_ach_med=float(np.median(gap)),
        cmd_minus_ach_p90=float(np.percentile(np.abs(gap), 90)),
        roll0_med=float(np.median([abs(s["roll0"]) for s in sw])),
        pitch0_med=float(np.median([abs(s["pitch0"]) for s in sw])),
        vy0_med=float(np.median(np.abs([s["vy0"] for s in sw]))),
        tau_p90=float(np.percentile([s["tau_peak"] for s in sw], 90)),
    )

def main():
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6:
        raise SystemExit("no-overlay path changed")
    print("identity", round(b["dx"], 6), flush=True)
    cur = R.base(name="current")
    jobs = []
    for seed in DIAG + NOMINAL:
        jobs.append(dict(x=B.X, seed=seed, rand=True, T=8.0, headarm=cur, command_sign=-1.0,
                         measure_path=True, capture=True, tag="nominal"))
    for seed in REACH:
        for amp in (0.0, 0.10, -0.10, 0.16):
            sp = R.base(name="latch")
            sp["latch_probe"] = dict(amp=amp)
            jobs.append(dict(x=B.X, seed=seed, rand=True, T=4.0, headarm=sp, command_sign=-1.0,
                             measure_path=True, capture=True, tag="reach", latch_amp=amp))
    yaw_kinds = [
        ("base", None),
        ("hip+", dict(kind="hip_both", amp=0.03)),
        ("hip-", dict(kind="hip_both", amp=-0.03)),
        ("stance+", dict(kind="hip_stance", amp=0.03)),
        ("stance-", dict(kind="hip_stance", amp=-0.03)),
        ("step+", dict(kind="step_diff", amp=0.04)),
        ("step-", dict(kind="step_diff", amp=-0.04)),
    ]
    for seed in range(71700, 71708):
        for name, amp in (("base", None), ("st+8", 0.008), ("st-8", -0.008), ("st+15", 0.015), ("st-15", -0.015)):
            sp = R.base(name=name)
            if amp is not None:
                sp["yaw_probe"] = dict(kind="hip_stance", amp=amp)
            jobs.append(dict(x=B.X, seed=seed, rand=True, T=6.0, headarm=sp, command_sign=-1.0,
                             measure_path=True, tag="yaw", yname=name))
    for seed in YAW:
        for name, yp in yaw_kinds:
            sp = R.base(name=name)
            if yp:
                sp["yaw_probe"] = yp
            jobs.append(dict(x=B.X, seed=seed, rand=True, T=6.0, headarm=sp, command_sign=-1.0,
                             measure_path=True, tag="yaw", yname=name))
    with mp.Pool(4) as pool:
        rows = pool.map(B.rollout, jobs, chunksize=1)
    by = {}
    for job, row in zip(jobs, rows):
        row["tag"] = job["tag"]
        row["amp"] = job.get("latch_amp")
        row["yname"] = job.get("yname")
        by.setdefault(job["tag"], []).append(row)

    diag = [r for r in by["nominal"] if r["seed"] in DIAG]
    nom = [r for r in by["nominal"] if r["seed"] in NOMINAL]
    print("diag falls", [(r["seed"], r["fell"]) for r in diag], flush=True)
    print("nominal", [(r["seed"], r["fell"]) for r in nom], flush=True)
    rep = dict(
        identity_dx=float(b["dx"]),
        note="Identification only. Known fall seeds are not a training set. Single support is not treated as a contact failure.",
        diag_swings=summarize_swings(diag, "known wave falls"),
        nominal_swings=summarize_swings(nom, "fresh nominal"),
    )
    # Paired reach: same seed, amp 0.10 and -0.10 minus amp 0, achieved hip at touchdown.
    reach = {}
    for r in by["reach"]:
        reach.setdefault(r["seed"], {})[r["amp"]] = half_cycles(r.get("capture") or [])
    paired = []
    for seed, amps in reach.items():
        base = amps.get(0.0) or []
        for amp in (0.10, -0.10, 0.16):
            alt = amps.get(amp) or []
            n = min(len(base), len(alt))
            for i in range(n):
                if base[i]["side"] != alt[i]["side"]:
                    continue
                if base[i]["air"] < 0.08 or alt[i]["air"] < 0.08:
                    continue
                paired.append(dict(
                    seed=seed, amp=amp, side=base[i]["side"],
                    d_ach=round(alt[i]["ach_end"] - base[i]["ach_end"], 4),
                    d_cmd=round(alt[i]["cmd_air"] - base[i]["cmd_air"], 4),
                    d_foot_y=round(alt[i]["foot_y"] - base[i]["foot_y"], 4),
                    tau=alt[i]["tau_peak"],
                ))
    def pack(amp):
        sub = [p for p in paired if p["amp"] == amp]
        if not sub:
            return dict(n=0)
        d_ach = np.array([p["d_ach"] for p in sub])
        d_cmd = np.array([p["d_cmd"] for p in sub], float)
        ratio = [p["d_ach"] / p["d_cmd"] for p in sub if abs(p["d_cmd"]) > 0.02]
        return dict(
            n=len(sub),
            d_ach_med=float(np.median(d_ach)),
            d_cmd_med=float(np.median(d_cmd)),
            frac_reached=None if not ratio else float(np.median(ratio)),
            d_foot_y_mm=float(np.median([p["d_foot_y"] for p in sub]) * 1000),
            tau_p90=float(np.percentile([p["tau"] for p in sub], 90)),
        )
    rep["reach_paired"] = {"plus_0.10": pack(0.10), "minus_0.10": pack(-0.10), "plus_0.16": pack(0.16)}
    print("reach", rep["reach_paired"], flush=True)

    yaw = {}
    for r in by["yaw"]:
        yaw.setdefault(r["yname"], []).append(r)
    base_y = {r["seed"]: r for r in yaw["base"]}
    yaw_rep = {}
    for name, rs in yaw.items():
        dys, survived, speeds = [], 0, []
        for r in rs:
            b0 = base_y[r["seed"]]
            dys.append(math.degrees(r["yaw_change"] - b0["yaw_change"]))
            survived += r["fell"] is None
            if r["speed"] is not None:
                speeds.append(r["speed"])
        arr = np.array(dys)
        yaw_rep[name] = dict(
            n=len(rs), up=survived,
            dyaw_med=float(np.median(arr)),
            dyaw_min=float(arr.min()), dyaw_max=float(arr.max()),
            n_pos=int(np.sum(arr > 1.0)), n_neg=int(np.sum(arr < -1.0)),
            speed_med=None if not speeds else float(np.median(speeds)),
        )
        print("yaw", name, yaw_rep[name], flush=True)
    rep["yaw_paired_vs_base"] = yaw_rep
    rep["wave_fall_modes"] = {str(r["seed"]): fall_mode(r.get("capture") or [], r["fell"]) for r in diag}
    rep["diag_last_swings"] = {str(r["seed"]): half_cycles(r.get("capture") or [])[-2:] for r in diag}
    path = os.path.join(ROOT, "results", "reach_id.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, flush=True)

if __name__ == "__main__":
    main()
