"""Arm checks on the v3.34 scene (logic from body-v3.34-body/measure/arm_check.py part 1 and parts_check_v333.py part 3).
(1) Arm sweep: both arms vs torso shells, kilt, chest leaves and the head (neutral). Grid: shoulder -5..84 step 7.5, elbow 0..120 step 10,
    coupled soft limit 25-sh <= el <= min(110, 105-sh), gripper 0/60.  PASS: 0 hits.
(2) Joint sweeps: elbow -10..120, gripper -10..60, shoulder -10..110 (step 5). A pair counts only if it is not already touching at rest.
    PASS: 0 hits inside the soft limits (v3.34 record: elbow/gripper 0; shoulder hits only at -10 deg, outside the -5 soft limit).
usage: python arm_sweep.py"""
import numpy as np, trimesh
import geomlib as G
items, joints = G.load_scene(); fk = G.make_fk(joints); TM, dec, ARMA = G.TM, G.dec, G.ARMA
LM = {l: dec(trimesh.util.concatenate([TM(V, F) for ln, n, k, V, F in items if ln == l])) for l in ARMA}
env = trimesh.collision.CollisionManager()
for ln, n, k, V, F in items:
    if ln == "trunk_assembly" and (n.startswith(("torso_shell", "kilt", "leaf_chest")) or n == "hip_ring"): env.add_object(n, dec(TM(V, F), 8000))
    if ln == "head_assembly" and n.startswith("head3"): env.add_object("head:" + n, dec(TM(V, F), 20000))
out = {"tag": "v334_wig344"}; hits = {"shell": 0, "kilt": 0, "head": 0}; poses = 0; ex = []
arm = trimesh.collision.CollisionManager()
for l, m in LM.items(): arm.add_object(l, m)
for sh in np.arange(-5, 85, 7.5):
    for el in np.arange(0, 121, 10):
        if not (25 - sh <= el <= max(0.0, min(110, 105 - sh))): continue
        for gr in (0, 60):
            poses += 1; Tw = fk({"shoulder_L": sh, "elbow_L": el, "shoulder_R": sh, "elbow_R": el, "gripper_L": gr, "gripper_R": gr})
            for l in ARMA: arm.set_transform(l, Tw[l])
            hit, names = env.in_collision_other(arm, return_names=True)
            if hit:
                ks = set()
                for a, b in names:
                    e = a if a in env._objs else b
                    ks.add("shell" if e.startswith("torso") or e.startswith("leaf") else ("head" if e.startswith("head") else "kilt"))
                for k_ in ks: hits[k_] += 1
                if len(ex) < 6: ex.append(dict(sh=float(sh), el=float(el), gr=gr, pairs=sorted({f"{a}|{b}" for a, b in names})))
hits["poses"] = poses; out["arm_sweep"] = hits; out["arm_sweep_examples"] = ex; print("arm sweep", hits, flush=True)
IT = {n: (ln, TM(V, F)) for ln, n, k, V, F in items}
def sweep(moving_links, fixed_links, jn, angles):
    cm_f = trimesh.collision.CollisionManager(); cm_m = trimesh.collision.CollisionManager(); mv = {}
    for n, (ln, m) in IT.items():
        if ln in fixed_links: cm_f.add_object(n, m)
        if ln in moving_links: cm_m.add_object(n, m); mv[n] = ln
    base = None; res = {}
    for ang in [0.0] + list(angles):
        Tw = fk({jn: ang})
        for n, ln in mv.items(): cm_m.set_transform(n, Tw[ln])
        hit, pairs = cm_f.in_collision_other(cm_m, return_names=True); pairs = {tuple(sorted(p)) for p in pairs}
        if base is None: base = pairs; continue
        new = pairs - base
        if new: res[ang] = sorted("|".join(p) for p in new)
    return dict(rest_contacts=sorted("|".join(p) for p in base), hits=len(res), bad_angles=sorted(res)[:12], examples={k: res[k] for k in sorted(res)[:4]})
for s in "LR":
    out[f"elbow_sweep_{s}"] = sweep((f"fore_arm_{s}", f"finger_{s}"), (f"upper_arm_{s}",), f"elbow_{s}", np.arange(-10, 121, 5.0))
    out[f"gripper_sweep_{s}"] = sweep((f"finger_{s}",), (f"fore_arm_{s}",), f"gripper_{s}", np.arange(-10, 61, 5.0))
    out[f"shoulder_sweep_{s}"] = sweep((f"upper_arm_{s}", f"fore_arm_{s}", f"finger_{s}"), ("trunk_assembly",), f"shoulder_{s}", np.arange(-10, 111, 5.0))
    print(s, {k: (v["hits"], v["bad_angles"][:6]) for k, v in out.items() if k.endswith(f"_sweep_{s}")}, flush=True)
G.save("arm_sweep_v334_wig344.json", out)
