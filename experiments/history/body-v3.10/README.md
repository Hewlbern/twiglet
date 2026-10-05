# Twiglet ODM robot, body v3.7

Built from v3.6, which is left unchanged. The user picked "chunkier boots, wood grain, green leaves and chunkier locks". The two new reference photos (measure/ref_front.png, measure/ref_34.png) guided the grain pattern, the leaf placement and the lock shape. The 210 mm head, all mounts, the cone body, the arms and the legs are as in v3.6.

## What to reprint (changed_parts_v36_to_v37.json)
- **Head (twiglet-head-v3.7-stl.zip):** head_upper, head_lower, snout (grain) and fringe (new). Chin collars, eye bezels and display carriers are unchanged.
- **Body:** torso_shell_front/back (grain, leaf sockets, vine without the old embossed lumps), shin_cover_L/R (grain), upper_arm_L/R and forearm_L/R (grain, leaf socket).
- **New parts:** boot_L/R (chunky boots, which replace the body-v2 boot shells), and leaves (green PLA): leaf_L x2 (shoulders), leaf_M x3 (elbows, top of chest), leaf_S x2 (vine).
- **Unchanged (reuse):** all other parts: frame, cradle, hip ring/brackets, thigh parts, boot cuffs, sleeves, grippers, fingers and head_yaw_to_roll.

## Chunky boots (v37_features.boot)
- Wide, flat black blocks with a rounded toe (superellipse plan, fuller at the front), a thick visible sole band (9 mm, stepped 2.1 mm proud) and a rounded top edge.
- Size: 128.6 x 65.6 x 34.5 mm (v3.6 boot shell: 110 x 53 x 24 mm).
- Hollow: 1.5 mm double wall, cavity open underneath, bridged roof. Print sole down with no supports. About 33 g more per boot than the v2 shell.
- Contact footprint is unchanged: the boot bottom sits 1.5 mm above the floor, so only the TPU sole touches (the sim sole box is identical to v3.6).
- Each boot is shifted 2.5 mm outboard so the inner faces stay as far apart as possible (foot-to-foot).

## Wood grain (v37_features.grain_sph / grain_cyl)
- Pattern: vertical plank-like striations with deeper seams about every 21 mm, faint horizontal ring banding (as in the photos), and concentric rings around the eye sockets.
- Parts: head shells, snout, torso cone shell, upper-arm and forearm covers, shin covers.
- Method: a radial map of each part's outer surface is built from surface samples. A grooved skin (surface + 0.15 - depth x pattern) is subtracted in a thin band just outside the surface (manifold boolean), so inner faces and mounts are never touched and the output stays watertight.
- Depth is up to 0.55 mm and is made shallower locally so that no wall drops below 1.25 mm. Measured minimum wall after grain: head_upper 1.40, head_lower 1.40, snout 1.41, torso shell 1.39, shin covers 1.50, upper arm 1.43, forearm 1.41 mm (grain_report_v37.json).

## Leaves (v37_features.leaf_local / place_leaf / socket)
- Flat pointed leaves, 1.8 mm thick, with engraved veins, a stem, and an integral 2.9 mm peg that goes into a 3.3 mm through-socket in the shell or cover. Print veined face down with the peg up (no supports) in green PLA. Add a drop of CA.
- Seven leaves, placed like the photos: one on each shoulder (upper-arm plate, reaching up over the sleeve, tilted out 30 deg), one on each elbow (forearm), and three on the chest vine (the top one at z 80, lowered from 84 to clear the head at -34 deg pitch).
- The vine relief is kept; its four small embossed leaf lumps were removed.

## Chunky fringe (v37_features.fringe, head_v37.py)
- 11 broad, flat, felt-like locks (38-42 mm wide, about 7 mm thick, soft lens section with a slight central ridge, pointed tips) on a crown cap under the hat. The locks curve down over the upper eye rims and flare out at the sides, as in the photos.
- The underside follows the ball (0.3 mm gap). Bezels and snout are cut clear.
- The one-piece fringe is 150 x 226 x 169 mm, which fits the P1S. Pinned split halves are included as an alternative.
- Screen coverage: 4.2 % of each visible screen circle (v3.6: 0 %). Only the top rim is covered, less than in the photos.

## Eyes
- The firmware already has the heart expression shown in the photos (`EYE HEART`, double beat, in head-v3-digital-eyes/firmware/TwigletEyes/TwigletEyes.ino + eye_bitmaps.h; `pi_eyes.py expr("heart")`). Ring eyes are kept.
- The renders show hearts in v37_vs_new_photos.png and v37_three_quarter_hearts.png.
- Sockets are unchanged: the 82.8 mm black bezels already give a dark socket, and deepening them would move the mounts.

## Checks
- All STLs are watertight, one body each, and fit the P1S (41 body parts, 12 head parts).
- Sims: see sim/compare_v36_v37.md. Mass is +94 g. The walk needed no re-tune.
- Collisions (collide_report.json):
  - No clash at rest or with the arms at rest. Gait with both legs and with arms + legs: 0 contacts. Single-leg check: 21 (the same leg-spacer / shin-cover cases as v3.6's 20).
  - Arm sweep: 51 hits, all arm vs head at extreme poses as before; none involve the leaves.
  - New boot limits: inward hip roll is free to 10 deg (v3.6: 13; the gait uses about 9.1), ankle toe-down is free to -54 deg (v3.6: -65; boot vs boot cuff), and knee to 87 deg.
  - Head pitch is free -36..+10 as in v3.6, so the -34 soft limit keeps its margin (the top chest leaf was lowered for this).
- Fringe printing: the one-piece fringe is exported in the least-overhang orientation found by search (about 25 cm2 over 45 deg). The split halves need only about 7 cm2 each, so print those for minimal supports.

## Remaining differences vs the new photos (not in v3.7 scope)
- Torso: the photos show a slimmer torso narrowing to a thin dark neck, with a visible gap under the head exposing the neck mechanism. The v3.6/v3.7 cone and chin collars close that gap.
- Arms and grippers: the photos show thinner wooden arm segments, big black grippers and a black cable looping from each gripper up to the shoulder.
- Shoulder leaves in the photos are larger clusters (2-3 leaves) sitting on top of the shoulder joint. v3.7 has one leaf per shoulder and elbow, which is subtle in renders against the black sleeves.
- The fringe in the photos is slightly more ragged/asymmetric, and the photo locks cover a bit more of the upper eye.
- Eye sockets in the photos look deeper and larger (dark ring around the screen).
