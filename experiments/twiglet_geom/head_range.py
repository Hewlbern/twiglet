"""Wig-vs-arm sweep + whole-head range check (from hair-v3.40/checks/arm_head_check.py; the logic is unchanged, only the scene loading is new).
(1) wig vs arms at head yaw 0/-45/+45 on the grid sh -10..110 step 10, el -10/0/30/60/90/110, gripper 0/45 (156 poses per yaw).
    Counts raw hits and hits inside the arm soft limits (shoulder -5..84, 25-sh <= el <= min(110, 105-sh)).
(2) whole-head range on a 7x9x5 grid of head pitch/yaw/roll over the joint ranges (315 poses), arms at rest (sh 8, el 20).
    Counts poses where any head3 part touches a printed trunk part or an arm link, and poses where the wig touches.
PASS (hair budget, same since v3.40): wig-arm hits in soft limits = 0 at every yaw; head range ~154/315; wig-only poses = 0.
usage: python head_range.py [tag] [--no-range]"""
import sys, numpy as np, trimesh
import geomlib as G
tag = next((a for a in sys.argv[1:] if not a.startswith("--")), "v334_wig344")
items, joints = G.load_scene(); fk = G.make_fk(joints); TM, dec, ARMA = G.TM, G.dec, G.ARMA
wig = [TM(V, F) for ln, n, k, V, F in items if n == "head3_fringe"][0]
LM = {l: dec(trimesh.util.concatenate([TM(V, F) for ln, n, k, V, F in items if ln == l])) for l in ARMA}
out = {"tag": tag, "scene": "scene_v334_wig344.npz"}; cw = trimesh.collision.CollisionManager(); cw.add_object("wig", wig); diag = []
for yaw in (0, -45, 45):
    nh = ns = n = 0
    for sh in range(-10, 111, 10):
        for el in (-10, 0, 30, 60, 90, 110):
            for gr in (0, 45):
                Tw = fk({"head_yaw": yaw, "shoulder_L": sh, "elbow_L": el, "gripper_L": gr, "shoulder_R": sh, "elbow_R": el, "gripper_R": gr}); n += 1
                hl = [l for l, mm in LM.items() if cw.in_collision_single(mm, transform=np.linalg.inv(Tw["head_assembly"]) @ Tw[l])]
                if hl:
                    soft = bool(-5 <= sh <= 84 and 25 - sh <= el <= max(0.0, min(110, 105 - sh))); nh += 1; ns += soft; diag.append(dict(yaw=yaw, sh=sh, el=el, gr=gr, links=hl, in_soft=soft))
    out[f"wig_arm_yaw_{yaw}"] = dict(poses=n, hits=nh, hits_in_soft=ns); print("wig-arm yaw", yaw, out[f"wig_arm_yaw_{yaw}"], flush=True)
out["wig_arm_hits"] = diag
if "--no-range" not in sys.argv:
    TRP = {n: TM(V, F) for ln, n, k, V, F in items if ln == "trunk_assembly" and (k in ("pla_new", "pla_leaf", "kilt") or k.startswith("repl_")) and "frame_v331" not in n}
    HEADP = {n: TM(V, F) for ln, n, k, V, F in items if ln == "head_assembly" and n.startswith("head3_")}
    J = {jn: (par, ch, p, ax, rng) for jn, par, ch, p, ax, rng in joints}
    ct = trimesh.collision.CollisionManager()
    for tn, tm in TRP.items(): ct.add_object("trunk:" + tn, dec(tm, 8000))
    for l, mm in LM.items(): ct.add_object(l, mm)
    HD = {hn[6:]: dec(hm, 20000) for hn, hm in HEADP.items()}
    rg = {j: J[j][4] for j in ("head_pitch", "head_yaw", "head_roll")}
    def grid(j, n): lo, hi = rg[j]; return np.degrees(np.linspace(lo, hi, n)) if abs(hi) < 7 else np.linspace(lo, hi, n)
    REST = {"shoulder_L": 8, "elbow_L": 20, "shoulder_R": 8, "elbow_R": 20}; n = 0; hits = 0; wigp = 0; wigonly = 0; by = {}
    for p in grid("head_pitch", 7):
        for y in grid("head_yaw", 9):
            for r in grid("head_roll", 5):
                Tw = fk(dict(REST, head_pitch=p, head_yaw=y, head_roll=r)); n += 1
                for l in ARMA: ct.set_transform(l, Tw[l])
                ph = []
                for hn, hm in HD.items():
                    c, names = ct.in_collision_single(hm, transform=Tw["head_assembly"], return_names=True)
                    if c:
                        ph.append(hn)
                        for nm in names: by[f"{hn} x {nm}"] = by.get(f"{hn} x {nm}", 0) + 1
                hits += bool(ph); wigp += "fringe" in ph; wigonly += (ph == ["fringe"])
    out["head_range"] = dict(poses=n, poses_with_any_head_contact=hits, poses_wig_contact=wigp, poses_wig_only=wigonly, pairs=by); print("range", {k: v for k, v in out["head_range"].items() if k != "pairs"}, flush=True)
G.save(f"head_range_{tag}.json", out)
