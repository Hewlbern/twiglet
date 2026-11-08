"""Read the qualification falls. Does not change any hashed file."""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import run_head843_traj as T
import run_head843_search as S
import run_head843_heading as H
import run_head843_yawstate as Y
import run_head843_shortbal as B

def main():
    search = json.load(open(os.path.join(ROOT, "results", "head843_search.json")))
    gait = np.array([search["searched_gait"][k] for k in S.KEYS], float)
    base = np.array([search["searched_ctrl"][k] for k in S.CTRL_KEYS], float)
    pre = json.load(open(os.path.join(ROOT, "results", "head843_shortbal_qual_prereg.json")))
    ztraj = np.array([pre["candidate"]["traj_z"][k] for k in T.KEYS], float)
    zsb = np.load(os.path.join(ROOT, "params", "head843_shortbal.npy"))
    cases = [
        ("nom", 150216, H.NOM, 10.0), ("nom", 150258, H.NOM, 10.0),
        ("nom", 151246, H.NOM, 10.0), ("nom", 152541, H.NOM, 10.0),
        ("saved", 150272, H.NOM, 10.0), ("saved", 152339, H.NOM, 10.0),
        ("saved", 152805, H.NOM, 10.0), ("saved", 153782, H.NOM, 10.0),
        ("long", 154186, H.NOM, 20.0), ("long", 154342, H.NOM, 20.0),
        ("low", 155188, H.LO, 10.0),
    ]
    out = []
    for tag, seed, xml, Ts in cases:
        for mode in ("cand", "base"):
            js = B.jobs(mode, zsb, base, gait, ztraj, [seed], xml, Ts)
            js[0]["keep_trace"] = True
            row = Y.run_jobs(js)[0]
            tr = row.get("trace") or []
            y0 = tr[0]["yaw"] if tr else 0.0
            def dyaw(p):
                a = p["yaw"] - y0
                return math.degrees((a + math.pi) % (2 * math.pi) - math.pi)
            fell = row["fell"]
            def first(pred):
                for p in tr:
                    if pred(p):
                        return round(p["t"], 2)
                return None
            pre_s = None
            if fell is not None and tr:
                target = fell - 0.4
                pre_s = min(tr, key=lambda p: abs(p["t"] - target))
            # pitch rate from neighbouring samples
            pr = None
            if pre_s is not None:
                i = tr.index(pre_s)
                if 0 < i < len(tr) - 1:
                    dt = tr[i + 1]["t"] - tr[i - 1]["t"]
                    if dt > 0:
                        pr = math.degrees((tr[i + 1]["pitch"] - tr[i - 1]["pitch"]) / dt)
            rec = dict(
                tag=tag, seed=seed, mode=mode, fell=fell, dx=round(float(row["dx"]), 3),
                yaw15=first(lambda p: abs(dyaw(p)) > 15),
                roll8=first(lambda p: abs(math.degrees(p["roll"])) > 8),
                pitch8=first(lambda p: math.degrees(p["pitch"]) < -8),
            )
            if pre_s is not None:
                rec.update(
                    pre_t=round(pre_s["t"], 2),
                    pre_yaw=round(dyaw(pre_s), 1),
                    pre_roll=round(math.degrees(pre_s["roll"]), 1),
                    pre_pitch=round(math.degrees(pre_s["pitch"]), 1),
                    pre_pr=None if pr is None else round(pr, 1),
                )
            out.append(rec)
            print(tag, seed, mode, "fell", fell, "pitch8", rec["pitch8"], "yaw15", rec["yaw15"],
                  "pre", rec.get("pre_pitch"), rec.get("pre_roll"), rec.get("pre_yaw"), rec.get("pre_pr"), flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "head843_shortbal_falls.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
