"""Validation only of the frozen short-step trim. No retune and no new law.

The controller, evaluator, models, and randomization are the files hashed in
the preregistration. keep_trace only retains the state log that measure_path
already builds. It does not change the policy. Baseline pairing is not run.
Nothing stops because an interval has already cleared or missed.
"""
import os, sys, json, time, hashlib, math
from datetime import datetime, timezone
import numpy as np
from scipy.stats import beta
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_MODE = "write" if "--write-prereg" in sys.argv else ("check" if "--metric-check" in sys.argv else "run")
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_traj as T
import run_head843_search as S
import run_head843_heading as H
import run_head843_yawstate as Y
import run_head843_shortbal as B

PREREG = os.path.join(ROOT, "results", "head843_shortbal_val_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_shortbal_val.json")

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def hashes():
    return {
        "candidate_npy": sha(os.path.join(ROOT, "params", "head843_shortbal.npy")),
        "baseline_traj_npy": sha(os.path.join(ROOT, "params", "head843_traj.npy")),
        "baseline_search_npy": sha(os.path.join(ROOT, "params", "head843_search.npy")),
        "reliable_npy": sha(os.path.join(ROOT, "params", "reliable.npy")),
        "fast_npy": sha(os.path.join(ROOT, "params", "fast.npy")),
        "efficient_npy": sha(os.path.join(ROOT, "params", "efficient.npy")),
        "xml_nom": sha(H.NOM),
        "xml_lo": sha(H.LO),
        "xml_hi": sha(H.HI),
        "xml_canonical": sha(os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")),
        "scene": sha(os.path.join(ROOT, "geometry", "scene_v335ac.npz")),
        "manoeuvre": sha(os.path.join(HERE, "manoeuvre.py")),
        "simlib": sha(os.path.join(HERE, "simlib.py")),
        "episode": sha(os.path.join(HERE, "episode.py")),
        "shortbal_eval": sha(os.path.join(HERE, "run_head843_shortbal.py")),
        "traj_eval": sha(os.path.join(HERE, "run_head843_traj.py")),
        "val_runner": sha(os.path.join(HERE, "run_head843_shortbal_val.py")),
    }

def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi

def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ph, c - h, c + h]

def clopper(k, n):
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [k / n, lo, hi]

def yaw_series(tr):
    y0 = tr[0]["yaw"]
    return [math.degrees(wrap(p["yaw"] - y0)) for p in tr]

def from_trace(tr, fell, yaw_change):
    if not tr:
        return dict(yaw_peak_max=None, yaw_peak_min=None, yaw_peak_abs=None, backward_pitch=None)
    ys = yaw_series(tr)
    # The first logged sample is one 2 ms step after reset. Shift the series so
    # its last sample matches the official terminal yaw, which uses yaw at reset.
    shift = math.degrees(yaw_change) - ys[-1]
    ys = [v + shift for v in ys]
    out = dict(
        yaw_peak_max=float(max(ys)),
        yaw_peak_min=float(min(ys)),
        yaw_peak_abs=float(max(abs(v) for v in ys)),
        yaw_ref_shift_deg=float(shift),
        backward_pitch=None,
    )
    if fell is None:
        return out
    i = min(range(len(tr)), key=lambda k: abs(tr[k]["t"] - (fell - 0.4)))
    pr = None
    if 0 < i < len(tr) - 1:
        dt = tr[i + 1]["t"] - tr[i - 1]["t"]
        if dt > 0:
            pr = math.degrees((tr[i + 1]["pitch"] - tr[i - 1]["pitch"]) / dt)
    pre_pitch = math.degrees(tr[i]["pitch"])
    out.update(
        pre_t=float(tr[i]["t"]),
        pre_pitch=float(pre_pitch),
        pre_roll=float(math.degrees(tr[i]["roll"])),
        pre_yaw=float(ys[i]),
        pre_pr=None if pr is None else float(pr),
        backward_pitch=bool(pre_pitch < -8.0 and pr is not None and pr < 0.0),
    )
    return out

def slim(r):
    j = r.get("joints") or {}
    def sat(names):
        vals = [j[n]["sat"] for n in names if n in j]
        return None if not vals else float(np.mean(vals))
    mn, pp = r.get("motion_mean_deg") or {}, r.get("motion_pp_deg") or {}
    at, pt = r.get("ankle_track") or {}, r.get("pitch_tail") or {}
    sh_m = sh_p = None
    if "shoulder_L" in mn and "shoulder_R" in mn:
        sh_m = 0.5 * (mn["shoulder_L"] + mn["shoulder_R"])
    if "shoulder_L" in pp and "shoulder_R" in pp:
        sh_p = 0.5 * (pp["shoulder_L"] + pp["shoulder_R"])
    row = dict(
        seed=int(r["seed"]), fell=None if r["fell"] is None else float(r["fell"]),
        dx=float(r["dx"]), T=float(r["T"]), yaw=float(r["yaw_change"]),
        sh_m=sh_m, sh_p=sh_p, hy=pp.get("head_yaw"),
        frac_neg=at.get("frac_neg"), frac_abs=at.get("frac_abs"), gt10=pt.get("frac_gt10"),
        ankle_sat=sat(("left_ankle", "right_ankle")),
        hip_sat=sat(("left_hip_pitch", "right_hip_pitch")),
        main_sat=(r.get("load") or {}).get("main_sat"),
    )
    row.update(from_trace(r.get("trace") or [], row["fell"], row["yaw"]))
    return row

def yaw_dist(vals):
    a = np.asarray(vals, float)
    return dict(n=int(a.size), median=float(np.median(a)), p10=float(np.percentile(a, 10)),
                p90=float(np.percentile(a, 90)), min=float(a.min()), max=float(a.max()),
                frac15=float(np.mean(np.abs(a) > 15)))

def block_stats(rows):
    surv = [r for r in rows if r["fell"] is None]
    end_all = np.degrees([r["yaw"] for r in rows])
    end_surv = np.degrees([r["yaw"] for r in surv]) if surv else np.array([])
    peak = np.array([r["yaw_peak_abs"] for r in rows if r.get("yaw_peak_abs") is not None], float)
    peak_max = [r["yaw_peak_max"] for r in rows if r.get("yaw_peak_max") is not None]
    peak_min = [r["yaw_peak_min"] for r in rows if r.get("yaw_peak_min") is not None]
    falls = []
    n_back = 0
    for r in rows:
        if r["fell"] is None:
            continue
        if r.get("backward_pitch"):
            n_back += 1
        falls.append(dict(
            seed=r["seed"], t=r["fell"], dx=round(r["dx"], 3),
            yaw_end_deg=round(float(np.degrees(r["yaw"])), 2),
            yaw_peak_abs=None if r.get("yaw_peak_abs") is None else round(r["yaw_peak_abs"], 2),
            pre_pitch=None if r.get("pre_pitch") is None else round(r["pre_pitch"], 2),
            pre_roll=None if r.get("pre_roll") is None else round(r["pre_roll"], 2),
            pre_yaw=None if r.get("pre_yaw") is None else round(r["pre_yaw"], 2),
            pre_pr=None if r.get("pre_pr") is None else round(r["pre_pr"], 2),
            backward_pitch=r.get("backward_pitch"),
        ))
    def mean(key, src):
        vals = [r[key] for r in src if r.get(key) is not None]
        return None if not vals else float(np.mean(vals))
    def med(key, src):
        vals = [r[key] for r in src if r.get(key) is not None]
        return None if not vals else float(np.median(vals))
    return dict(
        succ=len(surv), n=len(rows), rate=len(surv) / len(rows),
        wilson=wilson(len(surv), len(rows)), clopper=clopper(len(surv), len(rows)),
        progress=float(np.mean([r["dx"] / r["T"] for r in rows])),
        speed=None if not surv else float(np.mean([r["dx"] / r["T"] for r in surv])),
        shoulder_mean=med("sh_m", surv), shoulder_pp=med("sh_p", surv), head_yaw_pp=med("hy", surv),
        frac_neg=mean("frac_neg", rows), frac_abs=mean("frac_abs", rows), gt10=mean("gt10", rows),
        ankle_sat=mean("ankle_sat", rows), hip_sat=mean("hip_sat", rows), main_sat=mean("main_sat", rows),
        heading=dict(
            all_trials_end=yaw_dist(end_all),
            survivors_end=None if end_surv.size == 0 else yaw_dist(end_surv),
            trajectory_peak_abs=None if peak.size == 0 else dict(
                n=int(peak.size), median=float(np.median(peak)), p90=float(np.percentile(peak, 90)),
                max=float(peak.max()), frac15=float(np.mean(peak > 15)),
                signed_max=float(np.max(peak_max)), signed_min=float(np.min(peak_min))),
            note="all_trials_end uses yaw at the horizon or at the fall. survivors_end drops falls. trajectory_peak_abs is the largest |heading change| at any logged sample, including trials that finish inside ±15°.",
        ),
        falls=falls, n_backward_pitch=n_back, n_other_fall=len(falls) - n_back,
        fell=[r["seed"] for r in rows if r["fell"] is not None],
    )

def load_models():
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    prev = json.load(open(os.path.join(ROOT, "results", "head843_shortbal_qual_prereg.json")))
    ztraj = np.array([prev["candidate"]["traj_z"][k] for k in T.KEYS], float)
    zsb = np.load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    return gait, base, ztraj, zsb

def one_job(seed, xml, Ts, gait, base, ztraj, zsb):
    js = B.jobs("cand", zsb, base, gait, ztraj, [seed], xml, Ts)
    js[0]["keep_trace"] = True
    return js[0]

def metric_check():
    gait, base, ztraj, zsb = load_models()
    raw = json.load(open(os.path.join(ROOT, "results", "head843_shortbal_qual.json")))
    prev = next(r for r in raw["blocks"]["nom20_cand"] if r["seed"] == 154186)
    row = slim(Y.run_jobs([one_job(154186, H.NOM, 20.0, gait, base, ztraj, zsb)])[0])
    dy = abs(math.degrees(row["yaw"]) - math.degrees(prev["yaw"]))
    dt = abs((row["fell"] or -1) - (prev["fell"] or -2))
    print("metric-check seed 154186", "fell", row["fell"], "prev", prev["fell"], "dyaw_deg", round(dy, 4),
          "peak", None if row.get("yaw_peak_abs") is None else round(row["yaw_peak_abs"], 2),
          "end", round(math.degrees(row["yaw"]), 2),
          "shift", None if row.get("yaw_ref_shift_deg") is None else round(row["yaw_ref_shift_deg"], 3),
          "class", row.get("backward_pitch"), "pre_pitch", row.get("pre_pitch"), flush=True)
    if dt > 1e-6 or dy > 0.05 or row.get("yaw_peak_abs") is None:
        raise SystemExit("metric check failed; prereg not written")
    print("metric-check ok", flush=True)

def write_prereg():
    if os.path.exists(PREREG):
        raise SystemExit("prereg already exists")
    z = np.load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    prev = json.load(open(os.path.join(ROOT, "results", "head843_shortbal_qual_prereg.json")))
    doc = {
        "preregistered_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": "Validation only. Counts and seeds fixed before any trial in this file. No retune, no larger clip, no new law, no response to interim falls. No early stop on a favorable or unfavorable interval. No pooling across horizons, masses, or with the 150000 qualification, the 400-seed screen, or the 400-seed 20 s block. No baseline pairing. A simulated distribution, not a hardware certification.",
        "candidate": {
            "file": "params/head843_shortbal.npy",
            "sha256": hashes()["candidate_npy"],
            "z_short_balance": {k: float(v) for k, v in zip(B.KEYS, z)},
            "pitch_sign": 1.0,
            "cap_rad": 0.06,
            "yaw_command_clip_rad": 0.03,
            "hip_yaw_clip_rad": 0.07,
            "traj_file": "params/head843_traj.npy",
            "traj_sha256": "1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc",
            "traj_z": prev["candidate"]["traj_z"],
        },
        "hashes": hashes(),
        "physics": "Fall at 45 deg roll or pitch, or trunk COM height below 0.6 of the start height. Randomization: body mass ±10%, geom friction 0.6-1.0, armature and damping ±30% on dof 6 and after, latency 0-5 steps of 2 ms, backlash 0.4 deg. Servo stall clip ±1.91 N·m, kp 12 N·m/rad, kd 0.25. Unchanged.",
        "heads": {"nominal_kg": 0.84258, "low_kg": 0.82258, "high_kg": 0.88458},
        "logging": "keep_trace retains the sample log that measure_path already builds. Terminal yaw is wrap(final yaw − yaw at reset), the same field as the 150000 qualification. Peak yaw uses that same reset reference: the logged series is shifted by one constant so its last sample equals the terminal yaw. On the metric-check seed that constant was about 0.45 deg, the yaw in the first 2 ms step.",
        "backward_pitch_rule": "A fall is backward-pitch when the logged sample nearest 0.4 s before the fall has pitch below −8 deg and the pitch rate from the neighbouring samples is negative. Any other fall is other. The rule was fixed before these trials.",
        "criteria": {
            "interval": "two-sided 95% Wilson, z=1.96, applied separately to each block",
            "support": "lower bound >= 0.995 on that block's candidate trials",
            "scope": "Each line is one horizon and one head mass. None is a hardware certification. Clopper-Pearson is reported and is not a second gate.",
        },
        "blocks": [
            {"name": "nom20", "seeds_inclusive": [180000, 183999], "n": 4000, "T_s": 20.0, "xml": "head843", "priority": 1},
            {"name": "nom10rep", "seeds_inclusive": [184000, 187999], "n": 4000, "T_s": 10.0, "xml": "head843", "priority": 2},
            {"name": "lo10", "seeds_inclusive": [188000, 188999], "n": 1000, "T_s": 10.0, "xml": "head823", "priority": 3},
            {"name": "hi10", "seeds_inclusive": [189000, 189999], "n": 1000, "T_s": 10.0, "xml": "head885", "priority": 4},
        ],
        "order": "nom20 fully, then nom10rep, then lo10, then hi10. Candidate only.",
        "provenance": {
            "traj_npy_mtime_utc": "2026-11-08T01:47:34Z",
            "traj_qual_prereg_utc": "2026-11-08T01:52:02Z",
            "traj_qual_seeds": "130000-133999 nominal 10 s, 134000-134399 nominal 20 s, 135000-135199 low, 136000-136199 heavy. Result 3978/4000 preserved. Hash 1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc.",
            "miss_timeline_utc": "2026-11-08T02:08:29Z",
            "manoeuvre_mtime_utc": "2026-11-08T02:10:25Z",
            "train_script_mtime_utc": "2026-11-08T02:11:26Z",
            "train_seeds": "140200-140215 nominal 10 s, 140400-140407 nominal 20 s, 140500-140507 heavy, 140600-140607 low, four generations.",
            "sign_probe_seeds": "140100-140115 fresh 20 s yaw-sign check, and the 22 misses of 130000-133999 as a mechanism check. Not a selection set.",
            "selection_seeds": "141000-141199 nominal 10 s, 141300-141339 nominal 20 s, 141400-141423 heavy and the same seeds on the low head.",
            "selection_ckpt_utc": "2026-11-08T02:11:57Z",
            "npy_frozen_utc": "2026-11-08T02:12:48Z",
            "screen_utc": "2026-11-08T02:14:08Z",
            "screen_seeds": "142000-142399 nominal 10 s, 142500-142539 nominal 20 s, 142600-142619 heavy and low. After the npy save. Not this qualification and not this validation.",
            "qual_prereg_utc": "2026-11-08T02:17:09Z",
            "qual_finished_utc": "2026-11-08T02:30:21Z",
            "qual_seeds": "150000-153999, 154000-154399, 155000-155199, 156000-156199.",
            "qual_raw_counts": "nom20_cand in head843_shortbal_qual.json has 400 rows and 399 survivors. The one fall is seed 154186 at 4.664 s with terminal yaw 14.6 deg. lo10_cand has 200 rows and 199 survivors. The one fall is seed 155188 at 3.476 s with terminal yaw 20.7 deg. The 0 percent of that 20 s block past ±15 deg is the terminal yaw of all 400 rows. Peak yaw along the trajectory was not stored there.",
            "fall_reread_utc": "2026-11-08T02:31:37Z",
            "metric_check": "Seed 154186, already in the qualification, was replayed once to confirm keep_trace does not move the fall time or the terminal yaw. It is not in the blocks above.",
        },
    }
    json.dump(doc, open(PREREG, "w"), indent=1)
    print("wrote", PREREG, doc["preregistered_at_utc"], flush=True)

def load_state(pre):
    if os.path.exists(OUT):
        return json.load(open(OUT))
    return {"prereg": PREREG, "blocks": {}, "pending": [b["name"] for b in pre["blocks"]]}

def save_state(st):
    json.dump(st, open(OUT, "w"))

def run_block(block, gait, base, ztraj, zsb, st):
    xmls = {"head843": H.NOM, "head823": H.LO, "head885": H.HI}
    name = block["name"]
    seeds = list(range(block["seeds_inclusive"][0], block["seeds_inclusive"][1] + 1))
    if len(seeds) != block["n"]:
        raise SystemExit("seed count mismatch " + name)
    have = {r["seed"] for r in st["blocks"].get(name, [])}
    todo = [s for s in seeds if s not in have]
    print(name, "resume", len(have), "todo", len(todo), flush=True)
    chunk = 200 if block["T_s"] >= 20 else 400
    xml = xmls[block["xml"]]
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        jobs = B.jobs("cand", zsb, base, gait, ztraj, part, xml, block["T_s"])
        for j in jobs:
            j["keep_trace"] = True
        rows = Y.run_jobs(jobs)
        st["blocks"].setdefault(name, []).extend(slim(r) for r in rows)
        st["blocks"][name].sort(key=lambda r: r["seed"])
        save_state(st)
        fell = sum(1 for r in st["blocks"][name] if r["fell"] is not None)
        print(name, "done", len(st["blocks"][name]), "falls", fell, flush=True)
    if name in st["pending"] and len(st["blocks"][name]) == block["n"]:
        st["pending"].remove(name)
        save_state(st)

def main():
    if _MODE == "check":
        metric_check()
        return
    if _MODE == "write":
        write_prereg()
        return
    pre = json.load(open(PREREG))
    now = hashes()
    for k, v in pre["hashes"].items():
        if now[k] != v:
            raise SystemExit(f"hash changed {k}")
    zsb = np.load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    if [round(float(v), 8) for v in zsb] != [round(pre["candidate"]["z_short_balance"][k], 8) for k in B.KEYS]:
        raise SystemExit("vector mismatch")
    if sha(os.path.join(ROOT, "params", "head843_traj.npy")) != "1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc":
        raise SystemExit("traj hash changed")
    gait, base, ztraj, _ = load_models()
    st = load_state(pre)
    t0 = time.time()
    for block in pre["blocks"]:
        run_block(block, gait, base, ztraj, zsb, st)
    summary = {}
    for block in pre["blocks"]:
        name = block["name"]
        if len(st["blocks"].get(name, [])) != block["n"]:
            print("incomplete", name, len(st["blocks"].get(name, [])), flush=True)
            continue
        summary[name] = block_stats(st["blocks"][name])
        a = summary[name]
        h = a["heading"]
        print(name, f"{a['succ']}/{a['n']}", "wilson", [round(x, 6) for x in a["wilson"]],
              "prog", round(a["progress"], 4),
              "end15", round(h["all_trials_end"]["frac15"], 4),
              "surv15", None if h["survivors_end"] is None else round(h["survivors_end"]["frac15"], 4),
              "peak15", None if h["trajectory_peak_abs"] is None else round(h["trajectory_peak_abs"]["frac15"], 4),
              "back", a["n_backward_pitch"], "other", a["n_other_fall"],
              "met", a["wilson"][1] >= 0.995, flush=True)
    st["summary"] = summary
    st["seconds"] = round(time.time() - t0, 1)
    st["criteria"] = {k: bool(v["wilson"][1] >= 0.995) for k, v in summary.items()}
    save_state(st)
    print("DONE pending", st["pending"], st["criteria"], flush=True)

if __name__ == "__main__":
    main()
