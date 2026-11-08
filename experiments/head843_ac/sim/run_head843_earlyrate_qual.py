"""Preregistered tests of the early pitch-rate candidate.

Separate from the frozen shortbal checkpoint. No retune during the run.
No pooling across blocks. Nothing stops because an interval already cleared
or missed.
"""
import os, sys, json, time, hashlib
from datetime import datetime, timezone
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_MODE = "write" if "--write-prereg" in sys.argv else "run"
sys.path.insert(0, HERE)
os.environ.setdefault("TWIGLET_XML", os.path.join(HERE, "models", "twiglet_v3_v335ac.xml"))
os.environ.setdefault("TWIGLET_PARAMS", os.path.join(ROOT, "params", "reliable.npy"))
import run_head843_earlyrate as E
import run_head843_shortbal_val as V

PREREG = os.path.join(ROOT, "results", "head843_earlyrate_qual_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_earlyrate_qual.json")
FROZEN = "52d70ff1fffeb1a68085b97401f78154eedc8f8d81fc45088dde3800330073b5"

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def hashes():
    h = V.hashes()
    h["early_npy"] = sha(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    h["manoeuvre"] = sha(os.path.join(HERE, "manoeuvre.py"))
    h["early_runner"] = sha(os.path.join(HERE, "run_head843_earlyrate.py"))
    h["qual_runner"] = sha(os.path.join(HERE, "run_head843_earlyrate_qual.py"))
    return h

def write_prereg():
    if os.path.exists(PREREG):
        raise SystemExit("prereg already exists")
    h = hashes()
    if h["candidate_npy"] != FROZEN:
        raise SystemExit("shortbal checkpoint changed")
    z = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    doc = {
        "preregistered_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": "Separate lineage from params/head843_shortbal.npy. Counts fixed before any trial. No retune, no cap change, no optional stop, no pooling with the shortbal qualifications or with the 400-seed screen. A simulated distribution, not a hardware certification.",
        "candidate": {
            "file": "params/head843_earlyrate.npy",
            "sha256": h["early_npy"],
            "z_early": {k: float(v) for k, v in zip(E.KEYS, z)},
            "frozen_short_balance": {"pitch_on": 0.08724, "k_pitch": 0.93511, "k_rate": 0.22824, "k_yaw": 0.12509, "pitch_sign": 1.0, "cap_rad": 0.06},
            "law": "Same hip geometry and 0.06 rad cap as the frozen trim. Before pitch reaches pitch_on, if pitch is below early_on and pitch rate is more backward than rate_on, the rate term alone moves the stance thigh forward. IMU pitch and pitch rate, plus the gait phase. No mass, no sole force.",
        },
        "baseline": {"file": "params/head843_shortbal.npy", "sha256": FROZEN, "note": "rate_on absent, so the early branch is off."},
        "hashes": h,
        "screen_not_this_test": "Seeds 202000-202923. 400/400 versus 397/400 on the low head is not this qualification.",
        "blocks": [
            {"name": "lo10", "seeds_inclusive": [210000, 213999], "n": 4000, "T_s": 10.0, "xml": "head823", "priority": 1},
            {"name": "nom10", "seeds_inclusive": [214000, 217999], "n": 4000, "T_s": 10.0, "xml": "head843", "priority": 2},
            {"name": "nom20", "seeds_inclusive": [218000, 221999], "n": 4000, "T_s": 20.0, "xml": "head843", "priority": 3},
            {"name": "hi10", "seeds_inclusive": [222000, 222999], "n": 1000, "T_s": 10.0, "xml": "head885", "priority": 4},
        ],
        "criterion": "Two-sided 95% Wilson lower bound >= 0.995 on the early candidate, separately for each block. Clopper-Pearson is reported and is not a second gate. The shortbal nominal qualifications are not inherited.",
    }
    json.dump(doc, open(PREREG, "w"), indent=1)
    print("wrote", PREREG, doc["preregistered_at_utc"], flush=True)

def slim(r):
    row = V.slim(r)
    pt = r.get("pitch_tail") or {}
    row["min_pitch"] = pt.get("min_deg")
    return row

def main():
    if _MODE == "write":
        write_prereg()
        return
    pre = json.load(open(PREREG))
    now = hashes()
    for k, v in pre["hashes"].items():
        if now[k] != v:
            raise SystemExit("hash changed " + k)
    early = np.load(os.path.join(ROOT, "params", "head843_earlyrate.npy"))
    xmls = {"head823": V.H.LO, "head843": V.H.NOM, "head885": V.H.HI}
    st = json.load(open(OUT)) if os.path.exists(OUT) else {"prereg": PREREG, "blocks": {}, "pending": [b["name"] + "_" + m for b in pre["blocks"] for m in ("early", "base")]}
    t0 = time.time()
    for block in pre["blocks"]:
        seeds = list(range(block["seeds_inclusive"][0], block["seeds_inclusive"][1] + 1))
        if len(seeds) != block["n"]:
            raise SystemExit("seed count " + block["name"])
        xml = xmls[block["xml"]]
        for mode in ("early", "base"):
            key = block["name"] + "_" + mode
            have = {r["seed"] for r in st["blocks"].get(key, [])}
            todo = [s for s in seeds if s not in have]
            print(key, "resume", len(have), "todo", len(todo), flush=True)
            chunk = 200 if block["T_s"] >= 20 else 400
            for i in range(0, len(todo), chunk):
                part = todo[i:i + chunk]
                js = E.jobs(mode, early, part, xml, block["T_s"])
                for j in js:
                    j["keep_trace"] = True
                st["blocks"].setdefault(key, []).extend(slim(r) for r in V.Y.run_jobs(js))
                st["blocks"][key].sort(key=lambda r: r["seed"])
                json.dump({"prereg": st["prereg"], "pending": st["pending"], "blocks": st["blocks"]}, open(OUT, "w"), default=float)
                fell = sum(1 for r in st["blocks"][key] if r["fell"] is not None)
                print(key, "done", len(st["blocks"][key]), "falls", fell, flush=True)
            if key in st["pending"] and len(st["blocks"].get(key, [])) == block["n"]:
                st["pending"].remove(key)
    summary = {}
    for block in pre["blocks"]:
        name = block["name"]
        summary[name] = {}
        for mode in ("early", "base"):
            rows = st["blocks"][name + "_" + mode]
            a = V.block_stats(rows)
            mins = [r["min_pitch"] for r in rows if r.get("min_pitch") is not None]
            a["min_pitch"] = float(np.mean(mins)) if mins else None
            a["p10_min"] = float(np.percentile(mins, 10)) if mins else None
            summary[name][mode] = a
        fa, fb = summary[name]["early"]["fell"], summary[name]["base"]["fell"]
        saved, cost = sorted(set(fb) - set(fa)), sorted(set(fa) - set(fb))
        summary[name]["pair"] = dict(saved=len(saved), cost=len(cost), net=len(saved) - len(cost))
        e = summary[name]["early"]
        print(name, f"{e['succ']}/{e['n']}", "wilson", [round(x, 6) for x in e["wilson"]],
              "met", e["wilson"][1] >= 0.995, "net", summary[name]["pair"]["net"],
              "end15", round(e["heading"]["all_trials_end"]["frac15"], 4),
              "peak15", round(e["heading"]["trajectory_peak_abs"]["frac15"], 4),
              "back", e["n_backward_pitch"], flush=True)
    st["summary"] = summary
    st["seconds"] = round(time.time() - t0, 1)
    st["criteria"] = {k: bool(v["early"]["wilson"][1] >= 0.995) for k, v in summary.items()}
    # Drop raw rows from the final file? Keep them; the low4000 file did. They are large for 4 blocks.
    json.dump(st, open(OUT, "w"), default=float)
    print("DONE", st["pending"], st["criteria"], flush=True)

if __name__ == "__main__":
    main()
