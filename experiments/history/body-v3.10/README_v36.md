# Twiglet ODM robot, body v3.6

Built from v3.5, which is left unchanged. The user asked for a proportionally larger head, a more sloped body, arms closer in, and everything closer to the photo.

## Head: 210 mm ball (was 180), reprinted
- Torque: the head is centred over the pitch axis, so static head-pitch torque stays around 0.20 to 0.23 N·m at every size tried (190 to 220). In the sim it is 0.225 N·m, 0.46x rated, a margin of about 2.2x. Yaw and roll static torques are under 0.01 N·m. Every size passed the 1.4x rule, so torque did not decide the size.
- Proportions: renders from the photo's camera (renders/head_size_v36_photo_camera.png) show the head + fringe + hat outline matching the photo's hat top and fringe spread at 210 to 220. At 210 the rotational inertia is 1.53x the 180 mm head (220 would be 1.76x). The head+arm dynamic head-pitch peak is 0.667 N·m (v3.5: 0.542). I chose 210 as the best balance of look and dynamics.
- The head was rebuilt with mounts cut 1:1 to the real hardware (roll mount, Pi Zero, eye driver, 2.1in display carriers), not a uniform scale. The fringe is split a/b with 2x 3 mm pins so it fits the P1S bed. See print_sheet_head_v36.md and ../../twiglet-head-v3.6-stl.zip.
- Soft head-pitch range is -34..+3 deg (collision sweep is clean over that range).

## Body: smooth cone (torso_env_v36.py)
- For each of 120 rays, the v3.5 envelope is replaced by a concave majorant over height plus a minimum taper, then angularly smoothed. The top is a 5 mm round shoulder dome into a slim neck ring. The result is one smooth surface with no frame lumps; the vine relief is kept.
- Depth is 128.9 mm (v3.5: 117.5) because the front slopes out to the hem. Width goes from 54.5 mm half-width at the waist to 39 mm at the top.

## Arms
- TILT 13->10 deg, shoulder YS 46->45 mm, elbow rest 20->30 deg. The tuck is limited by the cone width at elbow height. Outward left hip roll is now limited at -20 deg by the hip-roll servo, not the gripper.

## Checks
- collide_report.json: no clash at rest or with arms at rest; gait with both legs and with arms+legs has 0 contacts; single-leg results are the same 20 known cases as before; the arm sweep has 51 hits, all arm-vs-head at extreme poses.
- Sims: see sim/compare_v35_v36.md. The max-speed gait was re-tuned: 100% success at 0.172 m/s.
- BOM is unchanged from v3.5: 13x STS3215 (bom_v35.md). All STLs are watertight, one body each, and fit the P1S bed.
