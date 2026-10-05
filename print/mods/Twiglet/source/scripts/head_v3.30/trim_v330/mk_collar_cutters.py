"""v3.30 collar side-hem relief cutters (model frame = Blender frame; link frame = model + (-2.1, 0, -66)).
Hem height h(phi) about the collar-ring axis (x=11.8, y=0 model): untouched to |phi| 64 deg (front + front tab at 50 deg), cosine ramp to
link z 109.0 (model 175.0) by 70 deg, flat to 118 deg, ramp back down to untouched by 122.5 deg (the rear tab at 130 +-6.5 deg and its screw
hole are not touched). Removes the collar band below the hem: the collar keeps a continuous 4.1 mm band (z 109.0-113.1 link) -> one body."""
import numpy as np, trimesh, json, sys
CX, CY, DZ = 11.8, 0.0, 66.0
ZC, ZOFF, A0, A1, A2, A3 = 109.0, 99.0, 64.0, 70.0, 118.0, 122.5
def h(a):
    a = np.abs(a); out = np.full_like(a, ZOFF)
    u = np.clip((a - A0) / (A1 - A0), 0, 1); out = np.where((a >= A0) & (a < A1), ZOFF + (ZC - ZOFF) * 0.5 * (1 - np.cos(np.pi * u)), out)
    out = np.where((a >= A1) & (a <= A2), ZC, out)
    v = np.clip((a - A2) / (A3 - A2), 0, 1); out = np.where((a > A2) & (a < A3), ZC - (ZC - ZOFF) * 0.5 * (1 - np.cos(np.pi * v)), out)
    return out
def cutter(sign, r0=60.0, r1=100.0, zb=89.0, a_lo=62.0, a_hi=124.5, step=0.25):
    A = np.arange(a_lo, a_hi + 1e-9, step); n = len(A); V = []
    for a in A:
        t = np.radians(sign * a); c, s = np.cos(t), np.sin(t); zt = float(h(np.array([a]))[0])
        for r, z in ((r0, zb), (r1, zb), (r1, zt), (r0, zt)): V.append((CX + r * c, CY + r * s, z + DZ))
    V = np.array(V); F = []
    for i in range(n - 1):
        for k in range(4):
            a, b = 4 * i + k, 4 * i + (k + 1) % 4; c_, d = 4 * (i + 1) + (k + 1) % 4, 4 * (i + 1) + k
            F += [(a, b, c_), (a, c_, d)]
    F += [(0, 2, 1), (0, 3, 2)]; e = 4 * (n - 1); F += [(e, e + 1, e + 2), (e, e + 2, e + 3)]
    m = trimesh.Trimesh(V, F, process=True); m.fix_normals(); assert m.is_volume, "cutter not a volume"
    return m
info = {}
for sd, sg in (("L", 1), ("R", -1)):
    m = cutter(sg); m.export(f"collar_cutter_{sd}.stl"); info[sd] = dict(volume_cm3=round(m.volume / 1000, 2), faces=len(m.faces))
info["hem"] = dict(axis_model_xy=[CX, CY], z_hem_link=ZC, z_hem_model=ZC + DZ, ramps_deg=[A0, A1, A2, A3])
json.dump(info, open("collar_cutters.json", "w"), indent=1); print(json.dumps(info))
