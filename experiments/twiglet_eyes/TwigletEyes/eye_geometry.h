// Per-eye mapping from the art frame (viewer's view, up = up, centred on the head's eye APERTURE) to panel pixels.
// Computed from the head v3 CAD (scripts/parts_head3.py): the panel sits 4.1 mm up/inward of the aperture axis
// (+0.7 deg tilt), and is mounted rotated so its 12-pin header points down/inward. Aperture centre on the glass, in
// panel pixels, ASSUMING the panel's native row 0 is along the board's top edge (+Y in the Waveshare drawing) and
// column 0 on its left (seen from the front). That native scan orientation is NOT verified: run `TEST` once per eye,
// then fix with `ROT n`, `MIRROR 0|1`, `CENTER x y` and `SAVE` (stored in NVS).
#pragma once
//                      L eye (robot's left)     R eye (robot's right)
#define GEO_L_CX 218
#define GEO_L_CY 217
#define GEO_L_ROT 2        // art rotated 180 deg on the panel (world-up = panel native +y)
#define GEO_R_CX 263
#define GEO_R_CY 262
#define GEO_R_ROT 3        // art rotated 270 deg clockwise (world-up = panel native -x)
#ifndef DEFAULT_SIDE
#define DEFAULT_SIDE 'L'   // or build with -DDEFAULT_SIDE='R'; can also be set at runtime with `SIDE R` + `SAVE`
#endif
