"""v3.30 head-range redesign (roll-bearing holder + collar fixing), cutter / adder solids for Blender (run in this folder).
Frames: head parts in the MODEL frame (= Blender head_v330.blend frame; link frame = model + (-2.1, 0, -66));
head_yaw_to_roll in its PRINT frame (= link + (4.125, -0.1, -105.751), same as v39_head_yaw_to_roll.stl).
Roll axis (link): y 0.1, z 127.85, along x.  Collar-ring axis (link): x 9.7, y 0.
 head_lower : - old bearing holder (inclined strut + housing + lower hanger)     cut_holder.stl
              - 4 collar screw tabs (phi +-50 / +-130)                            cut_tabs.stl
              - back-bottom shell band below z 118 for |phi| > 100 deg (ramp 95-105; hidden from the front)   cut_backrim.stl
              + new bearing housing 7 mm deck-hung web (bottom window below axis-12.5, 282 deg wrap), bearing 12.1 mm further forward (same 20x32x7 bearing, same axis)  add_housing.stl
              + rear ballast ledge (|phi| >= 150, z 130.5-133 link, 7 mm deep) for 25 g of steel (M8 nuts / wheel weights)  add_ballast_ledge.stl (ballast_25g.stl = link-frame ballast volume for the sims)
              + 4 internal collar bosses (phi +-28 / +-52, z 113.1-124) with vertical M3 x 5 x 4 heat-set insert holes  add_bosses.stl / cut_insert_holes.stl
 chin collars: keep the front band |phi| <= 64 only (cut_collar_L/R.stl) + 2 inward screw ledges each (add_ledges_L/R.stl, M3 clearance holes)
 head_yaw_to_roll: - everything behind x -12 (old tower, hub, rear ring sector)     cut_neck_rear.stl
                   + tower 6 mm (x -29..-23), hub d19.8 (x -37.4..-28.5), cross-bar + 2 side arms to the ring sides   add_neck_rear.stl
"""
import json, numpy as np, trimesh
from trimesh.creation import box, cylinder
M2L = np.array([-2.1, 0.0, -66.0]); L2P = np.array([4.125, -0.1, -105.751])
AX = np.array([0.0, 0.1, 127.85]); RC = np.array([9.7, 0.0]); BALL_C = np.array([9.678, -0.006, 169.122]); RB = 104.795
def B(lo, hi): return box(bounds=[lo, hi])
def U(*m): return trimesh.boolean.union([x for x in m], engine="manifold")
def D(a, *b): return trimesh.boolean.difference([a] + list(b), engine="manifold")
def I(a, b): return trimesh.boolean.intersection([a, b], engine="manifold")
def cylx(r, x0, x1, n=128):
    c = cylinder(radius=r, height=x1 - x0, sections=n); c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation([(x0 + x1) / 2, AX[1], AX[2]]); return c
def cylz(r, cx, cy, z0, z1, n=64):
    c = cylinder(radius=r, height=z1 - z0, sections=n); c.apply_translation([cx, cy, (z0 + z1) / 2]); return c
def sector(a0, a1, r0, r1, z0, z1, ztop=None, step=0.5):
    """solid sector about the collar-ring axis, phi a0..a1 deg, rr r0..r1, z z0..z1 (or z0..ztop(phi))"""
    A = np.arange(a0, a1 + 1e-9, step); A[-1] = a1; V = []
    for a in A:
        t = np.radians(a); c, s = np.cos(t), np.sin(t); zt = z1 if ztop is None else ztop(a)
        for r, z in ((r0, z0), (r1, z0), (r1, zt), (r0, zt)): V.append((RC[0] + r * c, RC[1] + r * s, z))
    V = np.array(V); F = []; n = len(A)
    for i in range(n - 1):
        for k in range(4):
            p, q = 4 * i + k, 4 * i + (k + 1) % 4; r_, s_ = 4 * (i + 1) + (k + 1) % 4, 4 * (i + 1) + k
            F += [(p, q, r_), (p, r_, s_)]
    F += [(0, 2, 1), (0, 3, 2)]; e = 4 * (n - 1); F += [(e, e + 1, e + 2), (e, e + 2, e + 3)]
    m = trimesh.Trimesh(V, F, process=True); m.fix_normals(); assert m.is_volume; return m
P = dict(BX0=-37.1, BW=7.0, BR=16.0, BRI=10.0, HW=1.8, LIP=1.6, LIPR=13.0, WEB_Y=10.0, DECK_Z=159.0,
         TOW_X1=-23.0, TOW_W=6.0, TOW_Y=13.5, TOW_Z0=112.5, HUB_R=9.9, ARM_Y0=28.5, ARM_Y1=38.0, ARM_Z1=124.0, RING_CUT_X=-12.0,
         Z_RIM=113.118, BOSS_PHI=(28.0, 52.0), BOSS_HW=4.5, BOSS_R0=76.5, BOSS_Z1=124.0, INS_R=2.0, INS_D=6.5, INS_RR=81.0,
         LEDGE_T=2.5, LEDGE_R0=77.0, LEDGE_R1=87.0, CLR_R=1.7, COLLAR_PHI=64.0, TAB_PHI=(50.0, 130.0), TAB_HW=11.0, TAB_RR=84.8,
         BACK_Z=118.0, BACK_A0=95.0, BACK_A1=105.0, SLOT_H=12.5, BAL_PHI=150.0, BAL_Z0=133.0, BAL_Z1=148.0, BAL_T=6.5, LEDGE_H=2.5, LEDGE_D=7.0, WALL_IN=2.6)
def link_ball(dr):     # head ball (link frame) shrunk by dr
    s = trimesh.creation.icosphere(subdivisions=6, radius=RB - dr); s.apply_translation(BALL_C + M2L); return s
def build(p=P):
    out = {}
    # ---------------- head_lower cutters
    h = B([-78, -26, 95], [-36.3, 26, 147.5]); out["cut_holder"] = I(h, cylz(84.5, RC[0], RC[1], 90, 150, 256))
    tabs = []
    for pt in p["TAB_PHI"]:
        for sg in (1, -1):
            tabs.append(sector(sg * pt - p["TAB_HW"], sg * pt + p["TAB_HW"], 55.0, p["TAB_RR"], 95.0, 124.5))
            tabs.append(sector(sg * pt - p["TAB_HW"], sg * pt + p["TAB_HW"], p["TAB_RR"] - 1.0, 92.0, 95.0, p["Z_RIM"] + 0.012))   # tab skin hugging the collar, below the shell rim
    out["cut_tabs"] = U(*tabs)
    def zb(a):
        a = abs(a); u = np.clip((a - p["BACK_A0"]) / (p["BACK_A1"] - p["BACK_A0"]), 0, 1); return 111.0 + (p["BACK_Z"] - 111.0) * 0.5 * (1 - np.cos(np.pi * u))
    out["cut_backrim"] = U(sector(90.0, 180.0, 40.0, 100.0, 90.0, None, ztop=zb), sector(-180.0, -90.0, 40.0, 100.0, 90.0, None, ztop=zb))
    # ---------------- head_lower adders
    x0, x1 = p["BX0"], p["BX0"] + p["BW"]; ro = p["BR"] + p["HW"]
    ring = D(cylx(ro, x0 - 0.5, x1), cylx(p["BR"], x0, x1 + 1))
    ring = D(ring, B([x0 - 0.6, -30, 90], [x1 + 0.1, 30, AX[2] - p["SLOT_H"]]), cylx(p["LIPR"], x0 - 1, x0 + 1))   # bottom window + no rear membrane (hub / inner race free)   # bottom window (bearing outer ring shows, 282 deg wrap): +2 deg back pitch
    lip = D(cylx(ro, x0 - p["LIP"], x0 - 0.5 + 0.01), cylx(p["LIPR"], x0 - p["LIP"] - 1, x0 + 1), B([x0 - 5, -30, 90], [x0 + 1, 30, AX[2] - 8.0]))
    web = D(B([x0 - 0.5, -p["WEB_Y"], AX[2]], [x1, p["WEB_Y"], p["DECK_Z"]]), cylx(p["BR"], x0, x1 + 1))
    hs = D(U(ring, lip, web), cylx(p["LIPR"], x0 - 2.0, x0 + 0.5)); hs.merge_vertices()   # r13 clear behind the bearing (no web slab / membrane over the hub)
    out["add_housing"] = max(hs.split(only_watertight=False), key=lambda b: abs(b.volume))   # drop zero-volume web/bore slivers
    # rear ballast ledge (printed) + ballast volume (25 g steel, sim / check only): restores the head-pitch hold margin lost by moving mass forward
    def band(z0, z1):
        return sector(p["BAL_PHI"], 360.0 - p["BAL_PHI"], 50.0, 110.0, z0, z1)        # one sector across the back (phi 150..210)
    out["add_ballast_ledge"] = D(I(band(p["BAL_Z0"] - p["LEDGE_H"], p["BAL_Z0"]), link_ball(1.2)), link_ball(p["WALL_IN"] + p["LEDGE_D"]))
    out["ballast_25g"] = D(I(band(p["BAL_Z0"] + 0.05, p["BAL_Z1"]), link_ball(p["WALL_IN"] + 0.05)), link_ball(p["WALL_IN"] + p["BAL_T"]))
    inner = link_ball(1.2); bos, holes = [], []
    for pb in p["BOSS_PHI"]:
        for sg in (1, -1):
            a = sg * pb; bos.append(I(sector(a - p["BOSS_HW"], a + p["BOSS_HW"], p["BOSS_R0"], 92.0, p["Z_RIM"], p["BOSS_Z1"]), inner))
            t = np.radians(a); holes.append(cylz(p["INS_R"], RC[0] + p["INS_RR"] * np.cos(t), p["INS_RR"] * np.sin(t), p["Z_RIM"] - 1.0, p["Z_RIM"] + p["INS_D"], 48))
    out["add_bosses"] = U(*bos); out["cut_insert_holes"] = U(*holes)
    # ---------------- collars
    for sd, sg in (("L", 1), ("R", -1)):
        lo_, hi_ = (p["COLLAR_PHI"], 180.0) if sg > 0 else (-180.0, -p["COLLAR_PHI"])
        out[f"cut_collar_{sd}"] = sector(lo_, hi_, 40.0, 100.0, 90.0, 120.0)
        led, hol = [], []
        for pb in p["BOSS_PHI"]:
            a = sg * pb; led.append(I(sector(a - p["BOSS_HW"], a + p["BOSS_HW"], p["LEDGE_R0"], p["LEDGE_R1"], p["Z_RIM"] - p["LEDGE_T"], p["Z_RIM"]), link_ball(0.6)))
            t = np.radians(a); hol.append(cylz(p["CLR_R"], RC[0] + p["INS_RR"] * np.cos(t), p["INS_RR"] * np.sin(t), p["Z_RIM"] - 5, p["Z_RIM"] + 1, 48))
        lg = D(U(*led), *hol)
        out[f"add_ledges_{sd}"] = lg
    # ---------------- neck (link frame here, converted to print frame on export)
    out["cut_neck_rear"] = B([-80, -60, 90], [p["RING_CUT_X"], 60, 160])
    t1 = p["TOW_X1"]; t0 = t1 - p["TOW_W"]
    tower = U(B([t0, -p["TOW_Y"], p["TOW_Z0"]], [t1, p["TOW_Y"], AX[2]]), cylx(p["TOW_Y"], t0, t1))
    hub = cylx(p["HUB_R"], p["BX0"] - 0.3, t0 + 0.5)
    bar = B([t0, -p["ARM_Y1"], p["TOW_Z0"]], [t1, p["ARM_Y1"], p["ARM_Z1"]])
    arms = [B([t0, p["ARM_Y0"], p["TOW_Z0"]], [p["RING_CUT_X"] + 2.0, p["ARM_Y1"], p["ARM_Z1"]]), B([t0, -p["ARM_Y1"], p["TOW_Z0"]], [p["RING_CUT_X"] + 2.0, -p["ARM_Y0"], p["ARM_Z1"]])]
    drops = [B([-15.0, p["ARM_Y0"], 105.751], [p["RING_CUT_X"] + 2.0, p["ARM_Y1"], p["ARM_Z1"]]), B([-15.0, -p["ARM_Y1"], 105.751], [p["RING_CUT_X"] + 2.0, -p["ARM_Y0"], p["ARM_Z1"]])]
    out["add_neck_rear"] = U(tower, hub, bar, *arms, *drops)
    out["bearing_new"] = D(cylx(p["BR"], x0, x1), cylx(p["BRI"], x0 - 1, x1 + 1))
    return out
if __name__ == "__main__":
    out = build(); info = dict(params=P, frames=dict(model_to_link=M2L.tolist(), link_to_neck_print=L2P.tolist()))
    for k, m in out.items():
        assert m.is_volume, k
        m.export(f"link_{k}.stl")                        # link frame copy (checks)
        e = m.copy()
        if "neck" in k: e.apply_translation(L2P)
        elif k not in ("bearing_new", "ballast_25g"): e.apply_translation(-M2L)
        e.export(f"{k}.stl"); info[k] = dict(vol_cm3=round(m.volume / 1000, 3), bounds_link=m.bounds.round(2).tolist(), faces=len(m.faces))
    json.dump(info, open("redesign_parts.json", "w"), indent=1); print(json.dumps({k: v["vol_cm3"] for k, v in info.items() if isinstance(v, dict) and "vol_cm3" in v}))
