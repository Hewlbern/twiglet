"""Diagnostic only. Does not write a qualification."""
import os, sys, math
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

def go(seeds, T, heading=None, amp=None, kff=0.0, xml=H.NOM):
    z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    js = E.jobs("early", z, seeds, xml, T)
    for j in js:
        if heading:
            h = dict(heading)
            if kff:
                h["k_yaw_ff"] = kff
            j["heading"] = h
        if amp:
            j["amp"] = dict(amp)
    rows = V.Y.run_jobs(js)
    for r in rows:
        hd = r.get("heading") or {}
        print(r["seed"], "fell", r["fell"], "dx", round(r["dx"], 3),
              "yaw", round(math.degrees(r["yaw_change"]), 1),
              "err", None if hd.get("heading_err_final_deg") is None else round(hd["heading_err_final_deg"], 1),
              flush=True)
    return rows

def main():
    print("FINGERPRINT", flush=True)
    go([214000, 214001], 10.0)
    print("GRID", flush=True)
    cases = [
        ("p45fast", 3.0, 6.0, 45, 0.20),
        ("n45fast", 3.0, 6.0, -45, 0.20),
        ("p45slow", 3.0, 8.0, 45, 0.15),
        ("n45slow", 3.0, 8.0, -45, 0.15),
        ("p90", 2.5, 8.5, 90, 0.20),
        ("n90", 2.5, 8.5, -90, 0.20),
    ]
    for name, t0, t1, deg, kff in cases:
        print(name, flush=True)
        h = dict(kind="feedback", t0=t0, t1=t1, delta=math.radians(deg), kp=0.6, kd=0.02, ki=0.0, limit=0.07)
        go(list(range(232200, 232204)), 12.0, h, kff=kff)

if __name__ == "__main__":
    main()
