"""Preregistered qualification of the onset right-stance flip. No retune."""
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

PREREG = os.path.join(ROOT, "results", "head843_manoeuvre_d_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_manoeuvre_d_val.json")
CFG = os.path.join(ROOT, "params", "head843_manoeuvre_cfg_d.json")
NPY = os.path.join(ROOT, "params", "head843_earlyrate.npy")

def jobs_for(block, seeds, xml):
    z = np.load(NPY)
    js = E.jobs("early", z, seeds, xml, block["T"])
    kind = block["kind"]
    for j in js:
        if kind in ("slew", "slalom"):
            j["keep_trace"] = True
        if kind == "slew":
            j["heading"] = dict(kind="feedback", t0=block["t0"], t1=block["t1"],
                                delta=math.radians(block["delta_deg"]), kp=0.6, kd=0.02, ki=0.0, limit=0.07,
                                k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True, yaw_alloc="right_stance_onset")
        elif kind == "slalom":
            j["heading"] = dict(kind="route", k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True,
                                yaw_alloc="right_stance_onset", segments=[
                                    {"t0": 2, "t1": 7, "yaw_deg": 20}, {"t0": 7, "t1": 12, "yaw_deg": 0},
                                    {"t0": 12, "t1": 17, "yaw_deg": -20}, {"t0": 17, "t1": 22, "yaw_deg": 0}])
    return js

def slim(block, row):
    ok, info = B.passed(block, row)
    j = row.get("joints") or {}
    anks = [j[n]["sat"] for n in ("left_ankle", "right_ankle") if n in j]
    out = dict(seed=int(row["seed"]), fell=None if row["fell"] is None else round(float(row["fell"]), 3),
               task=bool(ok), ankle_sat=None if not anks else round(float(np.mean(anks)), 4),
               min_pitch=None if not row.get("pitch_tail") else round(row["pitch_tail"].get("min_deg", 0.0), 2))
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
    st = json.load(open(OUT)) if os.path.exists(OUT) else {"blocks": {}, "pending": [b["name"] for b in pre["blocks"]]}
    for block in pre["blocks"]:
        name = block["name"]
        seeds = list(range(block["seeds"][0], block["seeds"][1] + 1))
        have = {r["seed"] for r in st["blocks"].get(name, [])}
        todo = [s for s in seeds if s not in have]
        print(name, "todo", len(todo), flush=True)
        chunk = 50 if block["T"] >= 20 else 100
        for i in range(0, len(todo), chunk):
            part = todo[i:i + chunk]
            rows = V.Y.run_jobs(jobs_for(block, part, H.NOM))
            st["blocks"].setdefault(name, []).extend(slim(block, r) for r in rows)
            st["blocks"][name].sort(key=lambda r: r["seed"])
            json.dump(st, open(OUT, "w"))
            k = sum(1 for r in st["blocks"][name] if r["task"])
            print(name, "done", len(st["blocks"][name]), "task", k, flush=True)
        if name in st.get("pending", []):
            st["pending"].remove(name)
        json.dump(st, open(OUT, "w"))
    summary = {}
    for block in pre["blocks"]:
        rows = st["blocks"][block["name"]]
        k = sum(1 for r in rows if r["task"])
        w = B.wilson(k, len(rows))
        gate = block["n"] >= 1000
        summary[block["name"]] = dict(task=k, n=len(rows), wilson=w,
                                      met=bool(gate and len(rows) == block["n"] and w[1] >= 0.995),
                                      falls=[r["seed"] for r in rows if r["fell"] is not None])
        print("SUM", block["name"], f"{k}/{len(rows)}", [round(x, 5) for x in w], "met", summary[block["name"]]["met"], flush=True)
    st["summary"] = summary
    json.dump(st, open(OUT, "w"))
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
