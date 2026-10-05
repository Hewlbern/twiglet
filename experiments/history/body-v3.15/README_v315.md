# body-v3.15: one-piece chunky wig with a smooth crown, plus photo-matched eye facets and ring bezels

## Crown indentation (v3.14): cause and fix
- **Cause:** the v3.14 crown was a thin 2 mm cap (theta 0-26 deg) sitting 8-9 mm below the 10 mm clump roots that started on it. That made a crater ringed by root ridges, with V-grooves over the top. The 3 pin bosses stood up out of the cap floor.
- **Fix:** a solid crown dome 12 mm above the seat out to 30 deg, then a convex falloff to a feather edge at 52 deg. The clumps now root at 24 deg or more, under the dome edge. The pins go into blind 6.5 mm holes from the seat side, with no bosses.
- **Check:** outer-crown ray grid (3077 points, theta < 32 deg). Max dip 0.19 mm (sub-layer), p99 0.013 mm, 0 dips over 0.3 mm. The dome sits 11.9-12.2 mm above the seat.

## Chunkier hair (measured on the photo, eye spacing 105 mm used as scale)
- **Photo:** clumps about 35-50 mm wide and 11-14 mm thick, about 15 around the head (7 across the forehead).
- **Before (v3.14):** 17 clumps / 45 strands.
- **Now (v3.15):** 14 clumps / 25 strands, 38-54 mm wide and 13-14 mm thick. Each clump is either one fat strand or two strands with a deep centre V fold. Roots swell from 72% to 100% thickness.

## Eyes
- **Facet:** flat facet plane (a = 95.11) out to rho 40, with a cone blend to rho 48. It is recessed 2.86 mm at the bezel edge.
- **Backing and bore:** a 2.6 mm backing ring sits behind the facet. Bore is 36.3 mm radius.
- **Grain rings:** 4 grain rings re-engraved around each eye.
- **Bezel:** black, 74.4 mm eye disc (was an 88 mm flange), 6.2 mm ring face, 62 mm window, 4.6 mm spigot. The screen sits about 12 mm behind the ring front.
- **Unchanged:** carriers, screens and mounts. Overlaps are 0.
- **Near the snout:** the facet cut stops at snout hull x1.30, and the socket is untouched.
- **Walls:** 2.0-2.1 mm or more (p5) on the facets.
  - The only readings under 1.25 mm are rays that exit through the split face at the split plane.
  - Other low readings come from the snout-socket rim, which reads identically on v3.14.

## Results (see sim/compare_v314_v315.md, collide_head_v315.json, head_print_report_v315.json)
- **Wig:** sim 198.9 g, but the moment about the neck axis is 1734 g·mm (v3.14: 2458), because the mass sits toward the back.
- **Neck load:** static head pitch 0.214 N·m = 2.29x margin.
- **Eye cover:** L 8.8% / R 16.9%.
- **Gaits:**
  - max-speed 100% at 0.178 m/s;
  - energy-aware 100% at 0.147 m/s, after re-tuning (it was 90% before walk_refine).
- **Head+arm:** did not fall; margin 17.9 mm (trend 34.9 → 26.6 → 17.9 mm), peak head pitch 0.825.
- **Collisions:**
  - rest 0; ranges the same as v3.14;
  - arm sweep 49 / 57 / 62, of which hair 0 / 19 / 6 (v3.14: 0 / 20 / 20).
