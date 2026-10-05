"""diag (rev C): add point masses (g, mm in the trunk_assembly frame) to the trunk inertial of an MJCF -> new xml. Measurement/sim input only."""
import sys, json, numpy as np, xml.etree.ElementTree as ET
def add_masses(src, dst, pts):     # pts: [(g, (x,y,z) mm)]
    T = ET.parse(src); b = [e for e in T.iter("body") if e.get("name") == "trunk_assembly"][0]; I = b.find("inertial")
    m0 = float(I.get("mass")); c0 = np.array([float(v) for v in I.get("pos").split()])
    f = [float(v) for v in I.get("fullinertia").split()]; J0 = np.array([[f[0], f[3], f[4]], [f[3], f[1], f[5]], [f[4], f[5], f[2]]])
    ms = np.array([p[0] / 1000 for p in pts]); ps = np.array([np.array(p[1]) / 1000 for p in pts]).reshape(-1, 3)
    M = m0 + ms.sum(); c = (m0 * c0 + (ms[:, None] * ps).sum(0)) / M
    def shift(J, m, r): return J + m * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    J = shift(J0, m0, c0 - c)
    for mi, pi in zip(ms, ps): J = shift(J, mi, pi - c) if mi > 0 else J - (-mi) * (np.dot(pi - c, pi - c) * np.eye(3) - np.outer(pi - c, pi - c))
    I.set("mass", f"{M:.6g}"); I.set("pos", " ".join(f"{v:.6g}" for v in c))
    I.set("fullinertia", " ".join(f"{v:.6g}" for v in (J[0, 0], J[1, 1], J[2, 2], J[0, 1], J[0, 2], J[1, 2]))); T.write(dst)
    print(dst, "trunk", round(m0, 4), "->", round(M, 4), "com mm", (c0 * 1000).round(2), "->", (c * 1000).round(2))
if __name__ == "__main__":
    a = json.load(open(sys.argv[3])); add_masses(sys.argv[1], sys.argv[2], [(g, tuple(p)) for g, p in a])
