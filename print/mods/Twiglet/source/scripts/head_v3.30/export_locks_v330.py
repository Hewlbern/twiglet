"""v3.30: export the v3.29 lock layout (hair_v330 defaults = v3.29 W13 tuning) as explicit 3-D lock spines for Blender:
per lock n samples of  base point on the seat B (mm, model frame), outward normal N, lateral L, full width W (mm), crest height H (mm above the seat).
-> blender/locks_v330.json  (the source of truth for blender/build_wig_v330.py; edit it or the curves in wig_v330.blend)"""
import os, sys, json, math, pickle, numpy as np
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path[:0] = [HERE, os.path.dirname(HERE)]; os.chdir(HERE)
import hair_v330 as HV
NAMES = ["F1 central fringe", "F2 fringe L", "F3 fringe R", "F4 front-side L", "F5 front-side R", "S1 L", "S1 R", "S23 L", "S23 R", "B1 L", "B1 R",
         "B2 L", "B2 R", "SB sideburn L", "SB sideburn R", "temple layer L", "temple layer R", "cheek L", "cheek R", "temple flick R", "temple flick L"]
def spine(i, L, n=48):
    phi0, th0, th1, W, Tm, curl, off, tc = L[:8]; sw, tw = (L[8], L[9]) if len(L) > 8 else (0.0, 0.0)
    t = np.linspace(0, 1, n); FA, FL, SO, CP, ST = HV.FACET, HV.FLOW, HV.SOFT, HV.CAP, HV.STYLE.get(i, {})
    lin = FA["SWEEP_LIN"] if 40 <= abs(phi0) <= 135 else 0.0
    sw = FL["SW"] * (abs(sw) * (1 if phi0 >= 0 else -1) if FL["SW_SIGN"] and 3 < abs(phi0) <= 135 else sw)
    sg = 1.0 if curl > 0 else -1.0 if curl < 0 else 0.0
    ph = phi0 + curl * (lin * t + (1 - lin) * t * t * (3 - 2 * t)) + sw * np.sin(2 * math.pi * t) * (1 - 0.3 * t) + sg * FL["TIPC"] * t ** 3
    bow = FL["TH_BOW"] * (1.0 if 40 <= abs(phi0) <= 135 else FL["BOW_B"] if abs(phi0) > 135 else FL["BOW_F"])
    th = th0 + (th1 - th0) * (t + bow * t * (1 - t)); P = HV.dirs_of(th, ph)
    Wk = SO["GAPW"] * W * (FA["WK_F"] if abs(phi0) < 40 else FA["WK_F45"] if abs(phi0) < 60 else FA["WK_S"] if abs(phi0) < 135 else FA["WK_B"])
    tv = np.clip((FA["BASE_TH"] - th0) / max(th1 - th0, 1.0), 0, 0.6)
    wend = max(ST.get("WEND", CP["WEND"]) * Wk, CP.get("WMIN", 0.0)); llen = np.linalg.norm(np.diff(P, axis=0), axis=1).sum() * HV.RREF
    Lk = float(np.clip(ST.get("LR", CP.get("LR", 1e9)) * 0.5 * wend / llen, 0.03, ST.get("L", CP["L"]))); te = 1 - Lk
    capf = np.sqrt(np.clip(1 - (np.clip(t - te, 0, None) / Lk) ** 2, 0, 1))
    w = (np.maximum(Wk * np.clip((1 - t) / (1 - tv), 0, 1) ** ST.get("TAPER", FA["TAPER_EXP"]), wend) + 0.6) * capf
    te_ = ST.get("TIP_EXP", SO["TIP_EXP_F"] if 15 < abs(phi0) < 40 else FA["TIP_EXP"])
    f = np.where(t < tc, 0.55 + 0.45 * np.sin(0.5 * math.pi * t / tc), ((1 - t) / (1 - tc)) ** te_)
    f = np.maximum(f, CP["HEND"] * (t >= tc)) * capf ** 0.5
    k0, k1 = (FA["K_TH0"], FA["K_TH1"]) if abs(phi0) < 40 else (FA["K_TH0_S"], FA["K_TH1_S"]); qk = np.clip((th - k0) / (k1 - k0), 0, 1)
    ck = FA["CREST_K"] if abs(phi0) < 40 else FA["CREST_K_S"] if abs(phi0) < 135 else FA["CREST_K_B"]; kup = 1.0 if abs(phi0) < 40 else FA["K_UP_S"]
    H = (kup + (ck - kup) * qk * qk * (3 - 2 * qk)) * Tm * f
    return t, th, ph, P, w, H, off
if __name__ == "__main__":
    R = pickle.load(open(".cache/head_v329.pkl", "rb")); meta = R["_meta"]; C = np.array(meta["ball_C"]); Rb = meta["ball_R"]
    cones = []
    for sd in "LR":
        c0 = R[f"eye_bezel_{sd}"].bounds.mean(0); ax = (c0 - C) / np.linalg.norm(c0 - C); cones.append((ax, 29.0, 105.8))
    env = HV.Envelope(C, [R["head_upper"], R["head_lower"], R["eye_bezel_L"], R["eye_bezel_R"]], cones, r_min=Rb - 0.5, cache=".cache/env_v314.npz"); del R
    out = dict(C=C.tolist(), note="units mm, model frame (x forward, y robot's left, z up); B = spine point on the wig seat, N outward, L lateral (robot-left-hand side), W full width, H crest height above the seat", locks=[])
    for i, L in enumerate(HV.LOCKS):
        t, th, ph, P, w, H, off = spine(i, L); rs = HV.seat_r(env, P); B = C + P * rs[:, None]
        T = np.gradient(B, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = P - (P * T).sum(1)[:, None] * T; N /= np.linalg.norm(N, axis=1)[:, None]; Lt = np.cross(N, T)
        out["locks"].append(dict(i=i, name=NAMES[i] if i < len(NAMES) else f"lock {i}", params=list(L), style=HV.STYLE.get(i, {}), off=off,
                                 th=np.round(th, 3).tolist(), ph=np.round(ph, 3).tolist(), B=np.round(B, 3).tolist(), N=np.round(N, 5).tolist(), L=np.round(Lt, 5).tolist(),
                                 W=np.round(w, 3).tolist(), H=np.round(H, 3).tolist()))
        print(i, out["locks"][-1]["name"], "len %.0f mm" % np.linalg.norm(np.diff(B, axis=0), axis=1).sum(), "W0 %.1f Wmax %.1f Wend %.1f Hmax %.1f" % (w[0], w.max(), w[-2], H.max()))
    json.dump(out, open("blender/locks_v330.json", "w")); print("ok")
