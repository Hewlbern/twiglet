"""Shared helpers for the twiglet geometry checks. The scene is scene/scene_v334_wig344.npz: the v3.34 body + head v3.30 +
hair v3.44 (c14) wig at rest, in the assembly frame (mm, trunk_assembly = identity), with 19 joints for forward kinematics.
It is made by tools/export_scene.py (provenance only)."""
import os, json, math, numpy as np, trimesh
from trimesh.transformations import rotation_matrix
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.environ.get("TWIGLET_GEOM_OUT", os.path.join(HERE, "out"))   # reference results live in results/ and are never overwritten
ARMA = ["upper_arm_L", "fore_arm_L", "finger_L", "upper_arm_R", "fore_arm_R", "finger_R"]
def load_scene(path=None):
    """-> items [(link, name, kind, V float32 (n,3) mm, F int32)], joints [(name, parent, child, point, axis, range)]"""
    Z = np.load(path or os.environ.get("TWIGLET_SCENE") or os.path.join(HERE, "scene", "scene_v334_wig344.npz"))
    meta = json.loads(str(Z["meta"]))
    items = [(ln, n, k, Z[f"V{i}"], Z[f"F{i}"]) for i, (ln, n, k) in enumerate(meta["items"])]
    joints = [(jn, par, ch, np.array(p), np.array(ax), tuple(rng)) for jn, par, ch, p, ax, rng in meta["joints"]]
    return items, joints
def TM(V, F): return trimesh.Trimesh(np.asarray(V, float), F, process=False)
def dec(m, n=6000): return m.simplify_quadric_decimation(face_count=n) if len(m.faces) > n else m
def make_fk(joints):
    def fk(q):
        Tw = {"trunk_assembly": np.eye(4)}
        for jn, par, ch, p, ax, rng in joints: Tw[ch] = Tw[par] @ rotation_matrix(math.radians(q.get(jn, 0.0)), ax, point=p)
        return Tw
    return fk
def save(name, out):
    os.makedirs(RESULTS, exist_ok=True); p = os.path.join(RESULTS, name); json.dump(out, open(p, "w"), indent=1, default=str); print("wrote", os.path.relpath(p, HERE)); return p
