"""Preregistered cfg_h qualification. No retune, no pooling with earlier hashes."""
import os, sys, json, math, hashlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_earlyrate as E
import run_head843_heading as H
import run_head843_shortbal_val as V
import run_head843_manoeuvre_b_val as B

PREREG = os.path.join(ROOT, "results", "head843_manoeuvre_h_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_manoeuvre_h_val.json")
CFG = os.path.join(ROOT, "params", "head843_manoeuvre_cfg_h.json")
NPY = os.path.join(ROOT, "params", "head843_earlyrate.npy")
SL = [{"t0": 2, "t1": 7, "yaw_deg": 20}, {"t0": 7, "t1": 12, "yaw_deg": 0},
      {"t0": 12, "t1": 17, "yaw_deg": -20}, {"t0": 17, "t1": 22, "yaw_deg": 0}]

def heading():
    return dict(k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True, yaw_alloc="right_stance_onset",
                step_guard=True, stance_roll_support=True, neg_onset_gate=True)

def jobs_for(block, seeds, xml):
    z = np.load(NPY)
    js = E.jobs("early", z, seeds, xml, block["T"])
    kind = block["kind"]
    for j in js:
        if kind in ("slew", "slalom", "restart"):
            j["keep_trace"] = True
        if kind == "slew":
            h = heading()
            h.update(kind="feedback", t0=block["t0"], t1=block["t1"],
                     delta=math.radians(block["delta_deg"]), kp=0.6, kd=0.02, ki=0.0, limit=0.07)
            j["heading"] = h
        elif kind == "slalom":
            h = heading()
            h.update(kind="route", segments=SL)
            j["heading"] = h
        elif kind == "stop":
            j["amp"] = dict(kind="baseline_then_phase_stop", t_stop=6.0, ramp_cycles=1.0)
        elif kind == "restart":
            j["amp"] = dict(kind="restart", cycles=[[0.0, 4.5], [8.0, 12.0]], ramp_s=1.0, ramp_cycles=1.0)
        elif kind == "speed":
            j["stride_scale"] = block["scale"]
    return js

def slim(block, row):
    ok, info = B.passed(block, row)
    out = dict(seed=int(row["seed"]), fell=None if row["fell"] is None else round(float(row["fell"]), 3), task=bool(ok))
    if isinstance(info, dict):
        out.update(info)
    if block["kind"] == "straight" and row.get("motion_pp_deg"):
        out["motion_pp"] = row["motion_pp_deg"]
        out["motion_mean"] = row["motion_mean_deg"]
    return out

def main():
    pre = json.load(open(PREREG))
    man = hashlib.sha256(open(os.path.join(HERE, "manoeuvre.py"), "rb").read()).hexdigest()
    cfg = hashlib.sha256(open(CFG, "rb").read()).hexdigest()
    npy = hashlib.sha256(open(NPY, "rb").read()).hexdigest()
    if man != pre["candidate"]["manoeuvre_sha256"]:
        raise SystemExit("manoeuvre changed " + man)
    if cfg != pre["candidate"]["cfg_sha256"]:
        raise SystemExit("cfg changed " + cfg)
    if npy != pre["candidate"]["base_npy_sha256"]:
        raise SystemExit("npy changed " + npy)
    st = json.load(open(OUT)) if os.path.exists(OUT) else {"blocks": {}}
    for block in pre["blocks"]:
        name = block["name"]
        seeds = list(range(block["seeds"][0], block["seeds"][1] + 1))
        have = {r["seed"] for r in st["blocks"].get(name, [])}
        todo = [s for s in seeds if s not in have]
        print(name, "todo", len(todo), flush=True)
        for i in range(0, len(todo), 40):
            rows = V.Y.run_jobs(jobs_for(block, todo[i:i + 40], H.NOM))
            st["blocks"].setdefault(name, []).extend(slim(block, r) for r in rows)
            st["blocks"][name].sort(key=lambda r: r["seed"])
            json.dump(st, open(OUT, "w"))
            k = sum(1 for r in st["blocks"][name] if r["task"])
            print(name, "done", len(st["blocks"][name]), "task", k, flush=True)
    summary = {}
    for block in pre["blocks"]:
        rows = st["blocks"][block["name"]]
        k = sum(1 for r in rows if r["task"])
        w = B.wilson(k, len(rows))
        gate = block["n"] >= 1000
        summary[block["name"]] = dict(task=k, n=len(rows), wilson=w,
                                      met=bool(gate and len(rows) == block["n"] and w[1] >= 0.995),
                                      falls=[r["seed"] for r in rows if r["fell"] is not None],
                                      misses=[r["seed"] for r in rows if not r["task"]])
        print("SUM", block["name"], f"{k}/{len(rows)}", [round(x, 5) for x in w], "met", summary[block["name"]]["met"], flush=True)
    bounds = {}
    for name, slot in pre.get("bounds_if_that_block_perfect", {}).items():
        if not summary.get(name, {}).get("met"):
            continue
        block = next(b for b in pre["blocks"] if b["name"] == name)
        for tag, xml in (("lo", H.LO), ("hi", H.HI)):
            seeds = list(range(slot[tag][0], slot[tag][1] + 1))
            rows = [slim(block, r) for r in V.Y.run_jobs(jobs_for(block, seeds, xml))]
            k = sum(1 for r in rows if r["task"])
            bounds[f"{name}_{tag}"] = dict(task=k, n=len(rows), wilson=B.wilson(k, len(rows)),
                                           note="100-seed mass screen. Not a 99.5% mass claim.")
            print("BOUND", name, tag, f"{k}/{len(rows)}", flush=True)
    st["summary"] = summary
    st["bounds"] = bounds
    json.dump(st, open(OUT, "w"))
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
