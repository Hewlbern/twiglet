"""MJCF for body v3 (same mass rules as body-v2/sim/gen_mjcf.py, plus the v3 part kinds):
  servo32 (Feetech STS3032 case) 20 g, horn32 1 g
  head3 (head-v3 printed parts) LIGHT print: 0.8 mm skin (2 walls) + 8 % infill, PLA 1.24 g/cm3
  display (2.1" round 480x480 module incl. PCB/FPC) 40 g each + 10 g eye-driver board (head-v3 estimate)
  eyering: visual only (0 g)
Arm joints (shoulder/elbow/gripper) get the STS3032 actuator: ctrlrange +-0.441 N.m (4.5 kg.cm stall @6 V), armature 0.004.
Usage: python gen_mjcf_v3.py  -> twiglet_v3.xml, mass_report_v3.json, meshes/"""
import os, sys, pickle, json, numpy as np, trimesh, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); BV3 = os.path.dirname(HERE); ROOT = os.path.dirname(BV3)
sys.path[:0] = [os.path.join(ROOT, "body-v2", "sim"), BV3]
import gen_mjcf as G
import view_v3 as V3
S32_STALL, S32_ARM = 0.441, 0.004
G.colour_of = V3.colour_of; G.COL = V3.COL
G.FIXED["eye_driver"] = 10.0
_pm = G.part_mass
def part_mass(name, m, kind, vref):
    V = abs(m.volume) if m.is_volume else abs(m.convex_hull.volume) * 0.35
    if kind == "servo32": return 20.0, V
    if kind == "horn32": return 1.0, V
    if kind == "display": return 40.0, V
    if kind == "eyering": return 0.0, V
    if kind == "kilt": return 1.24e-3 * V, V                 # v3.16 printed kilt petals: thin solid PLA
    if kind == "head3" and "snout" in name and os.environ.get("SNOUT_INFILL"):   # v3.11: what-if print setting for the snout only
        A = m.area; f = float(os.environ["SNOUT_INFILL"]); solid = min(V, A * 0.8) + f * max(0.0, V - A * 0.8); return 1.24e-3 * solid, V
    if kind == "head3" and "fringe" in name:   # v3.17: v3.19 wig printed with 3 % lightning infill (env WIG_INFILL / WIG_SKIN = what-if)
        A = m.area; f = float(os.environ.get("WIG_INFILL", "0.045")); sk = float(os.environ.get("WIG_SKIN", "0.8")); solid = min(V, A * sk) + f * max(0.0, V - A * sk); return 1.24e-3 * solid, V
    if kind == "head3":
        A = m.area; solid = min(V, A * 0.8) + 0.08 * max(0.0, V - A * 0.8); return 1.24e-3 * solid, V
    return _pm(name, m, kind, vref)
G.part_mass = part_mass
def v3_model(P=None):
    import design_v3 as D3
    M = pickle.load(open(os.path.join(BV3, ".cache", "v3model.pkl"), "rb")) if P is None else D3.build(P)
    M = dict(M); M["links"] = {k: list(v) for k, v in M["links"].items()}; M["name"] = "v3"
    # eye-driver board (ESP32-S3) behind the displays, inside the head
    disp = [m for n, m, k in M["links"]["head_assembly"] if k == "display"]
    c = np.mean([d.bounds.mean(0) for d in disp], axis=0) + [-35.0, 0, -5.0]
    b = trimesh.creation.box(extents=(20, 40, 25)); b.apply_translation(c)
    M["links"]["head_assembly"].append(("eye_driver", b, "elec_eye_driver"))
    return M
def write_v3(M, variant="v3", out_dir=HERE):
    fn = G.write(M, variant, out_dir)
    t = ET.parse(fn); r = t.getroot()
    for j in r.iter("joint"):
        if j.get("name", "").startswith(("shoulder_", "elbow_", "gripper_")): j.set("armature", str(S32_ARM))
    for a in r.iter("motor"):
        if a.get("name", "").startswith(("shoulder_", "elbow_", "gripper_")): a.set("ctrlrange", f"{-S32_STALL} {S32_STALL}")
    t.write(fn); return fn
if __name__ == "__main__":
    write_v3(v3_model())
