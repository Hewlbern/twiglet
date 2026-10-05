# v9 (flare 25 seat, all locks re-seated): v7b + F4/F5 lengthened at the tip only (mid unchanged -> eyes clear), fringe side tips shorter (photo shows the eye tops between locks),
#     asymmetric like the photo (robot's left eye less covered), cheek a little longer
EDITS = {
 "L05": dict(ths=1.14, dph=-35.0, pp=1.5, w=(1.0, 0.75), h=(1.1, 0.8), tipw=2.0),
 "L06": dict(ths=1.14, dph=36.0, pp=1.5, w=(1.0, 0.75), h=(1.1, 0.8), tipw=2.0),
 "L17": dict(ths=1.18, w=(1.0, 1.2), h=(1.0, 0.9)),
 "L18": dict(ths=1.18, w=(1.0, 1.2), h=(1.0, 0.9)),
 "L03": dict(dth=3.0, tp=3.0, dph=-6.0, pp=3.0, w=(1.0, 1.1)),
 "L04": dict(dth=3.0, tp=3.0, dph=6.0, pp=3.0, w=(1.0, 1.1)),
 "L19": dict(h=0.8, ths=1.05), "L20": dict(h=0.8, ths=1.05),
 "L01": dict(ths=0.86), "L02": dict(ths=0.92), "L15": dict(ths=0.86), "L16": dict(ths=0.92),
 "L07": dict(h=0.85), "L08": dict(h=0.85),
 "L09": dict(h=0.7, ths=0.9), "L10": dict(h=0.7, ths=0.9), "L11": dict(h=0.7, ths=0.9), "L12": dict(h=0.7, ths=0.9),
}
RESEAT_ALL = True

# t3: cheek locks dropped (mostly model-only in all 3 photos; 9.5 g at x 64)
DROP = ["L17", "L18"]
# t4: fringe per photo: robot-left fringe (L01) shorter (eye top clear in the original photo), central point a bit shorter
EDITS["L01"] = dict(ths=0.78); EDITS["L00"] = dict(ths=0.94)
# t6: front locks thinner (crest x0.65)
for _k in ("L00", "L01", "L02", "L15", "L16", "L03", "L04"): EDITS.setdefault(_k, {}); EDITS[_k]["h"] = 0.65
# t7: hidden back locks lower (B1/B2 crest .7->.5, S23 .85->.65)
for _k in ("L09", "L10", "L11", "L12"): EDITS[_k]["h"] = 0.5
for _k in ("L07", "L08"): EDITS[_k]["h"] = 0.65

# u5 (= u3 done right): robot-left front-side lock narrower, sideburn L 4 deg toward the face
EDITS["L03"].update(w=(0.9, 0.9)); EDITS.setdefault("L13", {}).update(ph_all=-4.0)

# v3 (v3.37): photo fringe has a big flat blade over each eye hanging down-outward to the eye-rim top (crossing over the side-swept F2/F3);
#     u5 had nothing hanging there (F2/F3 run along the brim) -> two new eye blades, tips on the bezel above the screen (eye cover must stay 0)
NEW = [dict(name="L21 eye blade L", th=[16, 26, 36, 46, 54, 60], ph=[9, 12, 16, 21, 26, 30], w=[13, 13, 12, 9, 5, 1.5], h=[6, 9, 11, 9, 5, 2], lip=2.0, p_top=1.4),
       dict(name="L22 eye blade R", th=[16, 26, 36, 46, 54, 60], ph=[-9, -12, -16, -21, -26, -30], w=[13, 13, 12, 9, 5, 1.5], h=[6, 9, 11, 9, 5, 2], lip=2.0, p_top=1.4)]
# v4: eye blades wider (photo blades are broad flat felt) + tip 3 deg higher (v3 eye cover .006)
for nl in NEW:
    sg = 1.0 if nl["name"].startswith("L21") else -1.0
    nl.update(th=[16, 25, 34, 43, 51, 57], ph=[sg * a for a in (9, 12, 15.5, 20, 24.5, 28)], w=[16, 16, 15, 12, 7, 1.5])
# v6: robot-left eye blade (L21) was half model-only in the original view (photo shows that eye's inner rim clear) -> shifted outward, shorter, narrower
NEW[0].update(th=[16, 25, 34, 43, 50, 55], ph=[12, 15, 19, 24, 29, 33], w=[14, 14, 13, 10, 6, 1.5])

# v3.38 w1: eye blades' lower halves hung below the photo's front fringe edge (front IoU .583 -> .570) -> shorter (tip th 51 / 50) and turned a little more outward
NEW[1].update(th=[16, 24, 32, 40, 46, 51], ph=[-9, -12, -16, -21, -26, -31], w=[16, 16, 15, 11, 6, 1.5])
NEW[0].update(th=[16, 24, 32, 40, 46, 50], ph=[12, 15, 19, 24, 29, 34], w=[14, 14, 13, 9.5, 5.5, 1.5])
# w2: photo front view: robot-right temple has a blade whose tip flicks OUT sideways at eye-top level (photo-only px at th 68-72, phi -80..-88, ~20 mm off the seat)
NEW.append(dict(name="L23 temple out-flick R", th=[40, 48, 56, 63, 69, 73], ph=[-66, -71, -76, -80, -84, -87], w=[10, 10, 9, 7, 4, 1.5], h=[5, 7, 8, 7, 5, 2], lip=2.0, p_top=1.4))
# w3: out-flick reached only r 134 (others already stand at ~132 there) -> tip turned further sideways
NEW[-1].update(th=[40, 48, 56, 62, 67, 71], ph=[-66, -72, -78, -83, -88, -93])
# w4: out-flick tip lower (photo flick sits at eye-top level, slightly below w3's tip) and longer
NEW[-1].update(th=[42, 50, 58, 65, 71, 76], ph=[-66, -72, -78, -84, -90, -96], w=[10, 10, 9.5, 8, 5, 1.5])
# w5: robot-right sideburn 5 deg outward (3/4 + front: model-only on its face side, photo-only just outside it)
EDITS.setdefault("L14", {}).update(ph_all=-5.0)
EDITS["L13"].update(ph_all=-8.0)   # w7: robot-left sideburn further toward the face (3/4: model-only beyond the far-side outline)
# w9: eye blades 15 % broader (photo blades over the eyes are wide felt blades)
for nl in NEW[:2]: nl["w"] = [round(x * 1.15, 2) if x > 2 else x for x in nl["w"]]
# v3.39 x4: robot-left temple out-flick matching the robot-right one (L23), mirrored
NEW.append(dict(name="L24 temple out-flick L", th=[42, 50, 58, 65, 71, 76], ph=[66, 72, 78, 84, 90, 96], w=[10, 10, 9.5, 8, 5, 1.5], h=[5, 7, 8, 7, 5, 2], lip=2.0, p_top=1.4))

# v3.40 y1: F2/F3 tips turned DOWN over the eyes' outer tops (were running out along the brim -> smooth band edge); exposes the temple layers' own points beyond
EDITS["L01"].update(dph=-14.0, pp=1.5, dth=4.0, tp=2.0)
EDITS["L02"].update(dph=14.0, pp=1.5, dth=4.0, tp=2.0)
# y2: separate locks: the front sheets were 45-72 mm wide and covered each other's points -> narrower (the seat groove between them = gap)
for _k, _w in (("L01", (0.7, 0.6)), ("L02", (0.7, 0.6)), ("L15", (0.7, 0.6)), ("L16", (0.7, 0.6)), ("L03", (0.65, 0.6)), ("L04", (0.65, 0.6))):
    EDITS.setdefault(_k, {})["w"] = _w

# v3.42 a7: PARTED fringe (no cutting): the old F2/F3 ran sideways along the eye-rim arc, so their long lower edges + the eye blades' lined up into one
#     continuous ledge. New layout = downward-pointing tapered locks whose tips form a zig-zag (tips at ph 0 / +-22 / +-43, V gaps between them):
#     eye blades re-routed steeper, F2/F3 replaced by steeper locks (L25/L26), buried temple layers L15/L16 dropped (were fully hidden; would fill the V's)
DROP = DROP + ["L01", "L02", "L15", "L16"]
NEW[0].update(th=[16, 24, 32, 39, 45, 50], ph=[12, 14, 17, 19, 21, 22], w=[15, 15, 14, 12, 10, 8], h=[6, 9, 11, 9, 5, 2])
NEW[1].update(th=[16, 24, 32, 40, 47, 52], ph=[-11, -13, -16, -19, -21, -22], w=[17, 17, 15, 13, 10, 8], h=[6, 9, 11, 9, 5, 2])
NEW.append(dict(name="L25 F2n fringe L", th=[16, 25, 34, 42, 50, 57], ph=[28, 31, 35, 39, 42, 45], w=[17, 17, 16, 14, 11, 8], h=[7, 12, 12, 9, 5, 2], lip=2.0, p_top=1.4))
NEW.append(dict(name="L26 F3n fringe R", th=[16, 25, 33, 41, 48, 54], ph=[-28, -31, -34, -37, -40, -42], w=[17, 17, 16, 14, 11, 8], h=[7, 12, 12, 9, 5, 2], lip=2.0, p_top=1.4))
EDITS["L00"]["w"] = (1.0, 0.8)
# a8: a7's V's opened up to th ~40 (too deep, locks spiky vs the photo's broad felt locks) -> the 4 parted locks 25 % broader, L00 lower half less narrowed
for nl in NEW:
    if nl["name"][:3] in ("L21", "L22", "L25", "L26"): nl["w"] = [round(x * 1.25, 2) for x in nl["w"]]
EDITS["L00"]["w"] = (1.0, 0.9)
# a10: photo temple flicks are CHUNKY felt locks (thin spike now) -> out-flicks L23/L24 ~1.5x wider with a long straight taper
for nl in NEW:
    if nl["name"][:3] in ("L23", "L24"): nl["w"] = [15, 15, 14.5, 12.5, 9, 4]
# a13: out-flicks = broad felt locks curving out (photo) rather than a radial horn: longer reach sideways, wider
for nl in NEW:
    if nl["name"][:3] in ("L23", "L24"):
        sg = 1.0 if nl["name"][:3] == "L24" else -1.0
        nl.update(th=[42, 50, 58, 65, 71, 76], ph=[sg * a for a in (64, 71, 79, 87, 95, 103)], w=[16, 16, 16, 14, 11, 5])
# a14: side curtains = chunky felt locks in the photo (thin hanging strands here) -> sideburns 35 % wider, S1 lower halves no longer narrowed
EDITS["L13"]["w"] = (1.35, 1.35); EDITS["L14"]["w"] = (1.35, 1.35)
EDITS["L05"]["w"] = (1.0, 1.0); EDITS["L06"]["w"] = (1.0, 1.0)

# v3.43 b2: photo side curtains = one broad continuous felt mass from temple to cheek whose tips part only at the ends; a14 = separate thin fingers with
#     head showing between -> lower halves of the side locks much wider (they overlap into one curtain), clean straight-tapered points (rib)
EDITS["L05"]["w"] = (1.0, 1.7); EDITS["L06"]["w"] = (1.0, 1.7)
EDITS["L13"]["w"] = (1.35, 2.1); EDITS["L14"]["w"] = (1.35, 2.1)
EDITS["L19"]["w"] = (1.0, 1.5); EDITS["L20"]["w"] = (1.0, 1.5)
# b5: b4 = 189.3 g (over 186.5) -> curtains' lower halves widened less (S1 x1.25, sideburns x1.8, temple flicks x1.25)
EDITS["L05"]["w"] = (1.0, 1.25); EDITS["L06"]["w"] = (1.0, 1.25)
EDITS["L13"]["w"] = (1.35, 1.8); EDITS["L14"]["w"] = (1.35, 1.8)
EDITS["L19"]["w"] = (1.0, 1.25); EDITS["L20"]["w"] = (1.0, 1.25)
# b6: between b5 and b4: curtains fuller (S1 x1.45, sideburns x1.95) within the mass budget
EDITS["L05"]["w"] = (1.0, 1.45); EDITS["L06"]["w"] = (1.0, 1.45)
EDITS["L13"]["w"] = (1.35, 1.95); EDITS["L14"]["w"] = (1.35, 1.95)
# v3.44 c3: b4-level side curtains (S1 lower half x1.8 - S1 hangs at ph ~103, on the pitch axis -> mass only, no moment)
EDITS["L05"]["w"] = (1.0, 1.8); EDITS["L06"]["w"] = (1.0, 1.8)
# v3.44 c7: sideburns to the b4 width (lower half x2.1)
EDITS["L13"]["w"] = (1.35, 2.1); EDITS["L14"]["w"] = (1.35, 2.1)
# c9: L00 point extended only at the tip (dth 5 deg growing as t^3) instead of c8's whole-lock ths (that added 1.3 g / +110 g.mm up front)
EDITS["L00"]["dth"] = 5.0; EDITS["L00"]["tp"] = 3.0
