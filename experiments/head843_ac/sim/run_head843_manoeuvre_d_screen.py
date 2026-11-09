"""Development screen for the onset right-stance flip. Not a qualification.

Declared before these seeds:
- cfg_c handoff stays (integrator on until the command exceeds 2 deg/s).
- The phase-selected hip still gets the full 0.45 proportional and 0.20 feedforward.
- For the first 0.40 s after the command rate rises through 2 deg/s, if that hip
  is the right hip and the right sole has more than 55% of the sole load, the
  sign is flipped. After 0.40 s the sign matches cfg_c. Gains are not reduced.
- 0.40 s is the measured window of the opposite peak (0.26-0.36 s into the slew).
Seeds 264000+ are new. The always-on flip screen remains in head843_manoeuvre_d_screen.json.
"""
import os, sys, json, math, hashlib
from datetime import datetime, timezone
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

OUT = os.path.join(ROOT, "results", "head843_manoeuvre_d_onset_screen.json")
ALLOC = "right_stance_onset"

BLOCKS = [
    dict(name="m20", kind="slew", T=10, t0=3, t1=8, delta_deg=-20, seeds=(264000, 264031)),
    dict(name="m45", kind="slew", T=10, t0=3, t1=6, delta_deg=-45, seeds=(264032, 264063)),
    dict(name="m90", kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=-90, seeds=(264064, 264095)),
    dict(name="p20", kind="slew", T=10, t0=3, t1=8, delta_deg=20, seeds=(264096, 264127)),
    dict(name="p45", kind="slew", T=10, t0=3, t1=6, delta_deg=45, seeds=(264128, 264159)),
    dict(name="p90", kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=90, seeds=(264160, 264191)),
    dict(name="p180_6dps", kind="slew", T=36, t0=2, t1=32, delta_deg=180, seeds=(264192, 264207)),
    dict(name="m180_6dps", kind="slew", T=36, t0=2, t1=32, delta_deg=-180, seeds=(264208, 264223)),
    dict(name="slalom", kind="slalom", T=24, seeds=(264224, 264239)),
    dict(name="straight10", kind="straight", T=10, seeds=(264240, 264255)),
]

def jobs_for(block, seeds, xml):
    z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    js = E.jobs("early", z, seeds, xml, block["T"])
    kind = block["kind"]
    for j in js:
        if kind in ("slew", "slalom"):
            j["keep_trace"] = True
        if kind == "slew":
            j["heading"] = dict(kind="feedback", t0=block["t0"], t1=block["t1"],
                                delta=math.radians(block["delta_deg"]), kp=0.6, kd=0.02, ki=0.0, limit=0.07,
                                k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True, yaw_alloc=ALLOC)
        elif kind == "slalom":
            j["heading"] = dict(kind="route", k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True,
                                yaw_alloc=ALLOC, segments=[
                                    {"t0": 2, "t1": 7, "yaw_deg": 20}, {"t0": 7, "t1": 12, "yaw_deg": 0},
                                    {"t0": 12, "t1": 17, "yaw_deg": -20}, {"t0": 17, "t1": 22, "yaw_deg": 0}])
        elif kind == "stop":
            j["amp"] = dict(kind="baseline_then_phase_stop", t_stop=6.0, ramp_cycles=1.0)
        elif kind == "speed":
            j["stride_scale"] = block["scale"]
    return js

def main():
    man = hashlib.sha256(open(os.path.join(HERE, "manoeuvre.py"), "rb").read()).hexdigest()
    st = {"written": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "role": "development_screen_not_qualification",
          "yaw_alloc": ALLOC,
          "onset_s": 0.40,
          "manoeuvre_sha256": man, "blocks": {}}
    for block in BLOCKS:
        seeds = list(range(block["seeds"][0], block["seeds"][1] + 1))
        print(block["name"], "n", len(seeds), flush=True)
        rows = []
        for i in range(0, len(seeds), 8):
            got = V.Y.run_jobs(jobs_for(block, seeds[i:i + 8], H.NOM))
            rows.extend(B.slim(block, r) for r in got)
            print(" ", block["name"], len(rows), sum(1 for r in rows if r["task"]), flush=True)
        st["blocks"][block["name"]] = rows
        json.dump(st, open(OUT, "w"))
    for name, rows in st["blocks"].items():
        fails = [r for r in rows if not r["task"]]
        print("SUM", name, f"{len(rows)-len(fails)}/{len(rows)}",
              [(f["seed"], f.get("fell"), f.get("err_deg"), f.get("wrong_deg"), f.get("yaw_deg")) for f in fails], flush=True)
    print("DONE", OUT, flush=True)

if __name__ == "__main__":
    main()
