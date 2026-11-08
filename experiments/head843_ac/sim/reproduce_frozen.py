"""Reproduce the frozen arms-forward scratch candidate and the no-overlay check.

Does not modify reliable.npy, the XML, or the scene. A full 200-seed batch is
not started from this file unless seeds are passed on the command line.

From sim/:

  python reproduce_frozen.py --identity

That compares seed 5000, randomized, 10 s, no overlay, with walk_search.evaluate.
The last recorded match is dx 2.082264 m.

  python reproduce_frozen.py --seeds 53000 53004

That runs the frozen candidate on those seeds and prints survival, speed, and
measured arm motion. The frozen config is the dict printed by --spec.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
os.environ.setdefault("TWIGLET_SCENE", os.path.join(ROOT, "geometry", "scene_v335ac.npz"))
_ARGV = sys.argv[1:]
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
import run_balance as B
import run_recover as R
from simlib import params_path
import numpy as np

def frozen():
    return R.base(name="frozen")

def main(argv):
    B.X = [float(v) for v in np.load(params_path(""))]
    spec = frozen()
    if "--spec" in argv or len(argv) == 1:
        print(json.dumps(dict(spec, command_sign=-1.0, params="params/reliable.npy",
                              T=10.0, rand=True, fall_tilt_deg=45, com_height_frac=0.6), indent=1))
    if "--identity" in argv:
        a = W.evaluate((np.array(B.X), 5000, True, 10.0))
        b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
        print("identity_dx", b["dx"], "match", abs(a["dx"] - b["dx"]) < 1e-6,
              "fell_match", bool(a["fell"]) == (b["fell"] is not None))
    if "--seeds" in argv:
        i = argv.index("--seeds")
        seeds = [int(s) for s in argv[i + 1:]]
        for seed in seeds:
            row = B.rollout(dict(x=B.X, seed=seed, rand=True, T=10.0, headarm=spec,
                                 command_sign=-1.0, measure_path=True))
            pp = row.get("motion_pp_deg") or {}
            mn = row.get("motion_mean_deg") or {}
            sh = None if "shoulder_L" not in pp else 0.5 * (pp["shoulder_L"] + pp["shoulder_R"])
            shm = None if "shoulder_L" not in mn else 0.5 * (mn["shoulder_L"] + mn["shoulder_R"])
            print(seed, "fell", row["fell"], "dx", round(row["dx"], 4),
                  "shoulder_mean", shm, "shoulder_pp", sh, "head_yaw_pp", pp.get("head_yaw"))

if __name__ == "__main__":
    main(_ARGV)
