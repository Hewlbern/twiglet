"""v3.34 copy (same parts, current out/asm = v3.34). sim input (v3.33; = mass_v332.py + the v3.33 arm parts): add the changed-part mass deltas (solid PLA 1.24 g/cm3, the rev C convention) to the MJCF bodies they ride on.
Delta = new - old part (volume and COM, asm/rest frame) -> point mass at the delta COM, converted to the body frame by MuJoCo FK at qpos0
(qpos0 == asm rest pose), merged into the body's inertial (parallel-axis, fullinertia).  Writes sim/twiglet_v3_v334.xml + sim/mass_v334.json.
  usage: mass_v332.py [stage prefixes comma list]  (default all)"""
import os, sys, json, numpy as np, trimesh, mujoco, xml.etree.ElementTree as ET, warnings
warnings.filterwarnings("ignore")
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = os.path.join(H, "sim"); R = H + "/blender/in/"; A = H + "/blender/out/asm/"
RHO = 1.24e-3; PT = json.load(open(R + "print_T.json")); only = [x for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else []) if x]
def ld(f, T=None):
    m = trimesh.load(f); m.merge_vertices()
    if T is not None: m.apply_transform(np.array(T))
    return m
pairs = []  # (body, old mesh or None, new mesh, name)
for s, b2, ft in (("L", "knee_and_ankle_assembly_2", "foot_assembly"), ("R", "knee_and_ankle_assembly_4", "foot_assembly_2")):
    pairs += [(f"fore_arm_{s}", ld(R + f"ref/gripper_housing_{s}.stl"), ld(A + f"gripper_housing_{s}.stl"), f"gripper_housing_{s}"),
              (f"finger_{s}", ld(R + f"ref/finger_moving_{s}.stl"), ld(A + f"finger_moving_{s}.stl"), f"finger_moving_{s}"),
              (ft, ld(R + f"ref/boot_{s}.stl"), ld(A + f"boot_{s}.stl"), f"boot_{s}")]
    for fb in ("front", "back"):
        n = f"shin_cover_{fb}_{s}"; pairs.append((b2, ld(R + f"stl_v331c/v331_{n}.stl", PT[n]), ld(A + n + ".stl"), n))
for s in "LR":       # v3.33 arm parts (rev C -> v3.33; new parts have no old mesh)
    pairs += [(f"upper_arm_{s}", ld(R + f"ref/shoulder_sleeve_{s}.stl"), ld(A + f"shoulder_sleeve_{s}.stl"), f"shoulder_sleeve_{s}"),
              (f"upper_arm_{s}", ld(R + f"ref/leaf_shoulder_{s}.stl"), ld(A + f"leaf_shoulder_{s}.stl"), f"leaf_shoulder_{s}"),
              (f"upper_arm_{s}", None, ld(A + f"vine_upper_{s}.stl"), f"vine_upper_{s}"),
              (f"fore_arm_{s}", ld(R + f"ref/elbow_sleeve_{s}.stl"), ld(A + f"elbow_sleeve_{s}.stl"), f"elbow_sleeve_{s}"),
              (f"fore_arm_{s}", ld(R + f"ref/leaf_elbow_{s}.stl"), ld(A + f"leaf_elbow_{s}.stl"), f"leaf_elbow_{s}"),
              (f"fore_arm_{s}", None, ld(A + f"vine_fore_{s}.stl"), f"vine_fore_{s}")]
for i in range(10): pairs.append(("trunk_assembly", ld(R + f"asm_kilt_petal_{i:02d}.stl"), ld(A + f"kilt_petal_{i:02d}.stl"), f"kilt_petal_{i:02d}"))
pairs.append(("trunk_assembly", None, ld(A + "chest_vine.stl"), "chest_vine"))
if only: pairs = [p for p in pairs if any(p[3].startswith(o) for o in only)]
src = os.path.join(S, "twiglet_v3_v331c_head330.xml"); m = mujoco.MjModel.from_xml_path(src); d = mujoco.MjData(m); d.qpos[:] = m.qpos0; mujoco.mj_kinematics(m, d)
bt = m.body("trunk_assembly").id; Rt = d.xmat[bt].reshape(3, 3); pt = d.xpos[bt]
T = ET.parse(src); rep = {}
def shift(Jm, mm, r): return Jm + mm * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
for body, o, n, name in pairs:
    vo = o.volume if o is not None else 0.0; co = o.center_mass if o is not None else np.zeros(3); dv = n.volume - vo
    if abs(dv) < 1e-6: continue
    c = (n.volume * n.center_mass - vo * co) / dv; g = dv * RHO
    b = m.body(body).id; Rb = Rt.T @ d.xmat[b].reshape(3, 3); pb = Rt.T @ (d.xpos[b] - pt)
    p_body = Rb.T @ (c / 1000.0 - pb)       # m, body frame
    E = [e for e in T.iter("body") if e.get("name") == body][0]; I = E.find("inertial")
    m0 = float(I.get("mass")); c0 = np.array([float(v) for v in I.get("pos").split()]); f = [float(v) for v in I.get("fullinertia").split()]
    J0 = np.array([[f[0], f[3], f[4]], [f[3], f[1], f[5]], [f[4], f[5], f[2]]]); dm = g / 1000.0; M = m0 + dm; cn = (m0 * c0 + dm * p_body) / M
    Jn = shift(J0, m0, c0 - cn); Jn = Jn + dm * (np.dot(p_body - cn, p_body - cn) * np.eye(3) - np.outer(p_body - cn, p_body - cn))
    I.set("mass", f"{M:.6g}"); I.set("pos", " ".join(f"{v:.6g}" for v in cn)); I.set("fullinertia", " ".join(f"{v:.6g}" for v in (Jn[0, 0], Jn[1, 1], Jn[2, 2], Jn[0, 1], Jn[0, 2], Jn[1, 2])))
    rep[name] = dict(body=body, dg=round(g, 2), at_mm=np.round(c, 1).tolist())
out = os.path.join(S, "twiglet_v3_v334.xml"); T.write(out)
mm2 = mujoco.MjModel.from_xml_path(out); tot = float(mm2.body_mass.sum()); rep["_total_kg"] = round(tot, 4); rep["_base_total_kg"] = round(float(m.body_mass.sum()), 4)
rep["_by_body_g"] = {}
for k, v in rep.items():
    if not k.startswith("_"): rep["_by_body_g"][v["body"]] = round(rep["_by_body_g"].get(v["body"], 0) + v["dg"], 2)
json.dump(rep, open(os.path.join(S, "mass_v334.json"), "w"), indent=1); print(json.dumps(rep["_by_body_g"]), rep["_base_total_kg"], "->", rep["_total_kg"])
