"""One fixed 4000-seed validation of the frozen trim on the 0.82258 kg head.

No retune. The 1000-seed low block stays inconclusive and is not pooled.
If this block misses the predeclared Wilson bar, there is no further extension.
"""
import os, sys, json, time, hashlib
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_MODE = "write" if "--write-prereg" in sys.argv else "run"
sys.path.insert(0, HERE)
os.environ.setdefault("TWIGLET_XML", os.path.join(HERE, "models", "twiglet_v3_v335ac.xml"))
os.environ.setdefault("TWIGLET_PARAMS", os.path.join(ROOT, "params", "reliable.npy"))
import run_head843_shortbal_val as V

PREREG = os.path.join(ROOT, "results", "head843_shortbal_low4000_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_shortbal_low4000.json")
FROZEN = "52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5"
TRAJ = "1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc"

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def hashes():
    h = V.hashes()
    h["low4000_runner"] = sha(os.path.join(HERE, "run_head843_shortbal_low4000.py"))
    h["val_runner_unchanged"] = h["val_runner"]
    return h

def write_prereg():
    if os.path.exists(PREREG):
        raise SystemExit("prereg already exists")
    h = hashes()
    if h["candidate_npy"] != FROZEN or h["baseline_traj_npy"] != TRAJ:
        raise SystemExit("frozen file hash mismatch; prereg not written")
    z = __import__("numpy").load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    doc = {
        "preregistered_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": "One new declared experiment. Seeds and the criterion are fixed before any trial. No retune, no larger clip, no optional stop, no pooling with the 1000-seed low block or with any nominal or heavy block. If the Wilson lower bound is below 0.995, the low-head question closes without another sample-size extension. A pass does not convert the earlier 1000 into a pooled qualification. Simulated distribution only, not hardware certification.",
        "why_a_second_test": "Seeds 188000-188999 were 996/1000, point estimate 0.996, Wilson lower 0.98976. The interval includes values below 0.995, so that block is inconclusive. It is not reused. Repeating a test is not itself a guarantee. This 4000 is a separate predeclared sample.",
        "candidate": {
            "file": "params/head843_shortbal.npy",
            "sha256": FROZEN,
            "z_short_balance": {k: float(v) for k, v in zip(V.B.KEYS, z)},
            "pitch_sign": 1.0,
            "cap_rad": 0.06,
            "traj_file": "params/head843_traj.npy",
            "traj_sha256": TRAJ,
        },
        "hashes": h,
        "physics": "Unchanged. Fall at 45 deg roll or pitch, or trunk COM height below 0.6 of the start. Mass randomization ±10%, friction 0.6-1.0, armature and damping ±30%, latency 0-5 steps of 2 ms, backlash 0.4 deg. Stall clip ±1.91 N·m.",
        "head": {"file": "sim/models/twiglet_v3_v335ac_head823.xml", "mass_kg": 0.82258, "sha256": h["xml_lo"]},
        "criterion": {
            "interval": "two-sided 95% Wilson, z=1.96",
            "support": "lower bound >= 0.995 on these 4000 trials only",
            "also_reported_not_a_gate": "Clopper-Pearson exact two-sided 95%",
            "scope": "10 s, 0.82258 kg head, seeds 190000-193999. Not the nominal 10 s blocks, not the 20 s block, not the heavy head, not hardware.",
        },
        "backward_pitch_rule": "Same rule as the 180000 validation: pitch below -8 deg and negative pitch rate at the sample nearest 0.4 s before the fall.",
        "block": {"name": "lo10_4000", "seeds_inclusive": [190000, 193999], "n": 4000, "T_s": 10.0, "xml": "head823"},
        "not_pooled": ["188000-188999", "150000-153999", "180000-183999", "184000-187999", "189000-189999"],
    }
    json.dump(doc, open(PREREG, "w"), indent=1)
    print("wrote", PREREG, doc["preregistered_at_utc"], flush=True)

def main():
    if _MODE == "write":
        write_prereg()
        return
    pre = json.load(open(PREREG))
    now = hashes()
    for k, v in pre["hashes"].items():
        if now[k] != v:
            raise SystemExit("hash changed " + k)
    if now["candidate_npy"] != FROZEN:
        raise SystemExit("trim hash changed")
    gait, base, ztraj, zsb = V.load_models()
    block = pre["block"]
    seeds = list(range(block["seeds_inclusive"][0], block["seeds_inclusive"][1] + 1))
    if len(seeds) != 4000:
        raise SystemExit("seed count")
    st = json.load(open(OUT)) if os.path.exists(OUT) else {"prereg": PREREG, "rows": [], "pending": True}
    have = {r["seed"] for r in st["rows"]}
    todo = [s for s in seeds if s not in have]
    print("lo10_4000 resume", len(have), "todo", len(todo), flush=True)
    t0 = time.time()
    for i in range(0, len(todo), 400):
        part = todo[i:i + 400]
        jobs = V.B.jobs("cand", zsb, base, gait, ztraj, part, V.H.LO, 10.0)
        for j in jobs:
            j["keep_trace"] = True
        st["rows"].extend(V.slim(r) for r in V.Y.run_jobs(jobs))
        st["rows"].sort(key=lambda r: r["seed"])
        json.dump(st, open(OUT, "w"))
        fell = sum(1 for r in st["rows"] if r["fell"] is not None)
        print("lo10_4000 done", len(st["rows"]), "falls", fell, flush=True)
    if len(st["rows"]) != 4000:
        print("incomplete", len(st["rows"]), flush=True)
        return
    summary = V.block_stats(st["rows"])
    summary["criterion_met"] = bool(summary["wilson"][1] >= 0.995)
    summary["seconds"] = round(time.time() - t0, 1)
    st["summary"] = summary
    st["pending"] = False
    json.dump(st, open(OUT, "w"))
    hdg = summary["heading"]
    print("RESULT", f"{summary['succ']}/{summary['n']}",
          "wilson", [round(x, 6) for x in summary["wilson"]],
          "clopper", [round(x, 6) for x in summary["clopper"]],
          "met", summary["criterion_met"],
          "prog", round(summary["progress"], 4),
          "end15", round(hdg["all_trials_end"]["frac15"], 4),
          "peak15", round(hdg["trajectory_peak_abs"]["frac15"], 4),
          "back", summary["n_backward_pitch"], "other", summary["n_other_fall"],
          flush=True)

if __name__ == "__main__":
    main()
