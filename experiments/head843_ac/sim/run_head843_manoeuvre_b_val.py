"""Preregistered wrap-safe manoeuvre qualification. No retune."""
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

PREREG = os.path.join(ROOT, "results", "head843_manoeuvre_b_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_manoeuvre_b_val.json")

def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(max(0.0, ph * (1 - ph) / n + z * z / (4 * n * n))) / den
    return [ph, c - h, c + h]

def unwrapped(tr):
    if not tr:
        return []
    y0 = tr[0]["yaw"]
    rel = np.unwrap([p["yaw"] - y0 for p in tr])
    return list(zip([p["t"] for p in tr], rel))

def gap_speed(tr, t0, t1):
    xs = [(p["t"], p["x"], p["y"]) for p in tr if t0 <= p["t"] <= t1]
    if len(xs) < 2:
        return None
    dist = sum(math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(xs, xs[1:]))
    return dist / (xs[-1][0] - xs[0][0])

def jobs_for(block, seeds, xml):
    z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    js = E.jobs("early", z, seeds, xml, block["T"])
    kind = block["kind"]
    for j in js:
        if kind in ("slew", "slalom", "restart"):
            j["keep_trace"] = True
        if kind == "slew":
            j["heading"] = dict(kind="feedback", t0=block["t0"], t1=block["t1"],
                                delta=math.radians(block["delta_deg"]), kp=0.6, kd=0.02, ki=0.0, limit=0.07,
                                k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True)
        elif kind == "slalom":
            j["heading"] = dict(kind="route", k_yaw_ff=0.20, k_yaw_p=0.45, track_settle=True, segments=[
                {"t0": 2, "t1": 7, "yaw_deg": 20}, {"t0": 7, "t1": 12, "yaw_deg": 0},
                {"t0": 12, "t1": 17, "yaw_deg": -20}, {"t0": 17, "t1": 22, "yaw_deg": 0}])
        elif kind == "stop":
            j["amp"] = dict(kind="baseline_then_phase_stop", t_stop=6.0, ramp_cycles=1.0)
        elif kind == "restart":
            j["amp"] = dict(kind="restart", cycles=[[0.0, 4.5], [8.0, 12.0]], ramp_s=1.0, ramp_cycles=1.0)
        elif kind == "speed":
            j["stride_scale"] = block["scale"]
    return js

def turn_ok(block, row):
    tr = row.get("trace") or []
    ys = unwrapped(tr)
    if row["fell"] is not None or len(ys) < 5:
        return False, {}
    delta = math.radians(block["delta_deg"])
    rel = np.array([y for _, y in ys])
    ts = np.array([t for t, _ in ys])
    final = float(rel[-1])
    err = final - delta
    sign = 1.0 if delta > 0 else -1.0
    wrong = float((-sign * rel).max())
    t1 = block["t1"]
    after = np.where(ts >= t1)[0]
    entered = None
    if len(after):
        hit = after[np.abs(rel[after] - delta) <= math.radians(15)]
        if len(hit):
            entered = float(ts[hit[0]] - t1)
    cross = (row.get("heading") or {}).get("crosstrack_rms_after_slew_m")
    ok = (abs(math.degrees(err)) <= 15.0 and final * delta > 0.0 and math.degrees(wrong) <= 15.0
          and entered is not None and entered <= block["T"] - t1 + 1e-6
          and cross is not None and cross <= 0.40)
    return bool(ok), dict(final_deg=round(math.degrees(final), 2), err_deg=round(math.degrees(err), 2),
                          wrong_deg=round(math.degrees(wrong), 2), settle_s=None if entered is None else round(entered, 2),
                          cross=None if cross is None else round(cross, 3))

def slalom_ok(row):
    tr = row.get("trace") or []
    ys = unwrapped(tr)
    if row["fell"] is not None or not ys:
        return False, {}
    ts = np.array([t for t, _ in ys]); rel = np.array([y for _, y in ys])
    targets = [(7, 20), (12, 0), (17, -20), (22, 0)]
    pts = {}
    ok = True
    for t, target in targets:
        i = int(np.argmin(np.abs(ts - t)))
        ang = math.degrees(rel[i])
        pts[str(t)] = round(ang, 2)
        if abs(ang - target) > 15.0:
            ok = False
    # positive lobe before negative lobe
    i7 = int(np.argmin(np.abs(ts - 7))); i17 = int(np.argmin(np.abs(ts - 17)))
    if not (rel[i7] > 0 and rel[i17] < 0):
        ok = False
    return bool(ok), pts

def passed(block, row):
    kind = block["kind"]
    yd = math.degrees(row["yaw_change"])
    up = row["fell"] is None
    if kind == "slew":
        ok, info = turn_ok(block, row)
        return ok, info
    if kind == "slalom":
        return slalom_ok(row)
    if kind == "stop":
        st = row.get("stop") or {}
        ok = bool(up and (st.get("speed_before_stop") or 0) > 0.05 and (st.get("speed_after_settle") or 1) < 0.03
                  and (st.get("disp_after_stop_m") or 1) < 0.15 and abs(yd) <= 15.0)
        return ok, dict(yaw_deg=round(yd, 2), after=st.get("speed_after_settle"), disp=st.get("disp_after_stop_m"))
    if kind == "restart":
        tr = row.get("trace") or []
        mid, walk = gap_speed(tr, 6.2, 7.6), gap_speed(tr, 9.5, 11.5)
        ok = bool(up and mid is not None and mid < 0.03 and walk is not None and walk > 0.08 and abs(yd) <= 15.0)
        return ok, dict(mid=None if mid is None else round(mid, 4), walk=None if walk is None else round(walk, 4), yaw_deg=round(yd, 2))
    if kind == "speed":
        target = 0.11 * block["scale"]
        prog = row["dx"] / row["T"]
        ok = bool(up and abs(yd) <= 20.0 and abs(prog - target) <= 0.25 * abs(target))
        return ok, dict(prog=round(prog, 4), yaw_deg=round(yd, 2))
    if kind == "straight":
        prog = row["dx"] / row["T"]
        ok = bool(up and abs(yd) <= 15.0 and prog >= 0.08)
        return ok, dict(prog=round(prog, 4), yaw_deg=round(yd, 2))
    return False, {}

def slim(block, row):
    ok, info = passed(block, row)
    j = row.get("joints") or {}
    anks = [j[n]["sat"] for n in ("left_ankle", "right_ankle") if n in j]
    out = dict(seed=int(row["seed"]), fell=None if row["fell"] is None else round(float(row["fell"]), 3),
               task=bool(ok), ankle_sat=None if not anks else round(float(np.mean(anks)), 4),
               min_pitch=None if not row.get("pitch_tail") else round(row["pitch_tail"].get("min_deg", 0.0), 2))
    out.update(info)
    return out

def main():
    pre = json.load(open(PREREG))
    man = hashlib.sha256(open(os.path.join(HERE, "manoeuvre.py"), "rb").read()).hexdigest()
    if man != pre["candidate"]["manoeuvre_sha256"]:
        raise SystemExit("manoeuvre changed " + man)
    st = json.load(open(OUT)) if os.path.exists(OUT) else {"blocks": {}, "pending": [b["name"] for b in pre["blocks"]]}
    xmls_done = False
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
    summary = {}
    for block in pre["blocks"]:
        rows = st["blocks"][block["name"]]
        k = sum(1 for r in rows if r["task"])
        w = wilson(k, len(rows))
        summary[block["name"]] = dict(task=k, n=len(rows), wilson=w, met=bool(len(rows) == block["n"] and w[1] >= 0.995),
                                      falls=[r["seed"] for r in rows if r["fell"] is not None])
        print("SUM", block["name"], f"{k}/{len(rows)}", [round(x, 5) for x in w], "met", summary[block["name"]]["met"], flush=True)
    bounds = {}
    for name, slots in pre["bounds_if_nominal_1000_perfect"].items():
        if name == "rule" or not summary.get(name, {}).get("met"):
            continue
        block = next(b for b in pre["blocks"] if b["name"] == name)
        bounds[name] = {}
        for tag, xml in (("lo", H.LO), ("hi", H.HI)):
            seeds = list(range(slots[tag][0], slots[tag][1] + 1))
            rows = [slim(block, r) for r in V.Y.run_jobs(jobs_for(block, seeds, xml))]
            k = sum(1 for r in rows if r["task"])
            bounds[name][tag] = dict(task=k, n=len(rows), wilson=wilson(k, len(rows)), rows=rows)
            print("BOUND", name, tag, f"{k}/{len(rows)}", flush=True)
    st["summary"] = summary
    st["bounds"] = bounds
    json.dump(st, open(OUT, "w"))
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
