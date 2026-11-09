"""Manoeuvre screen of the frozen early-rate gait. No retune.

Reads results/head843_earlyrate_manoeuvre_protocol.json and runs only those
commands. The npy file is not written.
"""
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

EARLY = "d308c5f003b051b3ddd0b32d15234571bce228eae43843ccc7c86553f067e892"
PROTO = os.path.join(ROOT, "results", "head843_earlyrate_manoeuvre_protocol.json")
OUT = os.path.join(ROOT, "results", "head843_earlyrate_manoeuvre.json")

def seeds_of(span):
    return list(range(span[0], span[1] + 1))

def yaw_deg(row):
    return float(np.degrees(row["yaw_change"]))

def ankle_sat(row):
    j = row.get("joints") or {}
    vals = [j[n]["sat"] for n in ("left_ankle", "right_ankle") if n in j]
    return None if not vals else float(np.mean(vals))

def hip_sat(row):
    j = row.get("joints") or {}
    vals = [j[n]["sat"] for n in ("left_hip_pitch", "right_hip_pitch", "left_hip_yaw", "right_hip_yaw") if n in j]
    return None if not vals else float(np.mean(vals))

def base_jobs(seeds, T, xml):
    z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    if hashlib.sha256(open(os.path.join(ROOT, "params", "head843_earlyrate.npy"), "rb").read()).hexdigest() != EARLY:
        raise SystemExit("earlyrate file changed")
    return E.jobs("early", z, seeds, xml, T)

def attach(js, spec):
    for j in js:
        j["pitch_tail"] = True
        j["measure_path"] = True
        if "delta_deg" in spec:
            j["heading"] = dict(kind="feedback", t0=spec["t0"], t1=spec["t1"],
                                delta=math.radians(spec["delta_deg"]), kp=0.6, kd=0.02, ki=0.0, limit=0.07)
        if "turn_bias_rad" in spec:
            j["turn_bias"] = spec["turn_bias_rad"]
        if "stride_scale" in spec:
            j["stride_scale"] = spec["stride_scale"]
        if "demand" in spec:
            j["demand"] = spec["demand"]
        if "amp" in spec:
            j["amp"] = dict(spec["amp"])
    return js

def task(name, row, spec):
    up = row["fell"] is None
    yd = yaw_deg(row)
    prog = row["dx"] / row["T"]
    if name == "straight" or name.startswith("bias"):
        return up and abs(yd) <= 15.0 and prog >= 0.08
    if "delta_deg" in spec:
        hd = (row.get("heading") or {}).get("heading_err_final_deg")
        delta = spec["delta_deg"]
        tracked = hd is not None and abs(hd) <= 15.0 and (yd * delta) > 0.0 and abs(yd) >= 0.5 * abs(delta)
        return bool(up and tracked)
    if name.startswith("speed") or name.startswith("demand"):
        scale = spec.get("stride_scale", spec.get("demand"))
        target = 0.11 * scale
        return up and abs(yd) <= 20.0 and abs(prog - target) <= 0.25 * abs(target)
    if name.startswith("stop"):
        st = row.get("stop") or {}
        before = st.get("speed_before_stop")
        after = st.get("speed_after_settle")
        disp = st.get("disp_after_stop_m")
        return bool(up and before is not None and before > 0.05 and after is not None and after < 0.03 and disp is not None and disp < 0.15)
    if name == "reverse":
        return up and prog < -0.04
    return False

def slim(row, name, spec):
    hd = row.get("heading") or {}
    st = row.get("stop") or {}
    return dict(
        seed=int(row["seed"]), fell=None if row["fell"] is None else float(row["fell"]),
        dx=round(float(row["dx"]), 3), dy=round(float(row["dy"]), 3),
        yaw_deg=round(yaw_deg(row), 2),
        prog=round(float(row["dx"] / row["T"]), 4),
        path_m=round(float(row.get("path_m") or 0.0), 3),
        min_pitch=None if not row.get("pitch_tail") else round(row["pitch_tail"].get("min_deg", 0.0), 2),
        heading_err_final_deg=None if hd.get("heading_err_final_deg") is None else round(hd["heading_err_final_deg"], 2),
        heading_err_rms_deg=None if hd.get("heading_err_rms_deg") is None else round(hd["heading_err_rms_deg"], 2),
        cross_after_m=None if hd.get("crosstrack_rms_after_slew_m") is None else round(hd["crosstrack_rms_after_slew_m"], 3),
        speed_before=None if st.get("speed_before_stop") is None else round(st["speed_before_stop"], 4),
        speed_after=None if st.get("speed_after_settle") is None else round(st["speed_after_settle"], 4),
        disp_after=None if st.get("disp_after_stop_m") is None else round(st["disp_after_stop_m"], 3),
        ankle_sat=ankle_sat(row), hip_sat=hip_sat(row),
        task=bool(task(name, row, spec)),
        upright=row["fell"] is None,
    )

def run_spec(spec, xml):
    seeds = seeds_of(spec["seeds"])
    js = attach(base_jobs(seeds, spec["T"], xml), spec)
    rows = V.Y.run_jobs(js)
    slim_rows = [slim(r, spec["name"], spec) for r in rows]
    n = len(slim_rows)
    n_task = sum(1 for r in slim_rows if r["task"])
    n_up = sum(1 for r in slim_rows if r["upright"])
    ys = [r["yaw_deg"] for r in slim_rows]
    return dict(name=spec["name"], n=n, upright=n_up, task=n_task,
                yaw_median=round(float(np.median(ys)), 2),
                prog_median=round(float(np.median([r["prog"] for r in slim_rows])), 4),
                rows=slim_rows)

def main():
    proto = json.load(open(PROTO))
    screens = []
    for spec in proto["screens"]:
        block = run_spec(spec, H.NOM)
        screens.append(block)
        print(spec["name"], f"task {block['task']}/{block['n']}", f"up {block['upright']}/{block['n']}",
              "yaw", block["yaw_median"], "prog", block["prog_median"], flush=True)
    by = {b["name"]: b for b in screens}
    held = []
    rules = proto["heldout_only_if_screen_task_is_perfect"]
    for name, rule in rules.items():
        screen = by[name]
        if screen["task"] != screen["n"]:
            print("heldout skipped", name, flush=True)
            continue
        spec = dict(next(s for s in proto["screens"] if s["name"] == name))
        spec["seeds"] = rule["seeds"]
        spec["name"] = name + "_held"
        block = run_spec(spec, H.NOM)
        held.append(block)
        print(spec["name"], f"task {block['task']}/{block['n']}", "yaw", block["yaw_median"], flush=True)
    bounds = []
    bound_map = proto["bounds_only_if_nominal_screen_task_is_perfect"]
    for spec in proto["screens"]:
        screen = by[spec["name"]]
        slots = bound_map.get(spec["name"]) if isinstance(bound_map, dict) else None
        if not slots or screen["task"] != screen["n"]:
            continue
        for tag, xml in (("lo", H.LO), ("hi", H.HI)):
            bspec = dict(spec)
            bspec["name"] = spec["name"] + "_" + tag
            bspec["seeds"] = slots[tag]
            bounds.append(run_spec(bspec, xml))
            print(bspec["name"], f"task {bounds[-1]['task']}/{bounds[-1]['n']}", flush=True)
    json.dump(dict(protocol=PROTO, screens=screens, heldout=held, bounds=bounds), open(OUT, "w"), indent=1)
    print("wrote", OUT, flush=True)

if __name__ == "__main__":
    main()
