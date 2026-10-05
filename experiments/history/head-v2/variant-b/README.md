# Twiglet head v2 - Variant B (game-style). Shared README (paths relative to head-v2/)

| | Variant A: photo-accurate (this folder) | Variant B: game-style (`variant-b/`) |
|---|---|---|
| Look | matches your robot photo: big round dark eye discs with orange LED rings, long tube snout, pale-mustard clumped fringe | closer to the Majora's Mask N64 Twiglet kid: angry slanted almond eyes with glowing yellow-orange inserts, short wide octagonal snout, flat olive-yellow leaf-blade fringe, strong vertical wood-grain ridges |
| Ball | Ø170 mm sphere, 2 mm wall, subtle ring grain around the snout | Ø170 mm sphere (+0.55 mm ridges), 2 mm wall, vertical grain ridges (5.5 mm pitch) |
| Snout | tube OD ≈47 mm, 58 mm long + thick lip, keyed spigot | octagon rim ≈81 mm across (≈48 % of face width), protrudes 36 mm, rounded octagon lip, black bore liner, keyed spigot |
| Printed parts | 8 (+ stand) | 9 (+ stand) |
| Est. printed head mass | ≈417 g | ≈436 g |
| Stock printed head (head.stl + head_bot_sheet + 2 antenna holders) | 317 g | 317 g |

Both variants share **the same internals**:
- **Neck mount:** the stock head's roll-mount region (4 insert bosses), roll-bearing holder and Pi Zero standoffs are copied from the official `head.stl` (Apache-2.0).
- **Deck and dome:** the same deck/dome split with 4× M3 insert columns.
- **Hat anchors:** the same fabric-hat groove ring, 5× Ø3 × 1.5 mm magnet pockets and 4× Ø2 stitch holes.
- **Fringe pegs:** the same 3 fringe peg holes.
- **Nothing printed for the hat or kilt.** Both are fabric. A hip ring for the skirt comes later.

## Files
- `stl/twiglet_head_v2_*.stl`: Variant A, print-oriented.
- `variant-b/stl/twiglet_head_v2B_*.stl`: Variant B.
- `build_report.json` / `variant-b/build_report.json`: per-part size, watertightness, volume, estimated mass, overhangs, colour, supports.
- `check_report.json` / `variant-b/check_report.json`: rest-pose interference plus a neck/head pose sweep vs the stock head.
- **Comparison sheets:**
  - `renders/compare_reference_vs_head_v2.png`: A vs your photo.
  - `variant-b/renders/compare_game_refs_vs_variant_b.png`: B vs the game images.
  - `renders/compare_A_vs_B.png`: A vs B.
- Other renders: `renders/head_*`, `display_*`, `odm_mounted_*` (A) and `variant-b/renders/headB_*`, `displayB_*`, `odmB_mounted_*` (B). A ghost hat is shown only in renders and is never exported.
- Scripts: `parts_head2.py`, `export_head2.py`, `render_head2.py`, `checks_head2.py [--variant-b]`, `make_compare.py`, `make_sheets.py`, `variant-b/{parts_head_b,export_b,render_b}.py`. Python 3 with trimesh, manifold3d, shapely and pyvista.

## Print settings (Bambu P1S, PLA/PETG)
- 0.2 mm layers, 3 walls, 15 % gyroid infill.
- Every part fits the 256 mm bed. The largest is a fringe at ≈195–203 mm.
- Orientation is baked into the STLs:
  - **Upper dome:** rim down, tree supports inside the crown.
  - **Lower shell:** deck down. Use tree supports "on build plate only" for the snout collar and the bearing pocket.
  - **Eye parts:** back down, no supports.
  - **Snout:** A goes mouth down; B goes rim down. No supports.
  - **B liner:** flange down.
  - **Fringe:** forehead up, with tree supports under the blade undersides and the tips.
- **Translucent orange/yellow filament** for A's rings and B's inserts lets the LEDs glow through.

## Assembly (both variants)
1. Heat-set the M3 inserts: 4 in the copied roll-mount bosses and 4 in the dome columns.
2. **Eyes:**
   - A: glue the orange ring into the black cup, route LEDs through the 3× Ø3.3 holes, then glue the cup into the shell pocket.
   - B: glue the translucent almond insert into the dark socket (2 LED holes), then glue the socket in.
3. **Snout:**
   - A: glue the spigot into the shell hole with the key aligned.
   - B: the same, then press or glue the black liner into the bore.
4. Press the fringe's 3 pegs into the holes under the hat line and glue them.
5. Put the Pi Zero on the copied standoffs. Mount the relocated board (it doesn't fit where the stock one sat) with 4× M2.5 on top of the deck. Close the dome onto the deck with 4× M3 from below.
6. Fit the head onto the stock head-roll servo mount. Use 4× M3 into the copied bosses, with the stock bearing in the copied holder.
7. **Dropped from stock:** `head_bot_sheet` (wider than the ball), the antenna holders, and the SG90 "ear" servos.
8. **Fabric hat:**
   - The groove ring sets the brim line.
   - Use 3 mm magnets in the pockets, or stitch through the Ø2 holes.
   - The hat's front edge tucks over the fringe.

**Display versions:** `*_display_stand.stl` bolts to the same 4 roll-mount bosses (4× M3 from below through the access tunnels). A has a round base; B has an octagonal one.

## Motion notes
See `check_report.json`. Avoid neck_pitch ≈65° combined with head_pitch −45°: the lower shell touches the neck sheets / body top there (set a soft limit). Sweep of 81 poses (roll ±30, yaw 0/±90, head_pitch ±45, neck_pitch −20/30/65): stock head 45 colliding poses; A 48 (6 Twiglet-only: 5 at neck 65 + head_pitch −45, 1 where A's long right fringe tip brushes the body top at yaw +90 / neck 30, 44 mm³, so limit yaw to about ±80° or trim that tip); B 48 (5 Twiglet-only, all at neck 65 + head_pitch −45). Rest pose: no interference for either.

## Known mismatches (honest)
**Variant A**
- The flat neck-opening underside shows in low views.
- The fringe is fewer, chunkier printed spikes, not felt strands. The real look needs felt or dry-brushing.
- The eye bezels are a clean printed disc, not the photo's glossy dome.

**Variant B**
- The game hair is darker olive with dark streaks and covers more of the crown and sides. B's 13 blades stop at the hat line and read brighter; paint the roots olive.
- The game head is a taller egg with no flat underside.
- The game eyes glow inside a black mask area. B's dark socket rim is only ≈4 mm.
- The game snout rim is a lighter tan-green. Print it in a lighter filament if you want that.

**Both**
- The head is ≈100–120 g heavier than the stock printed head.
- The ghost hat is a placeholder only.
