"""Development screen for the timed heading handoff. Not a qualification.

Declared before these seeds ran:
- The reset integrator stays on until the heading command is moving faster than
  2 deg/s, and it returns once the command has stopped and the error is under 6 deg.
- Turns use the same k_yaw_ff 0.20 and k_yaw_p 0.45 as cfg_b, same hip sign.
- A 180 deg command is 6 deg/s (t0=2, t1=32, T=36), which is under the ~7 deg/s
  body rate measured on the 10 deg/s misses. The 4 s after the slew is the same
  budget the 10 deg/s block used. It is not an added settle.
- A restart after the first walk begins at the next double-support edge.
Seeds 251000+ are new. cfg_b results are not reread or rescored.
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
import run_head843_manoeuvre_b_val as B
import run_head843_heading as H
import run_head843_shortbal_val as V

OUT = os.path.join(ROOT, "results", "head843_manoeuvre_c_screen.json")

BLOCKS = [
    dict(name="p20", kind="slew", T=10, t0=3, t1=8, delta_deg=20, seeds=(251000, 251031)),
    dict(name="m20", kind="slew", T=10, t0=3, t1=8, delta_deg=-20, seeds=(251032, 251063)),
    dict(name="p45", kind="slew", T=10, t0=3, t1=6, delta_deg=45, seeds=(251064, 251095)),
    dict(name="m45", kind="slew", T=10, t0=3, t1=6, delta_deg=-45, seeds=(251096, 251127)),
    dict(name="p90", kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=90, seeds=(251128, 251159)),
    dict(name="m90", kind="slew", T=12, t0=2.5, t1=8.5, delta_deg=-90, seeds=(251160, 251191)),
    dict(name="p180_6dps", kind="slew", T=36, t0=2, t1=32, delta_deg=180, seeds=(251192, 251215)),
    dict(name="m180_6dps", kind="slew", T=36, t0=2, t1=32, delta_deg=-180, seeds=(251216, 251239)),
    dict(name="restart", kind="restart", T=14, seeds=(251240, 251271)),
    dict(name="slalom", kind="slalom", T=24, seeds=(251272, 251303)),
    dict(name="straight10", kind="straight", T=10, seeds=(251304, 251335)),
    dict(name="stop", kind="stop", T=12, seeds=(251336, 251343)),
    dict(name="slow", kind="speed", T=10, scale=0.7, seeds=(251344, 251351)),
]

def main():
    man = hashlib.sha256(open(os.path.join(HERE, "manoeuvre.py"), "rb").read()).hexdigest()
    st = {"written": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "role": "development_screen_not_qualification",
          "manoeuvre_sha256": man, "blocks": {}}
    for block in BLOCKS:
        seeds = list(range(block["seeds"][0], block["seeds"][1] + 1))
        print(block["name"], "n", len(seeds), flush=True)
        rows = []
        for i in range(0, len(seeds), 8):
            part = seeds[i:i + 8]
            got = V.Y.run_jobs(B.jobs_for(block, part, H.NOM))
            rows.extend(B.slim(block, r) for r in got)
            k = sum(1 for r in rows if r["task"])
            print(" ", block["name"], len(rows), k, flush=True)
        st["blocks"][block["name"]] = rows
        json.dump(st, open(OUT, "w"))
    for name, rows in st["blocks"].items():
        k = sum(1 for r in rows if r["task"])
        fails = [r for r in rows if not r["task"]]
        print("SUM", name, f"{k}/{len(rows)}", "fails", [(f["seed"], f.get("fell"), f.get("err_deg"), f.get("wrong_deg"), f.get("yaw_deg")) for f in fails], flush=True)
    print("DONE", OUT, flush=True)

if __name__ == "__main__":
    main()
