# Twiglet head A for the Open Duck Mini v2 (photo-accurate ball head)

This is head **A**, the one chosen: a 170 mm wood-grain ball with big black eye discs, orange rings, an offset tube snout, a yellow printed fringe and a black chin collar.
**The hat and the green kilt are FABRIC**, made by you, and are never printed. The ghost hat in the renders only shows where the felt goes, and the clearance checks include it inflated by 3 mm.
Variant B (the game-style head) is in `variant-b/`, but it is not part of this pack.

## Parts (all in `stl/`, print-oriented; the previous revision is in `stl_prev/`)

All parts are watertight single bodies and fit the Bambu P1S bed (256 mm).

| File `twiglet_head_v2_…` | Colour | Qty | Size mm | ~g | Orientation / supports |
|---|---|---|---|---|---|
| head_upper | wood brown PLA | 1 | 168×168×73 | 78 | Split-plane rim down. Tree supports inside the crown only. |
| head_lower | wood brown PLA | 1 | 169×170×66 | 148 | Deck down, neck opening up. Tree supports "on build plate only" for the snout collar and bearing pocket. |
| chin_collar_L / _R | **black** PLA | 1+1 | 144×72×11 | 7 each | Joint face down, no supports. This is the photo's dark collar. |
| eye_cup_L / _R | black / very dark brown | 1+1 | 67×67×9 | 20 each | Back down, no supports. |
| eye_ring_L / _R | translucent **orange** | 1+1 | 35×35×4.4 | 4 each | Flat back down. |
| snout | wood brown PLA | 1 | 61×61×71 | 42 | Mouth down, no supports. |
| fringe | **yellow** PLA | 1 | 108×240×129 | 75 | Forehead up. Tree supports under the hidden underside and the tips. |
| display_stand (optional) | any | 1 | 132×132×142 | 114 | Base down. |

- Robot head printed total: **≈405 g**. The stock printed head is ≈317 g.
- The mass assumes 3 walls and 15 % gyroid infill, with the shells effectively solid.
- See `renders/parts_sheet_A.png` for the true colours.

**Hardware**
- M3 heat-set inserts:
  - 4 in the copied roll-mount bosses;
  - 4 in the dome columns;
  - 4 radial ones in the collar tabs (Ø4×6).
- M3 screws: 4 for the mount, 4 for the dome, 4 for the collar (M3×8, radial).
- 4× M2.5 for the Pi (stock standoffs).
- 4× M2.5 for the relocated ODM board on top of the deck.
- Six 3 mm LEDs behind the rings (optional).
- 5 × 3 mm magnets and/or stitching for the hat.

## Assembly order (bench, head upside down, collar OFF)
1. Fit the inserts.
2. Glue each orange ring into its black cup, and each cup into its pocket in the dome.
   - Bend the LED leads short. The pocket behind each ring leaves ≈10 mm of depth.
3. Glue the snout spigot into the socket, keyed. **Glue it to head_lower only**; the dome lifts off freely (checked).
4. Press and glue the fringe's pegs into the holes below the hat line, on the dome.
5. Put the Pi Zero on its standoffs (3 screws go straight in; the one at (65, 60) needs a ~20° tilted driver).
6. Put the relocated board on top of the deck (4× M2.5).
7. Fix the head to the stock `head_roll_mount` with 4× M3, vertically from below.
   - The holes match the stock mesh to within 0.1 mm.
   - The stock bearing sits in the copied holder.
8. Close the dome with 4× M3 from below. Use a ball-end hex at ~15°.
9. The neck side screws (`head_pitch_to_yaw`, 8× along ±y) can all be reached straight on, **even with the collar fitted** (tool path checked with a 110 mm driver).
10. Fit the two black collar halves around the neck: 2 radial M3 per half, into the tab inserts.
11. **Cables:** route the head cable down the side of the neck, not the back.
    - At the collar opening (Ø122 at z 166) the radial gap is 17–29 mm at the sides.
    - At the back it is ~0, so don't route there.
    - The deck cut-outs pass the leads down from the Pi and the board.
12. Dropped from stock: `head_bot_sheet`, the antenna holders and the SG90 "ears".

**Fabric hat anchors** (fitted to the photo's brim line: front edge at el 70°, back at −10°):
- a groove ring marks the hem line;
- 5 × 3 mm magnet pockets;
- 4 × Ø2 stitch holes.
- The fringe root band sits under the brim, so the felt covers the fringe roots.

## Fit with the rest of the robot (checked; scripts in `fit/`)

- **Rest pose:** the head parts don't touch each other or the ODM (mount, roll servo, bearing, Pi, neck). The relocated board envelope is clear too. Minimum clearance 1.0 mm (head_lower vs head_yaw_to_roll).
- **Body change:** the shoulder axis was lowered 12 mm (z 84 → 72) and the shoulder-mount plate top trimmed (124 → 110).
  - Without this, the chin hit the shoulder mounts and servos when looking down.
  - The rest-pose checks of the whole robot are clean.
- **Head/neck sweep, 525 poses:**
  - Twiglet-only hard collisions (printed parts plus felt hat +3 mm) went from 60 to 10. All 10 remaining are at extreme yaw+roll+pitch combinations.
  - The stock head itself collides in 290 of these poses.
- **Soft limits** (URDF joint degrees): collision-free on a finer 3330-pose grid, and they keep 78 % of the poses where the stock head is clear:
  - |head_roll| ≤ 20°
  - neck_pitch + head_pitch ≥ −35° (no deep look-down onto the chest)
  - if |head_yaw| > 60°: head_pitch between −20° and +10°
  - if neck_pitch ≥ 40°: |head_yaw| ≤ 90°, and |roll| ≤ 10° when |yaw| > 45°
- **Arms:**
  - With the head neutral, the first contact is at shoulder-forward 105° (elbow 90°) to 135° (elbow 0°). Soft limit: shoulder forward ≤ 100°.
  - For walking, keep the elbows flexed ~90°. That gives 0 of 120 random gait poses colliding. With straight arms, 5 of 120 extreme gait samples touch fingers to foot or knee (it was 2 of 120 before the shoulder drop).
- **Felt hat tail:** it drapes onto the neck, back and shoulders in many poses (soft contact only). Keep the tail short and floppy, or tack it to the crown.

## Neck servo load (STS3215, 7.4 V, stall ≈1.91 N·m)
- Head assembly mass (bottom-up): stock ≈456 g → head A ≈583 g. That includes the servo, Pi, board, inserts and ~45 g of felt hat.
- The head's centre of mass moves ≈16 mm forward and 30 mm up.

| Joint | Stock worst | Head A worst | Head A margin |
|---|---|---|---|
| neck_pitch | 0.63 N·m (33 %) | 0.96 N·m (50 %) at neck 65 / head +45 | 1.98× stall |
| head_pitch | 0.27 N·m | 0.53 N·m (28 %) | 3.6× |
| head_roll | 0.03 N·m | 0.12 N·m (6 %) | 15× |

- At rest the load is 0.20 N·m (11 %).
- With neck + head pitch kept between −35° and +45°, neck_pitch stays ≤ 0.64 N·m (33 %, 3×).
- **No head scale-up is recommended.** At ×1.1 the neck_pitch worst case rises to ≈1.4 N·m (~74 % of stall), and the chest/shoulder clearance is lost.

## Proportions vs the photo
| | Photo | Model (head A on ODM + Twiglet body) |
|---|---|---|
| Head Ø / total height (no hat) | ~0.38 (0.41 raw, minus the camera-from-above bias) | **0.34** (170 / 503 mm) |
| Head Ø / total height (with hat) | 0.34 | 0.33 (170 / 517 mm) |
| Head Ø / shoulder width incl. arms | ~1.16 | 1.42 (arms 120 mm wide, in front of the torso) |
| Slim torso | yes | ODM trunk 110 mm wide |

The head is about "a third of the height", as intended.

## Fidelity vs the photo (camera matched: az +13°, el 15°; see `renders/compare_overlay_photo.png`)
| Feature | Photo | Before | Now |
|---|---|---|---|
| Eye disc / ball Ø | 0.41 | 0.31 | 0.39 |
| Eye azimuth / elevation | ±32° / ~19–20° | ±24° / 21° | ±32° / 19.5° |
| Ring OD / disc; pupil / disc | 0.52; 0.26 | 0.54; 0.32 | 0.52; 0.27 |
| Snout mouth OD / bore / lip | ≈61 / 45 / 8–9 mm | 46.8 / 31 / 7.9 | 61 / 45 / 8 |
| Snout axis (points to the viewer's left, slightly down) | photo fit | yaw 0, pitch −10 | yaw −28, pitch −8 |
| Mouth position (projected, units of R) | (−0.72, −0.64) | (−0.37, −0.64) | (−0.71, −0.63) |
| Fringe clumps / thickness | ~13–16, felt-thin | 11 / 12 mm | 15 / 7–7.5 mm |
| Side locks | to jaw level, viewer's right wider | short | to ~el −20°; viewer's right flares wider |
| Hat front edge | el ~70–75° | 54° | 70° |
| Dark collar | yes | none | black split collar |

## Honest mismatches
- The printed fringe is still more regular than felt strands. Dry-brush it, or overlay felt, for the photo look.
- The side-lock tips were shortened ~6° to clear the chest when the head yaws. The photo locks hang slightly lower.
- The photo shows the head sitting directly on the shoulders. On the ODM, ~40 mm of neck stack shows between the torso top and the collar. Suggestion: a black fabric neck gaiter, which is flexible and won't limit motion.
- The ODM body is not the photo body:
  - the legs are wide-set (239 mm);
  - the arms hang in front of the torso;
  - so the shoulders read narrower than the head (1.42 vs 1.16).
- Widening the arms beyond y ±60 would put the fingers into the legs during gait, so I didn't change it.
- The eye discs are flat printed bezels, not the photo's glossy domes.
- The ghost hat is indicative. Your real felt hat's tail length decides how often it drapes on the body.
