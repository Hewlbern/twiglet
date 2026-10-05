# r1 ribbon first pass: per-lock twist (deg, root -> tip; L side +, R side mirrored -), fold crease, blade thickness
import numpy as np
TW = {"L00": (0, 0, 22), "L01": (0, 10, 18), "L02": (0, 10, 18), "L15": (0, 12, 16), "L16": (0, 12, 16),
      "L03": (0, 28, 12), "L04": (0, 28, 12), "L05": (5, 40, 10), "L06": (5, 40, 10), "L07": (0, -30, 10), "L08": (0, -30, 10),
      "L09": (0, 22, 10), "L10": (0, 22, 10), "L11": (0, -18, 10), "L12": (0, -18, 10), "L13": (0, 15, 8), "L14": (0, 15, 8),
      "L17": (0, 30, 10), "L18": (0, 30, 10), "L19": (0, 35, 8), "L20": (0, 35, 8)}
for s in SP:
    k = s["name"][:3]; d = s["co"][0] - C; sg = 1.0 if np.arctan2(d[1], d[0]) >= 0 else -1.0
    if k == "L00": sg = 1.0
    tw0, tw1, cr = TW.get(k, (0, 20, 10)); s["tw0"], s["tw1"], s["crease"] = sg * tw0, sg * tw1, cr
# r4: unseen back (B1/B2) and back-sides (S23) low + flat + narrower -> mass
LOW = {"L09": dict(liftk=0.5, tw=0.0, r=0.85), "L10": dict(liftk=0.5, tw=0.0, r=0.85), "L11": dict(liftk=0.5, tw=0.0, r=0.85), "L12": dict(liftk=0.5, tw=0.0, r=0.85),
       "L07": dict(liftk=0.5, tw=-8.0, r=0.85), "L08": dict(liftk=0.5, tw=-8.0, r=0.85)}
for s in SP:
    e = LOW.get(s["name"][:3])
    if e:
        d = s["co"][0] - C; sg = 1.0 if np.arctan2(d[1], d[0]) >= 0 else -1.0
        s["liftk"] = e["liftk"]; s["tw1"] = sg * e["tw"]; s["r"] = s["r"] * e["r"]
# s16: s13 with the side-lock steps sunk 0.7 mm on the L side only | s13: s7 with blunter base-lock points (pte 8 -> silhouette) + sharper overlay points (pte 4) + overlays on the temple flicks too | s7: keep the r11 silhouette (full-width base locks) and ADD narrower overlay locks stepped 1.6-2.0 mm proud on top (solid step = shadow line),
#     overlays end in their own points before the base tip -> reads as separate narrower locks; fringe triangle kept + 2 overlay points fanning over it
def OVL(sg, l2=1.8, len2=0.88, c=0.38, w=0.48): return [dict(c=0.0, w=1.0, len=1.0, tw=1.0, lift=0.0, pte=8.0), dict(c=c * sg, w=w, len=len2, tw=1.0, lift=l2, pt=1, pte=4.0)]
SUBA = {"L01": (), "L02": (), "L03": (), "L04": (), "L05": (1.8,), "L06": (1.8,), "L15": (1.6, 0.85), "L16": (1.6, 0.85), "L17": (1.6,), "L18": (1.6,), "L19": (1.5, 0.85), "L20": (1.5, 0.85)}
FAN3 = [dict(c=0.0, w=1.0, len=1.0, tw=1.0, lift=0.0, pte=8.0), dict(c=-0.42, w=0.36, len=0.8, tw=1.0, lift=1.6, fan=-0.15, pt=1), dict(c=0.42, w=0.36, len=0.74, tw=1.0, lift=1.6, fan=0.15, pt=1)]
LIFT = {"L01": 1.0, "L02": 1.0, "L15": 0.5, "L16": 0.5}
PTL = ("L01", "L02", "L03", "L04", "L05", "L06", "L13", "L14", "L15", "L16", "L17", "L18", "L19", "L20")
for s in SP:
    k = s["name"][:3]; d = s["co"][0] - C; sg = 1.0 if np.arctan2(d[1], d[0]) >= 0 else -1.0
    if k in SUBA: s["subs"] = OVL(sg, *SUBA[k])
    if k == "L00": s["subs"] = FAN3
    s["lift"] = LIFT.get(k, 0.0); s["pt"] = 1 if k in PTL else 0
    if k in ("L09", "L10", "L11", "L12"): s["liftk"] = 0.62
for s in SP:
    k = s["name"][:3]
    if k in ("L03", "L05", "L15", "L17", "L19") and s.get("subs"):
        s["subs"] = [dict(sb, lift=sb.get("lift", 0.0) - 0.7) for sb in s["subs"]]

# t8: + hidden back locks narrower (r x0.85 more)
for s in SP:
    if s["name"][:3] in ("L07", "L08", "L09", "L10", "L11", "L12"): s["r"] = s["r"] * 0.85

# t12: sharper lock definition: overlay sub-locks stepped +0.6 mm more (deeper shadow lines), overlay points sharper (pte 4 -> 3)
for s in SP:
    if s.get("subs") and len(s["subs"]) > 1:
        s["subs"] = [s["subs"][0]] + [dict(sb, lift=sb.get("lift", 0.0) + 0.6, pte=3.0) for sb in s["subs"][1:]]

# v1 (v3.37): photo locks are flat blades tapering to clear points with V gaps between tips -> base sub-locks of the fringe/front/side locks pointed from ~half length
TAPER = ("L00", "L01", "L02", "L03", "L04", "L05", "L06", "L13", "L14", "L15", "L16", "L19", "L20")
for s in SP:
    if s["name"][:3] in TAPER:
        s["pt"] = 1; s["pte"] = 2.5
        if s.get("subs"): s["subs"] = [dict(s["subs"][0], pt=1, pte=2.5)] + s["subs"][1:]

# v2: fringe / front-side locks split into 2 pointed flat blades each (photo: ~6 separate blades across the forehead with V gaps between tips),
#     the 2nd blade stepped 1.6 mm proud (overlaps = lock crossing over another) and fanned outward-down; old overlay removed (replaced by the 2nd blade)
SPLIT = {"L01": 1.0, "L02": 1.0, "L03": 0.9, "L04": 0.9}
for s in SP:
    k = s["name"][:3]
    if k in SPLIT:
        d = s["co"][0] - C; sg = 1.0 if np.arctan2(d[1], d[0]) >= 0 else -1.0
        lb = s["subs"][0].get("lift", 0.0)
        s["subs"] = [dict(c=-0.42 * sg, w=0.62, len=1.0, tw=1.0, lift=lb, pt=1, pte=2.5, fan=-0.10 * sg),
                     dict(c=0.42 * sg, w=0.62, len=0.88 * SPLIT[k], tw=1.0, lift=lb + 1.6, pt=1, pte=2.5, fan=0.18 * sg)]

# v3: new eye blades: flat, pointed from half length, stepped on top of F2/F3 (crossing)
for s in SP:
    k = s["name"][:3]
    if k in ("L21", "L22"):
        sg = 1.0 if k == "L21" else -1.0
        s["tw0"], s["tw1"], s["crease"] = 0.0, sg * 14.0, 16
        s["pt"] = 1; s["pte"] = 2.5; s["lift"] = 2.4
# w2: new temple out-flick: flat pointed blade, tip lifted off the head (builder 'flick'), on top of F5/S1
for s in SP:
    if s["name"][:3] == "L23":
        s["tw0"], s["tw1"], s["crease"] = 0.0, -20.0, 14; s["pt"] = 1; s["pte"] = 2.5; s["lift"] = 1.0; s["flick"] = 14.0
for s in SP:
    if s["name"][:3] == "L23": s["flick"] = 24.0; s["lift"] = 2.0
for s in SP:
    if s["name"][:3] == "L23": s["flick"] = 32.0

# w9 (v3.38): photo 3/4 + front: the fringe is a few BIG smooth flat blades; u5/v6 central lock carries 2 small overlay points (busy) -> L00 = one broad pointed blade
for s in SP:
    if s["name"][:3] == "L00": s["subs"] = [dict(s["subs"][0])]

# v3.39 x1: photo fringe = fewer, broader, smooth pointed blades -> no raised overlay strips anywhere on the front/side locks, F2/F3 back to ONE broad pointed blade each
for s in SP:
    k = s["name"][:3]
    if k in ("L05", "L06", "L15", "L16", "L19", "L20") and s.get("subs") and len(s["subs"]) > 1:
        s["subs"] = [dict(s["subs"][0], pt=1, pte=2.5)]
    if k in ("L01", "L02"):
        lb = s["subs"][0].get("lift", 0.0)
        s["subs"] = [dict(c=0.0, w=1.0, len=1.0, tw=1.0, lift=lb, pt=1, pte=2.5)]
# x2: photo locks are chunky felt with soft rounded (pillow) sections -> thicker blades with a rounder lens section (centre 4.4 mm, edges ~2 mm)
VIS = ("L00", "L01", "L02", "L03", "L04", "L05", "L06", "L13", "L14", "L15", "L16", "L19", "L20", "L21", "L22", "L23", "L24")
for s in SP:
    if s["name"][:3] in VIS: s["tk"] = 4.4; s["lens"] = 0.45
# x3: rounder pillow sections (bulge ~ 20-25 % of the half-width like the photo's felt locks)
for s in SP:
    if s["name"][:3] in VIS: s["tk"] = 7.0; s["lens"] = 0.28
# x4: L24 = mirror of L23 (flat->pillow pointed blade, tip lifted 32 mm off the head); hidden L19/L20 (under S1) back to thin blades (mass)
for s in SP:
    k = s["name"][:3]
    if k == "L24": s["tw0"], s["tw1"], s["crease"] = 0.0, 20.0, 14; s["pt"] = 1; s["pte"] = 2.5; s["lift"] = 2.0; s["flick"] = 32.0
    if k in ("L19", "L20"): s.pop("tk", None); s.pop("lens", None)
# x5: pitch headroom: pillow sections a little thinner (tk 7 -> 6, lens .28 -> .32; edges ~1.9 mm)
for s in SP:
    if s.get("tk") == 7.0: s["tk"] = 6.0; s["lens"] = 0.32
# v3.42 a5: eye blades sat only ~1.4 mm above F2/F3 -> their edges graze the F2/F3 surface at a shallow angle = crinkled slit seam; clear felt-layer overlap instead (lift 2.4 -> 4.5)
for s in SP:
    if s["name"][:3] in ("L21", "L22"): s["lift"] = 4.5
# v3.42 a6: front locks = long straight-sided TAPERS (photo: each fringe lock narrows steadily from a broad root to a clean point) -> the lower edge becomes
#     a zig-zag of separate points with wood V's between them (eye blades | F2/F3 | F4/F5), roots stay full width and blended; no cutting
for s in SP:
    k = s["name"][:3]
    if k in ("L01", "L02", "L21", "L22"):
        s["ptp"] = 1.0; s["pte"] = 1.6
        if s.get("subs"): s["subs"] = [dict(sb, ptp=1.0, pte=1.6) for sb in s["subs"]]
    if k in ("L00", "L03", "L04"):
        s["ptp"] = 0.8; s["pte"] = 2.0
        if s.get("subs"): s["subs"] = [dict(sb, ptp=0.8, pte=2.0) for sb in s["subs"]]
# a7: new steeper F2/F3 (L25/L26): pillow section, long straight taper to a clean point, a little lift (sits over F4/F5, under the eye blades)
for s in SP:
    k = s["name"][:3]
    if k in ("L25", "L26"):
        sg = 1.0 if k == "L25" else -1.0
        s["tw0"], s["tw1"], s["crease"] = 0.0, sg * 12.0, 12; s["pt"] = 1; s["pte"] = 1.6; s["ptp"] = 1.0; s["lift"] = 1.5; s["tk"] = 6.0; s["lens"] = 0.32
    if k in ("L21", "L22"): s["lift"] = 3.0
# a10: side curtains read as thin edge-on strands (twisted up to 40 deg at the tips) -> face the viewer as broad felt locks (twist / 2.5), flicks tapered straight
for s in SP:
    k = s["name"][:3]
    if k in ("L05", "L06", "L13", "L14", "L19", "L20", "L03", "L04"):
        s["tw1"] = s["tw1"] / 2.5
    if k in ("L23", "L24"): s["ptp"] = 1.0; s["pte"] = 1.6
# a11: F2n/F3n edges grazed F4/F5 at a shallow angle (lift 1.5 ~ coplanar) = crinkled seam lines down the sides -> clear felt-layer overlap (lift 3.5)
for s in SP:
    if s["name"][:3] in ("L25", "L26"): s["lift"] = 3.5
# a12: same fix one layer further out: F4/F5 (L03/L04) were coplanar with S1 (L05/L06) -> crinkled seam down the side curtains -> F4/F5 lift 2.0 (clear overlap)
for s in SP:
    if s["name"][:3] in ("L03", "L04"): s["lift"] = 2.0
for s in SP:
    if s["name"][:3] in ("L23", "L24"): s["flick"] = 20.0
# b2: side curtains a little thicker (felt) with long straight tapers to clean points
for s in SP:
    if s["name"][:3] in ("L05", "L06", "L13", "L14", "L19", "L20"):
        s["tk"] = 7.5; s["lens"] = 0.3; s["pt"] = 1; s["ptp"] = 1.0; s["pte"] = 2.0
        if s.get("subs"): s["subs"] = [dict(sb, pt=1, ptp=1.0, pte=2.0) for sb in s["subs"]]
# b4: b2's straight taper (pte 2) made the curtains' lower halves narrow fingers (prof 0.36 at 80 % length) -> keep them broad to ~75 % and point only at the end
for s in SP:
    if s["name"][:3] in ("L05", "L06", "L13", "L14", "L19", "L20"):
        s["pte"] = 4.0
        if s.get("subs"): s["subs"] = [dict(sb, pte=4.0) for sb in s["subs"]]
for s in SP:
    if s["name"][:3] in ("L05", "L06", "L13", "L14", "L19", "L20"): s["tk"] = 6.5
# v3.44 c3: the broad S1 curtain must not read as one slab -> TWO felt locks: a full-length base blade plus a narrower blade stepped 2 mm proud on its
#     face side that ends in its own point higher up and fans slightly away (shadow step + parted tips like the photo's layered side locks)
for s in SP:
    k = s["name"][:3]
    if k in ("L05", "L06"):
        d = s["co"][0] - C; sg = 1.0 if np.arctan2(d[1], d[0]) >= 0 else -1.0
        b0 = dict(s["subs"][0]) if s.get("subs") else dict(c=0.0, w=1.0, len=1.0, tw=1.0, lift=0.0)
        lb = b0.get("lift", 0.0)
        s["subs"] = [dict(b0, c=0.28 * sg, w=0.72, len=1.0, pt=1, ptp=1.0, pte=4.0, fan=0.05 * sg),
                     dict(b0, c=-0.36 * sg, w=0.6, len=0.82, lift=lb + 2.0, pt=1, ptp=1.0, pte=3.0, fan=-0.10 * sg)]
# v3.44 c7: pitch room - front fringe / front-side blades 6.0 -> 5.2 mm (lens .37 keeps the ~1.9 mm felt edges), mass sits ~80 mm in front of the pitch axis
for s in SP:
    if s["name"][:3] in ("L00", "L21", "L22", "L25", "L26", "L03", "L04"): s["tk"] = 5.2; s["lens"] = 0.37
# c11: pitch counterweight from the remaining mass headroom - back locks B1/B2 (behind the pitch axis, mostly under the hat) stand 1.5 mm higher (layer lift; their crest/liftk is clamped by the lip minimum)
for s in SP:
    if s["name"][:3] in ("L09", "L10", "L11", "L12"): s["lift"] = s.get("lift", 0.0) + 1.5
# c14c: closed crown needs ~2 g -> side-curtain felt blades 6.5 -> 5.6 mm (lens .30 -> .35 keeps the ~1.95 mm edges; widths/points/split unchanged)
for s in SP:
    if s["name"][:3] in ("L05", "L06", "L13", "L14", "L19", "L20"): s["tk"] = 5.6; s["lens"] = 0.35
