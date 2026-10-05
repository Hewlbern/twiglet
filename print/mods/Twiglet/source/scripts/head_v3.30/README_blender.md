# v3.30 wig locks in Blender: handover

Blender 4.2.23 LTS (headless): `$BLENDER (4.2 LTS)`.

## Files
- `locks_v330.json`: the 21 lock spines exported from the v3.29 procedural wig (`export_locks_v330.py`). Each lock has n = 48 samples, and each sample stores
  B (spine point on the seat, mm, head frame), N (normal), L (unit direction), W (full width), H (crest height), plus params/style/name.
- `build_wig_v330.py`: JSON (or `--from-blend`) -> Bezier spines (collection "LockSpines": point co = spine, point radius = half width,
  point weight_softbody = crest height; object props lip / p_top / off) -> loft (superellipse top p_top on a 2 mm side wall, buried 4 mm,
  NA 32 around, NT 96 along) -> SUBSURF 2 -> join -> voxel remesh 0.7 mm -> Taubin smoothing (0.5 / -0.53, 20 iterations) -> STL.
  The defaults are the shipped v3.30 tuning: `--hs 0.8 --ws 1.15 --ptop 1.4 --voxel 0.7`, ARM_H 0.55 forearm easing, plus the
  per-lock TWEAK table (fringe / front-side / temple crests x1.12, sideburns L13/L14 width x0.8). `--no-tweak` disables the tweaks and `--ovr file.py` runs extra code on SP.
- `wig_v330.blend`: the spine curves, lofted locks and final mesh. `wig_locks_v330.stl`: the build's output, read by `hair_v330.wig_blend`.
- `lock_table_v330.md`: per-lock root/mid/tip (th, phi), length, widths, crest, curl/wave/twist.

## Editing a lock
1. Open `wig_v330.blend`. In "LockSpines", move the curve points of the lock (e.g. `L03_F4`). To make it wider, scale the point radius
   (Alt-S). The crest height is the point's softbody weight. Save.
   You can also edit `locks_v330.json` (B / W / H of the samples).
2. Rebuild the locks: `blender -b -P blender/build_wig_v330.py -- --from-blend blender/wig_v330.blend` (or omit `--from-blend` to use the JSON).
3. Rerun the head chain: `python head_v330.py && python design_v3.py`, then the checks (headrange_v320, armsweep_v330, measure_v330,
   wallsec), then `export_head_v330.py`.

## Reused procedural parts (hair_v330.py)
- `seat_r(env, u)`: seat radius = shell envelope + 0.3 mm glue gap. `height(locks=[])`: crown dome + floor + hat seat + PIN_BOSS (+ HAT / hat_cap recessed felt-hat band).
- `attach_parts`: 4 vertical pins (PINS (th 20, phi 45/135/225/315), PIN_R 1.6, PIN_DEPTH 5.0) + keyed tongue (KEY: TH 31, arcs 70/40/40/40, W 2.4, H 1.1).
- `trim_k(u)`: arm / trunk relief factor. `wig_blend(env, cuts, sub)`: crown + the Blender locks squashed radially by (1 - k), sunk SINK k^2,
  with relieved tips that either keep >= MINP 1.4 mm above the seat or dive under it. Then hat-cap clip, minus the seat, + key tongue,
  minus eye / snout / collar cuts and pin holes.
- `head_v330.py`: cuts = eye-bezel hulls x1.012, snout hull x1.02, chin-collar hulls. Envelope cache `.cache/env_v314.npz`.

# v3.30 face (eyes / bezels / shell openings / snout) in Blender 4.5 LTS

Blender 4.5.9 LTS (headless): `$BLENDER (4.5 LTS)`. All booleans use the MANIFOLD solver (Blender 4.2's EXACT solver
broke the 300-600k-face shells).
1. `python blender/prep_face_inputs_v330.py`: data hand-off only. It writes the unchanged v3.29 parts as STL plus `params.json`
   (ball centre/radius, split height, carrier posts, socket frame, pod pieces) to `blender/in_v329/`. In float32, Blender would snap vertices
   closer than ~3e-5 mm onto each other, so those pairs are pushed 1.5e-4 mm apart first.
2. `blender -b -P blender/face_v330_bpy.py -- [--dz 4.0]`: all modelling. Output goes to `blender/out_v330/*.stl` + `face_info.json`, and the scene is saved
   to `blender/head_v330.blend` (collections v329_input / tools / v330; the tools collection holds every cutter, so the edits can be inspected and re-run).
   - Eyes: 4 mm lower; round revolved bezels (dark disc 70.8 mm, window 59.6 mm, ring 5.6 mm); flat wood rim to rho 42, blend to 49
     (constants R_OUT / R_WIN / R_SPIG / R_BORE / RF / RB / DZ at the top of the script). The old openings are refilled with a ball-wall cap, then
     the facet, blend, bore, ring pocket, 4 grain rings and backing ring are re-cut about the lowered eye frame. The carriers move down DZ, and their
     2 M3 posts are shortened DZ with the heat-set insert holes re-drilled. The pod and bezel lift sweeps are extended.
   - Snout: revolved cone (OD 65 -> 72 mm, L 72, 3 mm rounded mouth rim) on yaw -4 / pitch +22, a 3 mm concave root fillet onto the ball,
     39 wood-grain grooves (0.9 x 0.45 mm), and the keyed spigot + flush plug on the unchanged head_lower socket frame. Then minus the bezel hulls,
     the pod lift sweeps and the head-split lift cylinder.
3. `blender -b blender/head_v330.blend -P blender/stl_safe_v330.py -- eye_bezel_L eye_bezel_R display_carrier_L display_carrier_R snout head_lower head_upper`: float32-safe export (weld, delete zero-thickness coincident face pairs, dissolve slivers, fill micro-holes), then re-imports every STL and gates it (all edges 2 faces, 1 body, volume vs in-memory; results in `out_v330/stl_safe.json`). Replaces the older destructive `stl_clean_v330.py` loop.
   Result: every STL re-imports with 0 open / 0 non-manifold edges and 1 body; volume change vs the exact solver mesh < 0.01 %.
4. `python blender/load_face_v330.py`: loads the Blender STLs into the head-chain caches. Then run `head_v330.py` and the checks.

## v3.30 chin-collar relief (head range)
1. `python blender/trim_v330/mk_collar_cutters.py` (run inside trim_v330/): hem cutters (model frame), `collar_cutter_L/R.stl`; `snout_clear_cutter.stl` = snout convex hull x1.02.
2. `blender -b blender/head_v330.blend -P blender/trim_collars_v330.py`: imports the untrimmed collars (`trim_v330/chin_collar_*_v329.stl`) into collection
   `v330_collar_trim`, MANIFOLD Boolean minus both cutters, float32-safe export + gate -> `out_v330/chin_collar_L/R.stl`, `out_v330/collar_trim.json`; saves the blend
   (untrimmed scene: `trim_v330/head_v330_pretrim.blend`).
3. `python blender/trim_v330/load_trim.py`: puts them into `.cache/head_v330.pkl` and both `v3model.pkl` (pre-trim copies `*_pretrim.pkl`).
4. Zip: `blender/decimate_v330.py` ratio 0.67 -> `out_v330/collars_dec/` (max deviation 0.012 mm), then `export_head_v330.py`.

## v3.30 head-range redesign (holder, collar tabs, neck)
1. `cd blender/redesign_v330 && python mk_redesign_parts.py` -> cutter / adder STLs (head parts model frame, neck print frame) + redesign_parts.json.
2. `blender -b blender/head_v330.blend -P blender/redesign_v330.py`: inputs `redesign_v330/in/*` (pre-redesign v3.30a), MANIFOLD Booleans,
   float32-safe export + gate -> `out_v330/{head_lower,chin_collar_L,chin_collar_R,head_yaw_to_roll}.stl`, `out_v330/redesign.json`; saves the blend
   (pre-redesign scene `redesign_v330/head_v330_preredesign.blend`).
3. `python blender/redesign_v330/load_redesign.py`: caches (head_v330.pkl, both v3model.pkl; bearing +12.1 mm, neck part, 25 g ballast_back).
4. `python blender/redesign_v330/post_checks_rd.py` -> post_checks_rd.json (overlaps, hardware, neck vs head in roll / yaw, lift, eye cover, thin).
5. Zip: `export_head_v330.py` (collars no longer decimated; head_yaw_to_roll emitted from out_v330).
