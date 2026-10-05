HV.FLARE.update(SIDE=12.0); HV.ARM_CUT.update(RAMP=8.0, TH=93.0)
# v3.35 t2: extra side flare at eye level (photo hair stands off wider at z 0..+50) that fades out again below th 100 (no wider low cone -> arms)
import numpy as _np
_SEAT0 = getattr(HV, "_SEAT0", HV.seat_r); HV._SEAT0 = _SEAT0
EXF = dict(A=14.0, T0=50.0, T1=85.0, T2=100.0, T3=125.0)
def _ss(u): u = _np.clip(u, 0, 1); return u * u * (3 - 2 * u)
def _seat_r2(env, D_):
    r = _SEAT0(env, D_); th = _np.degrees(_np.arccos(_np.clip(D_[:, 2], -1, 1))); sw = D_[:, 1] ** 2 / _np.maximum(D_[:, 0] ** 2 + D_[:, 1] ** 2, 1e-9)
    return r + EXF["A"] * sw * _ss((th - EXF["T0"]) / (EXF["T1"] - EXF["T0"])) * (1 - _ss((th - EXF["T2"]) / (EXF["T3"] - EXF["T2"])))
HV.seat_r = _seat_r2

# t15: no feather edges anywhere: every lock vertex < MINP above the seat dives under it (fuse MINP rule, normally only in the relief bands, enabled everywhere with a 5 % min trim weight)
HV.BLEND.update(MINP=1.6, EXTRA=lambda uv: _np.full(len(uv), 0.0502))

HV.TRUNK_CUT.update(TH=112.0)   # u1: side-back tips hang lower behind the arm sweep (current-body free map: clear to th ~114)
# v3.43 b3: free map (.cache/free_map.npz, arms inside soft limits + head range): at |ph| 66-100 the obstacles start ~10-20 mm outside the seat only below
#     th ~102 -> the side-curtain relief starts at th 100 instead of 93 (curtains hang ~15 mm longer to the cheek like the photo); arm check decides
HV.ARM_CUT.update(TH=100.0)
# v3.44 c14: crown-top opening REMOVED (Mike: closed crown shell as in c0 / v3.43)
# v3.44 c12: hidden under the fabric hat AND near/in front of the pitch axis (not the far-back counterweight): lock relief squashed 60 % (same smooth radial
#     squash as the arm relief, no cut faces); a < 40 deg from the hat axis (ramp to 0 at 46; hat edge 50), weight fades out behind x ~ -35 mm
_HATSQ = dict(K=0.6, A0=40.0, A1=46.0, UX0=-0.55, UX1=-0.35)
def _hat_extra(uv):
    a = HV.hat_angle(uv); q = _np.clip((_HATSQ["A1"] - a) / (_HATSQ["A1"] - _HATSQ["A0"]), 0, 1); qx = _np.clip((uv[:, 0] - _HATSQ["UX0"]) / (_HATSQ["UX1"] - _HATSQ["UX0"]), 0, 1)
    return _np.maximum(0.0502, _HATSQ["K"] * q * q * (3 - 2 * q) * qx * qx * (3 - 2 * qx))
HV.BLEND.update(EXTRA=_hat_extra)
# c13: c12's squash thinned the lock roots to ~1.3 mm where they meet the crown outline (th ~34, ph +-130) -> squash only above th 24 (ramp to 0 at 28)
def _hat_extra(uv, _f=_hat_extra):
    th = _np.degrees(_np.arccos(_np.clip(uv[:, 2], -1, 1))); qt = _np.clip((28.0 - th) / 4.0, 0, 1)
    return _np.maximum(0.0502, (_f(uv) - 0.0502).clip(0) * qt * qt * (3 - 2 * qt) + 0.0502 * 0)
HV.BLEND.update(EXTRA=_hat_extra)
# c14b: hidden crown top under the fabric hat (th < 14, in front of / on the pitch axis; lock roots start at th 16, pin bosses at th >= 13.5 only rise at the
#     front-left pin): the closed crown shell 7.5 -> 3.0 mm thick there - outer surface eased down by up to 4.5 mm (smooth dish, ramp th 10-15), inner seat untouched
import inspect as _insp2
CDIP = dict(D=4.5, T0=10.0, T1=15.0)
_src2 = _insp2.getsource(HV.wig_blend)
_src2 = _src2.replace("    outer = trimesh.Trimesh(env.C + D_ * (rs + g - 0.45)[:, None], ico.faces, process=False)\n",
    "    _u2 = np.clip((CDIP['T1'] - thv) / (CDIP['T1'] - CDIP['T0']), 0, 1); g = np.maximum(g - CDIP['D'] * _u2 * _u2 * (3 - 2 * _u2), np.minimum(g, 3.45))\n"
    "    outer = trimesh.Trimesh(env.C + D_ * (rs + g - 0.45)[:, None], ico.faces, process=False)\n")
assert "CDIP" in _src2
HV.CDIP = CDIP; exec(_src2, HV.__dict__)
