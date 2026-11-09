"""Preregistered qualification of the short-step balance trim.

Writes the preregistration when called with --write-prereg and otherwise
refuses to start unless that file's hashes still match. The nominal 10 s
block finishes for the candidate before the short-step baseline starts.
Nothing stops because an interval already clears or misses. Horizons and
mass files are stored separately and are not pooled.

Seeds 150000-156199 were unused by training, selection, and the 400-seed
screen. The frozen trajectory file is the paired baseline and is not rewritten.
"""
import os, sys, json, time, hashlib
from datetime import datetime, timezone
from math import comb
import numpy as np
from scipy.stats import beta
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
_WRITE_PREREG = "--write-prereg" in sys.argv
sys.argv = [sys.argv[0], "v3"]
import run_head843_traj as T
import run_head843_search as S
import run_head843_heading as H
import run_head843_yawstate as Y
import run_head843_shortbal as B

PREREG = os.path.join(ROOT, "results", "head843_shortbal_qual_prereg.json")
OUT = os.path.join(ROOT, "results", "head843_shortbal_qual.json")

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
        "shortbal_eval": sha(os.path.join(HERE, "run_head843_shortbal.py")),
        "traj_eval": sha(os.path.join(HERE, "run_head843_traj.py")),
        "simlib": sha(os.path.join(HERE, "simlib.py")),
        "episode": sha(os.path.join(HERE, "episode.py")),
    }

def write_prereg():
    if os.path.exists(PREREG):
        raise SystemExit("prereg already exists: " + PREREG)
    z = np.load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    traj = json.load(open(os.path.join(ROOT, "results", "head843_traj_qual_prereg.json")))
    doc = {
        "preregistered_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": "Counts and seeds fixed before any qualification trial. No retune. No early stop on a favorable or unfavorable interval. No substitution of a smaller sample. No pooling with 127xxx, 130xxx, the 400-seed screen, or the selection block.",
        "candidate": {
            "file": "params/head843_shortbal.npy",
            "sha256": hashes()["candidate_npy"],
            "base_gait_file": "params/head843_traj.npy",
            "base_gait_sha256": hashes()["baseline_traj_npy"],
            "z_short_balance": {k: float(v) for k, v in zip(B.KEYS, z)},
            "pitch_sign": 1.0,
            "cap_rad": 0.06,
            "yaw_command_clip_rad": 0.03,
            "hip_yaw_clip_rad": 0.07,
            "law": "short_step_balance after the slow-yaw integral and k_yaw_phase. Pitch branch only while pitch < -pitch_on and pitch rate < 0: stance thigh forward, swing foot less forward. Heading trim on the phase-stance hip only. No sole force.",
            "traj_z": traj["candidate"]["z"],
        },
        "baseline": {
            "name": "frozen short-step trajectory",
            "file": "params/head843_traj.npy",
            "sha256": "1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc",
            "note": "Same gait and controller as the 3978/4000 qualification, with short_balance absent. That 3978/4000 result is not rewritten and is not pooled.",
        },
        "hashes": hashes(),
        "physics": traj["physics"],
        "heads": traj["heads"],
        "criterion_nominal_10s": traj["criterion_nominal_10s"],
        "blocks": [
            {"name": "nom10", "seeds_inclusive": [150000, 153999], "n": 4000, "T_s": 10.0, "xml": "head843", "modes": ["cand", "base"], "priority": 1},
            {"name": "nom20", "seeds_inclusive": [154000, 154399], "n": 400, "T_s": 20.0, "xml": "head843", "modes": ["cand", "base"], "priority": 2},
            {"name": "lo10", "seeds_inclusive": [155000, 155199], "n": 200, "T_s": 10.0, "xml": "head823", "modes": ["cand", "base"], "priority": 3},
            {"name": "hi10", "seeds_inclusive": [156000, 156199], "n": 200, "T_s": 10.0, "xml": "head885", "modes": ["cand", "base"], "priority": 4},
        ],
        "order": "Complete cand nom10 (4000) before base nom10. Then nom20 both, lo10 both, hi10 both. Do not stop because an interval already clears or misses.",
        "screen_not_qualification": "Seeds 142000-142399 were a 400-seed paired screen. They are not part of this distribution.",
        "diagnostic_not_qualification": "The 22 misses of seeds 130000-133999 were used only to read the pitch-versus-yaw time order. They are not in this sample.",
    }
    json.dump(doc, open(PREREG, "w"), indent=1)
    print("wrote", PREREG, doc["preregistered_at_utc"], flush=True)

def wilson(k, n, z=1.96):
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math_sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ph, c - h, c + h]

def math_sqrt(x):
    return float(np.sqrt(x))

def clopper(k, n):
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [k / n, lo, hi]

def pair_sets(fa, fb):
    saved, cost, both = sorted(set(fb) - set(fa)), sorted(set(fa) - set(fb)), sorted(set(fa) & set(fb))
    n = len(saved) + len(cost)
    if n == 0:
        p = 1.0
    else:
        kk = min(len(saved), len(cost))
        p = min(1.0, 2 * sum(comb(n, i) for i in range(kk + 1)) / 2 ** n)
    return dict(saved=saved, cost=cost, both=both, net=len(saved) - len(cost), n_disc=n, mcnemar_p=p)

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
    return dict(
        seed=int(r["seed"]), fell=None if r["fell"] is None else float(r["fell"]),
        dx=float(r["dx"]), T=float(r["T"]), yaw=float(r["yaw_change"]),
        sh_m=sh_m, sh_p=sh_p, hy=pp.get("head_yaw"),
        frac_neg=at.get("frac_neg"), frac_abs=at.get("frac_abs"), gt10=pt.get("frac_gt10"),
        ankle_sat=sat(("left_ankle", "right_ankle")),
        hip_sat=sat(("left_hip_pitch", "right_hip_pitch")),
        main_sat=(r.get("load") or {}).get("main_sat"),
        pitch_end=float(r.get("pitch_end") or 0.0), roll_end=float(r.get("roll_end") or 0.0),
    )

def block_stats(rows):
    surv = [r for r in rows if r["fell"] is None]
    ys = np.degrees([r["yaw"] for r in rows])
    def mean(key, src):
        vals = [r[key] for r in src if r.get(key) is not None]
        return None if not vals else float(np.mean(vals))
    def med(key, src):
        vals = [r[key] for r in src if r.get(key) is not None]
        return None if not vals else float(np.median(vals))
    falls = [dict(seed=r["seed"], t=r["fell"], dx=round(r["dx"], 3),
                  yaw_deg=round(float(np.degrees(r["yaw"])), 1))
             for r in rows if r["fell"] is not None]
    return dict(
        succ=len(surv), n=len(rows),
        rate=len(surv) / len(rows),
        wilson=wilson(len(surv), len(rows)),
        clopper=clopper(len(surv), len(rows)),
        progress=float(np.mean([r["dx"] / r["T"] for r in rows])),
        speed=None if not surv else float(np.mean([r["dx"] / r["T"] for r in surv])),
        frac15=float(np.mean(np.abs(ys) > 15)),
        yaw_dist=dict(median=float(np.median(ys)), p10=float(np.percentile(ys, 10)),
                      p90=float(np.percentile(ys, 90)), min=float(ys.min()), max=float(ys.max())),
        shoulder_mean=med("sh_m", surv), shoulder_pp=med("sh_p", surv), head_yaw_pp=med("hy", surv),
        frac_neg=mean("frac_neg", rows), frac_abs=mean("frac_abs", rows), gt10=mean("gt10", rows),
        ankle_sat=mean("ankle_sat", rows), hip_sat=mean("hip_sat", rows), main_sat=mean("main_sat", rows),
        fell=[r["seed"] for r in rows if r["fell"] is not None],
        falls=falls,
    )

def load_state():
    if os.path.exists(OUT):
        return json.load(open(OUT))
    return {"prereg": PREREG, "blocks": {}, "pending": ["nom10_cand", "nom10_base", "nom20_cand", "nom20_base", "lo10_cand", "lo10_base", "hi10_cand", "hi10_base"]}

def save_state(st):
    json.dump(st, open(OUT, "w"), indent=1)

def run_block(name, seeds, xml, Ts, mode, gait, base, ztraj, zsb, st):
    key = name + "_" + mode
    have = {r["seed"] for r in st["blocks"].get(key, [])}
    todo = [s for s in seeds if s not in have]
    print(key, "resume", len(have), "todo", len(todo), flush=True)
    chunk = 500
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        rows = Y.run_jobs(B.jobs(mode, zsb, base, gait, ztraj, part, xml, Ts))
        st["blocks"].setdefault(key, []).extend(slim(r) for r in rows)
        st["blocks"][key].sort(key=lambda r: r["seed"])
        save_state(st)
        fell = sum(1 for r in st["blocks"][key] if r["fell"] is not None)
        print(key, "done", len(st["blocks"][key]), "falls", fell, flush=True)
    if key in st["pending"]:
        st["pending"].remove(key)
    save_state(st)

def main():
    if _WRITE_PREREG:
        write_prereg()
        return
    pre = json.load(open(PREREG))
    now = hashes()
    for k, v in pre["hashes"].items():
        if now[k] != v:
            raise SystemExit(f"hash changed {k} {v} -> {now[k]}")
    zsb = np.load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    if [round(float(v), 8) for v in zsb] != [round(pre["candidate"]["z_short_balance"][k], 8) for k in B.KEYS]:
        raise SystemExit("shortbal vector does not match prereg")
    if sha(os.path.join(ROOT, "params", "head843_traj.npy")) != "1842eb17a70ff0c4ea0c7fd472e2842f797b42dff699a132d994a8ca2819cddc":
        raise SystemExit("traj baseline hash changed")
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    ztraj = np.array([pre["candidate"]["traj_z"][k] for k in T.KEYS], float)
    xmls = {"head843": H.NOM, "head823": H.LO, "head885": H.HI}
    st = load_state()
    t0 = time.time()
    for block in pre["blocks"]:
        seeds = list(range(block["seeds_inclusive"][0], block["seeds_inclusive"][1] + 1))
        if len(seeds) != block["n"]:
            raise SystemExit("seed count mismatch " + block["name"])
        for mode in block["modes"]:
            run_block(block["name"], seeds, xmls[block["xml"]], block["T_s"], mode, gait, base, ztraj, zsb, st)
    summary = {}
    for block in pre["blocks"]:
        name = block["name"]
        a = block_stats(st["blocks"][name + "_cand"])
        b = block_stats(st["blocks"][name + "_base"])
        summary[name] = dict(cand=a, base=b, pair=pair_sets(a["fell"], b["fell"]))
        c = summary[name]
        print(name, f"{a['succ']}/{a['n']}", "vs", f"{b['succ']}/{b['n']}",
              "net", c["pair"]["net"], "p", c["pair"]["mcnemar_p"],
              "prog", round(a["progress"], 4), round(b["progress"], 4),
              "y15", round(a["frac15"], 4), round(b["frac15"], 4),
              "wilson", [round(x, 6) for x in a["wilson"]], flush=True)
    nom = summary["nom10"]["cand"]
    summary["criterion_nominal_10s_met"] = bool(nom["wilson"][1] >= 0.995)
    summary["seconds"] = round(time.time() - t0, 1)
    summary["pending"] = st["pending"]
    st["summary"] = summary
    save_state(st)
    print("CRITERION", summary["criterion_nominal_10s_met"], "pending", st["pending"], flush=True)

if __name__ == "__main__":
    main()
