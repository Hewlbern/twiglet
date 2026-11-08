"""Why the 0.82258 kg head falls more often under the frozen trim.

Diagnostic only. pitch_auth logs commands and hip torque; it does not change q.
The 39 low-head falls are mechanism seeds, not a held-out.
"""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_shortbal_val as V

FALLS = [190007, 190039, 190107, 190295, 190313, 190321, 190325, 190495, 190533, 190659, 190688,
         191425, 191441, 191580, 191614, 192012, 192036, 192076, 192173, 192386, 192558, 192623,
         192641, 192730, 192806, 192937, 192939, 192978, 193079, 193364, 193369, 193489, 193526,
         193553, 193645, 193750, 193969, 193975, 193999]
SURV = [190100, 190101, 190102, 190103, 190104, 190105, 190108, 190109,
        190110, 190111, 190112, 190113, 190114, 190115, 190116, 190117]

def run(seeds, xml):
    gait, base, ztraj, zsb = V.load_models()
    jobs = V.B.jobs("cand", zsb, base, gait, ztraj, seeds, xml, 10.0)
    for j in jobs:
        j["pitch_auth"] = True
    rows = V.Y.run_jobs(jobs)
    out = []
    for r in rows:
        pa = r.get("pitch_auth") or {}
        out.append(dict(seed=r["seed"], fell=r["fell"], dx=round(float(r["dx"]), 3), **pa))
    return out

def brief(rows, name):
    fell = [r for r in rows if r["fell"] is not None]
    def col(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return None if not vals else float(np.median(vals))
    print(name, "fell", len(fell), "/", len(rows),
          "rate5", col("rate5"), "rate8", col("rate8"),
          "depth5", col("depth5"), "depth8", col("depth8"),
          "frac_cap", col("frac_capped"), "tau", col("med_tau"), "tau190", col("frac_tau190"),
          "soft", col("frac_soft"), "margin", col("med_fwd_margin_deg"),
          "trk8", col("trk8"), flush=True)

def main():
    # Confirm the logger does not move a known fall.
    raw = json.load(open(os.path.join(ROOT, "results", "head843_shortbal_low4000.json")))
    prev = next(r for r in raw["rows"] if r["seed"] == 190007)
    one = run([190007], V.H.LO)[0]
    print("check 190007", "now", one["fell"], "prev", prev["fell"], flush=True)
    if abs((one["fell"] or -1) - (prev["fell"] or -2)) > 1e-6:
        raise SystemExit("pitch_auth moved the fall")
    heads = (("lo", V.H.LO), ("nom", V.H.NOM), ("hi", V.H.HI))
    doc = {}
    for tag, xml in heads:
        doc["fall_" + tag] = run(FALLS, xml)
        brief(doc["fall_" + tag], "fall " + tag)
        doc["surv_" + tag] = run(SURV, xml)
        brief(doc["surv_" + tag], "surv " + tag)
    json.dump(doc, open(os.path.join(ROOT, "results", "head843_pitch_auth.json"), "w"), indent=1)
    print("wrote pitch_auth", flush=True)

if __name__ == "__main__":
    main()
