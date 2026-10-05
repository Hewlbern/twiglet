# Twiglet body v3.34: bigger hollow FEETECH gripper boxes + wider, flared kilt

All modelling was done in Blender (`body-v3.34-body/blender/body_v334.blend`, built from `body_v333.blend` / v333h; scripts `v334_arms.py`, `v334_kilt.py`).
Head and neck are v3.30 and unchanged. The renders and the wig-vs-arm sweep use `hair-v3.34/FINAL_WIG_model_frame.stl`.

## What changed
- **Gripper box:** 29 x 47 x 43 mm -> 36 x 47 x 57 mm. The photo box is ~42 x 62 with a ~47 mm face.
  - The box is longer along the forearm (about 52 mm of prong now shows below it, as in the photo) and deeper.
  - Still a HOLLOW shell: 1.6 mm walls, open bottom, same servo seat and finger. The housing grows 37.0 -> 41.7 cm3, about +5.8 g per side.
- **Kilt:** all 10 petals are wider and flare further out. Pointed leaf tips, layering and the band fit are kept.
  - Hem radius: front 98 -> 118, back 102 -> 122.
  - Hem height: the front petals stay at the v3.33 height; sides/back are 6 mm longer.
  - In the original view the whole kilt silhouette goes 151 x 120 -> 203 x 132 mm (photo 191 x 145), and kilt IoU .525 -> .608.
- Only 12 files changed: `v334_gripper_housing_L/R` and `v334_kilt_petal_00..09`. The other arm parts are the unchanged v3.33 files.

## Key metrics (metrics_v334.json)
- **Arm IoU at the best-fit pose:** front .565/.552 -> .597/.582; original .459/.536 -> .471/.568. At the rest pose: front .412/.406 -> .452/.442.
- **Mass:** 2.725 -> 2.753 kg (forearm +5.8 g per side, kilt +15.7 g).
- **Sim (policy v334r1, a light retune of v333r1):**
  - e-margin 34.0 mm; head pitch about 2.36x
  - max-speed gait 20/20 at 0.208 m/s; efficient gait 20/20 at 0.156 m/s; held-out seeds 19/20
  - Without the retune, v333r1 scored 19/20.
- **Checks:**
  - All parts are watertight single bodies. Elbow and gripper sweeps 0. Arm sweep 0/162. The shoulder hits only at -10°, outside the soft limits (same as v3.33).
  - Head range 154/315 and exact head x upper-arm 121, both identical to v3.33.
  - Wig-arm with the v3.34 wig: 0 hits inside the soft limits for all 3 registration fits.
  - Kilt swing in the walking gaits 0/1500 for legs and arms.

## Open items
- **Front width:** in the front views the kilt is capped by the arm corridor. The arms hang at |y| >= 67.7 and swing through the whole front half, so the front hem width is 124 -> 135 mm, not 191.
  - Getting closer needs the shoulders moved out about 10-15 mm (a spacer), or flexible TPU side petals that the arms push aside.
- **Synthetic leg grid:** gait120 extreme-knee poses give single-leg 12 (v3.33 8) and both-legs 1 (v3.33 3).
  - It is the swing foot touching under the flared front hem at knee 55-96°. The real walking gaits are contact-free.
- **Wig placement:** registered by ICP (about ±2 mm), because the exact hair transform was lost in the 04:15 box restore.
- **Order of checks:** parts_check, arm_check and hb were run on v334a, whose front petals were 6 mm longer, so they are conservative for the final v334b.
