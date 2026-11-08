"""Hypothetical mass and COM edits. The canonical XML is not written.

Train 87000-87079 with the frozen controller. A case is only taken to a fresh
held-out if it keeps the arm wave and survives at least four more walks than
the unedited model on this block. That held-out is still a mass-only model
edit, not a printable part.

  python run_mass_sensitivity.py
"""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["TWIGLET_XML"] = os.path.join(HERE, "models", "twiglet_v3_v335ac.xml")
os.environ["TWIGLET_PARAMS"] = os.path.join(ROOT, "params", "reliable.npy")
sys.argv = [sys.argv[0], "v3"]
import walk_search as W
import run_balance as B
import run_recover as R
import run_ankle as A
from simlib import params_path
import mujoco

TRAIN = (87000, 80)
WIG_G = 0.18609

def inventory():
    m, _ = __import__("manoeuvre")._model(None)
    rows = []
    for i in range(m.nbody):
        name = m.body(i).name
        if not name:
            continue
        rows.append(dict(name=name, mass=float(m.body_mass[i]),
                         ipos=[round(float(x), 5) for x in m.body_ipos[i]]))
    return rows

CASES = [
    ("baseline", None),
    ("head_m50_inertia", {"head_assembly": {"mass_delta": -0.050, "inertia": "with_mass"}}),
    ("head_m100_inertia", {"head_assembly": {"mass_delta": -0.100, "inertia": "with_mass"}}),
    ("head_wig_inertia", {"head_assembly": {"mass_delta": -WIG_G, "inertia": "with_mass"}}),
    ("head_wig_com_only", {"head_assembly": {"mass_delta": -WIG_G, "inertia": "fixed"}}),
    ("head_com_back_10mm", {"head_assembly": {"ipos_x": -0.010}}),
]

def main():
    t0 = time.time()
    B.X = [float(v) for v in np.load(params_path(""))]
    a = W.evaluate((np.array(B.X), 5000, True, 10.0))
    b = B.rollout(dict(x=B.X, seed=5000, rand=True, T=10.0))
    if abs(a["dx"] - b["dx"]) > 1e-6 or bool(a["fell"]) != (b["fell"] is not None):
        raise SystemExit("no-overlay path changed")
    frozen = R.base(name="frozen")
    if frozen.get("k_plan") or frozen.get("historical_fore_aft") or frozen.get("plan_from_arms"):
        raise SystemExit("forward-foot plan is still on the frozen spec")
    print("identity", round(b["dx"], 6), flush=True)
    inv = inventory()
    head = next(r for r in inv if r["name"] == "head_assembly")
    print("head", head, "total", round(sum(r["mass"] for r in inv), 4), flush=True)
    table = []
    raw = {}
    for name, edit in CASES:
        rows = A.run(B.jobs(TRAIN[0], TRAIN[1], headarm=frozen, command_sign=-1.0, pitch_tail=True, mass_edit=edit))
        s = B.summarize(rows)
        s["name"] = name
        s["pitch_tail"] = A.tail(rows)
        s["ankle_sat"] = A.joint_sat(rows, ("left_ankle", "right_ankle"))
        s["hip_pitch_sat"] = A.joint_sat(rows, ("left_hip_pitch", "right_hip_pitch"))
        s["yaw_dist"] = A.yaw_dist(rows)
        B.show(name, s)
        pt = s["pitch_tail"]
        print("  gt8", round(pt.get("frac_gt8") or 0, 4), "n>10", pt.get("n_max_gt10"),
              "yaw15", round(s["yaw_dist"]["frac_exceeding_15deg"], 3), flush=True)
        table.append(A.slim(s))
        raw[name] = s
    base = raw["baseline"]
    promising = []
    for s in table:
        if s["name"] == "baseline" or not A.pose_ok(s):
            continue
        if s["succ"] >= base["succ"] + 4:
            promising.append(s["name"])
    print("PROMISING", promising, flush=True)
    rep = dict(
        identity_dx=float(b["dx"]),
        note="In-memory mass edits. Not printable designs. Wig 186.09 g is a stated print estimate, not a body in the XML.",
        inventory=inv,
        train_seeds=list(TRAIN),
        train=table,
        promising=promising,
        seconds=round(time.time() - t0, 1),
    )
    path = os.path.join(ROOT, "results", "mass_sensitivity.json")
    with open(path, "w") as f:
        json.dump(rep, f, indent=1, default=float)
    print("wrote", path, flush=True)

if __name__ == "__main__":
    main()
