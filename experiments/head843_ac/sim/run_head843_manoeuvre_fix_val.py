"""Fixed validation of the heading-schedule candidate. No retune."""
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

PREREG = os.path.join(ROOT, "results", "head843_manoeuvre_fix_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_manoeuvre_fix_val.json")

def yaw_deg(row):
    return float(np.degrees(row["yaw_change"]))

def series(tr):
    if not tr:
        return []
    y0 = tr[0]["yaw"]
    out = []
    for p in tr:
        a = p["yaw"] - y0
        out.append((p["t"], math.degrees((a + math.pi) % (2 * math.pi) - math.pi), p["x"], p["y"]))
    return out

def gap_speed(tr, t0, t1):
    xs = [p for p in series(tr) if t0 <= p[0] <= t1]
    if len(xs) < 2:
        return None
    dist = sum(math.hypot(b[2] - a[2], b[3] - a[3]) for a, b in zip(xs, xs[1:]))
    return dist / (xs[-1][0] - xs[0][0])

def jobs_for(block, seeds, xml):
    z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    js = E.jobs("early", z, seeds, xml, block["T"])
    kind = block["kind"]
    for j in js:
        j["keep_trace"] = kind in ("slalom", "restart")
        if kind == "slew":
            j["heading"] = dict(kind="feedback", t0=block["t0"], t1=block["t1"],
                                delta=math.radians(block["delta_deg"]), kp=0.6, kd=0.02, ki=0.0, limit=0.07,
                                k_yaw_ff=0.20)
        elif kind == "slalom":
            j["heading"] = dict(kind="route", k_yaw_ff=0.20, segments=[
                {"t0": 2, "t1": 7, "yaw_deg": 20}, {"t0": 7, "t1": 12, "yaw_deg": 0},
                {"t0": 12, "t1": 17, "yaw_deg": -20}, {"t0": 17, "t1": 22, "yaw_deg": 0}])
        elif kind == "stop":
            j["amp"] = dict(kind="baseline_then_phase_stop", t_stop=6.0, ramp_cycles=1.0)
        elif kind == "restart":
            j["amp"] = dict(kind="restart", cycles=[[0.0, 4.5], [8.0, 12.0]], ramp_s=1.0, ramp_cycles=1.0)
        elif kind == "speed":
            j["stride_scale"] = block["scale"]
    return js

def passed(block, row):
    up = row["fell"] is None
    yd = yaw_deg(row)
    kind = block["kind"]
    if kind == "slew":
        hd = row.get("heading") or {}
        err = hd.get("heading_err_final_deg")
        cross = hd.get("crosstrack_rms_after_slew_m")
        delta = block["delta_deg"]
        return bool(up and err is not None and abs(err) <= 15.0 and (yd * delta) > 0.0
                    and abs(yd) >= 0.5 * abs(delta)
                    and cross is not None and cross <= 0.40)
    if kind == "stop":
        st = row.get("stop") or {}
        return bool(up and st.get("speed_before_stop") is not None and st["speed_before_stop"] > 0.05
                    and st.get("speed_after_settle") is not None and st["speed_after_settle"] < 0.03
                    and st.get("disp_after_stop_m") is not None and st["disp_after_stop_m"] < 0.15
                    and abs(yd) <= 15.0)
    if kind == "restart":
        tr = row.get("trace") or []
        mid, walk = gap_speed(tr, 6.2, 7.6), gap_speed(tr, 9.5, 11.5)
        return bool(up and mid is not None and mid < 0.03 and walk is not None and walk > 0.08 and abs(yd) <= 15.0)
    if kind == "speed":
        target = 0.11 * block["scale"]
        prog = row["dx"] / row["T"]
        return bool(up and abs(yd) <= 20.0 and abs(prog - target) <= 0.25 * abs(target))
    if kind == "slalom":
        tr = row.get("trace") or []
        ys = series(tr)
        if not up or not ys:
            return False
        targets = {7: 20, 12: 0, 17: -20, 22: 0}
        for t, target in targets.items():
            ang = min(ys, key=lambda p: abs(p[0] - t))[1]
            if abs(ang - target) > 15.0:
                return False
        return True
    if kind == "straight":
        return bool(up and abs(yd) <= 15.0 and row["dx"] / row["T"] >= 0.08)
    return False

def slim(block, row):
    hd = row.get("heading") or {}
    st = row.get("stop") or {}
    j = row.get("joints") or {}
    anks = [j[n]["sat"] for n in ("left_ankle", "right_ankle") if n in j]
    return dict(
        seed=int(row["seed"]), fell=None if row["fell"] is None else round(float(row["fell"]), 3),
        yaw_deg=round(yaw_deg(row), 2), prog=round(row["dx"] / row["T"], 4),
        path_m=round(float(row.get("path_m") or 0.0), 3),
        err=None if hd.get("heading_err_final_deg") is None else round(hd["heading_err_final_deg"], 2),
        cross=None if hd.get("crosstrack_rms_after_slew_m") is None else round(hd["crosstrack_rms_after_slew_m"], 3),
        before=None if st.get("speed_before_stop") is None else round(st["speed_before_stop"], 4),
        after=None if st.get("speed_after_settle") is None else round(st["speed_after_settle"], 4),
        disp=None if st.get("disp_after_stop_m") is None else round(st["disp_after_stop_m"], 3),
        ankle_sat=None if not anks else round(float(np.mean(anks)), 4),
        task=bool(passed(block, row)),
        min_pitch=None if not row.get("pitch_tail") else round(row["pitch_tail"].get("min_deg", 0.0), 2),
    )

def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ph, c - h, c + h]

def run_block(block, seeds, xml):
    rows = V.Y.run_jobs(jobs_for(block, seeds, xml))
    slim_rows = [slim(block, r) for r in rows]
    k = sum(1 for r in slim_rows if r["task"])
    return dict(name=block["name"], n=len(slim_rows), task=k, wilson=wilson(k, len(slim_rows)),
                upright=sum(1 for r in slim_rows if r["fell"] is None), rows=slim_rows)

def main():
    pre = json.load(open(PREREG))
    man = hashlib.sha256(open(os.path.join(HERE, "manoeuvre.py"), "rb").read()).hexdigest()
    npy = hashlib.sha256(open(os.path.join(ROOT, "params", "head843_earlyrate.npy"), "rb").read()).hexdigest()
    if man != pre["candidate"]["manoeuvre_sha256"] or npy != pre["candidate"]["base_npy_sha256"]:
        raise SystemExit("hash changed after prereg")
    results = []
    by = {}
    for block in pre["blocks"]:
        seeds = list(range(block["seeds"][0], block["seeds"][1] + 1))
        rec = run_block(block, seeds, H.NOM)
        results.append(rec)
        by[block["name"]] = (block, rec)
        print(block["name"], f"{rec['task']}/{rec['n']}", "wilson", [round(x, 4) for x in rec["wilson"]], flush=True)
    bounds = []
    for name, slots in pre["bounds_if_nominal_task_perfect"].items():
        if name == "rule":
            continue
        block, rec = by[name]
        if rec["task"] != rec["n"]:
            print("bounds skipped", name, flush=True)
            continue
        for tag, xml in (("lo", H.LO), ("hi", H.HI)):
            b = dict(block)
            b["name"] = name + "_" + tag
            seeds = list(range(slots[tag][0], slots[tag][1] + 1))
            out = run_block(b, seeds, xml)
            bounds.append(out)
            print(b["name"], f"{out['task']}/{out['n']}", flush=True)
    json.dump(dict(prereg=PREREG, results=results, bounds=bounds), open(OUT, "w"), indent=1)
    print("wrote", OUT, flush=True)

if __name__ == "__main__":
    main()
