# hair v3.40 STATUS  (box clock AEDT, UTC+11)
Request (Sun 4 Oct 11:48 AEDT): refine v3.39 x5 (hair-v3.39 untouched = fallback). All modelling in Blender. 1) clearer gaps between lock tips (rounder locks merge where they meet):
 V-notches / narrower near tips / offset depths-layering so each tip reads as its own chunky pointed lock. 2) more photo style (chunky felt, layered, clean points). Weight-neutral or lighter.
Budgets: pitch >=2.0x (x5 2.07x), mass <=186.5 g (x5 180.3), eye 0, arm in-soft 0, range ~154/315, wall min ~2 mm, watertight 1 body, P1S; head v3.30 fit/pins unchanged.
Deliverables: $WORK/hair_closeup_v339_v340.png (photo | x5 | v3.40) + IoU/outline first, then full checks, FINAL_WIG.stl.
Baseline x5: 180.3 g, moment 1583, pitch 2.07x, margin 33.1, IoU .477/.593/.614, out-hat .667/.649/.642, outline 13.39/6.25/9.51, walls min 2.30.
- 11:48 setup: copied from hair-v3.39 (x5 -> y0 + x5 variant files; x5 = the Blender pipeline source of hair_v339.blend), paths sed'd to hair-v3.40.
- 11:50 y0 (= x5) reproduces x5 exactly (180.3 g, 1583, IoU .477/.593/.614).
- 11:50 diagnosis (work/crop_x5_front.png): lower edge of the fringe beside the eye blades is one smooth curve = the long lower EDGES of F2/F3 (L01/L02 run diagonally out to th 55/ph +-64), so no tips read there; photo has a serrated edge (a point over each eye's outer top, then temple points). Plan y1: F2/F3 tips turned down (dph 14 toward the centre, dth +4) -> their points land over the eyes' outer tops, exposing the temple layers' (L15/L16) own points beyond = V notches between eye blade | F2/F3 | temple layer tips.
- 11:53 y1: F2/F3 tips turned down (tip th 59/66, ph +-50): 180.5 g; IoU .477/.595/.617, outline 13.38/6.26/9.48; visually no change (pair_x5_y1_front.png). Root cause from spines: the front locks are very WIDE overlapping sheets (half-widths F2/F3 22.5 mm, temple layers 26, F4/F5 32-36 mm = 65-72 mm wide) -> every tip is covered by a neighbour, the band reads as one surface. Next y2: front locks narrower (w x0.65-0.7 root, x0.6 tip) so each lock's point and the seat groove between locks show (lighter too).
- 11:55 y2: front locks narrower: 176.4 g (-3.9), moment 1280; IoU .473/.596/.623, out-hat .667/.655/.653, outline 13.27/6.05/9.03 (all outlines better than x5). Visibly more separate pointed locks along the fringe with grooves between (pair_x5_y2_original.png). QUICK CLOSE-UP written $WORK/hair_closeup_v339_v340.png (photo | x5 | y2) = latest_closeup.png. Next y3: narrower still (0.58/0.5).
- 11:56 y3: narrower still (0.58/0.5, F4/F5 0.55/0.5): 175.2 g; IoU .472/.590/.616 (down vs y2), visually ~= y2 -> keep y2 widths. Next y4: y2 + stronger layer steps between neighbours (F2/F3 lift 1.0 -> 2.2, eye blades 2.4 -> 3.4) so each lock edge casts its own shadow line.
- 11:58 y4: y2 + stronger layer steps (F2/F3 lift 2.2, eye blades 3.4): 176.8 g; IoU .474/.596/.623 (= y2); image diff vs y2 only 0.4-0.6 grey levels, full-res crop (work/zz_y2_y4_original.png) no clear gain -> keep y2 (lighter). FINAL CANDIDATE = y2 -> full checks (arm first).
- 12:03 y2 arm check: raw 3/27/35 (x5 4/27/35), in-soft 0/0/0, range 154/315, wig-only 0 -> PASS.
- 12:03 y2 sim: wig 176.4 g, head 804.3 g, ctrl 0.2299 -> pitch 2.13x (x5 2.07x). run_tests started.
- 12:17 y2 run_tests: motion margin 33.4 mm, standing 46.5, no falls. xml sim/twiglet_v3_y2_v340.xml. Next: decimate + walls.
- 12:22 y2 walls (60k, 59,984 faces): body area <1.2 mm 0.00 cm2 of 1125, body min 2.30 mm (= x5) -> PASS. Next: export.
- 12:23 EXPORT y2: FINAL_WIG.stl (59,984 faces, watertight, 1 body, 248.2x223.1x242.2 mm, fits_P1S true), FINAL_WIG_model_frame.stl + out/, hair_v340.blend (object FINAL_WIG_v340_y2),
  $WORK/hair_closeup_v339_v340.png (photo | x5 | y2) = latest_closeup.png; latest_compare.png refreshed.
## FINAL v3.40 = y2 (x5 untouched in hair-v3.39 = fallback)
  176.4 g @4.5% (x5 180.3), moment 1280 (1583), pitch 2.13x (2.07x), margin 33.4 (33.1), standing 46.5, eye 0/0, arm in-soft 0/0/0 (raw 3/27/35), range 154/315, wig-only 0, walls min 2.30 (2.30), 1 body, P1S ok.
  IoU .473/.596/.623 (x5 .477/.593/.614); out-hat .667/.655/.653 (.667/.649/.642); outline 13.27/6.05/9.03 (13.39/6.25/9.51).
  Changes vs x5: F2/F3 (L01/L02) + temple layers (L15/L16) width x0.7 root -> x0.6 tip, front-side F4/F5 (L03/L04) x0.65 -> x0.6 (were 45-72 mm wide overlapping sheets);
  F2/F3 tips turned down over the eyes' outer tops (dph 14 toward centre, dth +4). Rejected: y3 narrower still (IoU down), y4 stronger layer steps (no visible gain, +0.4 g).
