# Twiglet kilt v3.16 - printed green kilt (replaces the fabric kilt)

Parts: kilt_band (reprint of hip_ring with a rolled rim on top) + 10 hinged leaf petals. Mass: petals 59.9 g + band 9.5 g = 69.4 g.

| file | size (mm) | g | >45 deg overhang (cm2) |
|---|---|---|---|
| v316_kilt_band.stl | 118.3 x 110.7 x 11.0 | 9.5 | 4.2 |
| v316_kilt_petal_00.stl | 49.0 x 57.7 x 87.9 | 6.6 | 0.0 |
| v316_kilt_petal_01.stl | 32.2 x 62.4 x 87.9 | 6.3 | 0.0 |
| v316_kilt_petal_02.stl | 49.0 x 57.6 x 87.9 | 6.6 | 0.0 |
| v316_kilt_petal_03.stl | 52.6 x 37.4 x 87.9 | 5.6 | 0.0 |
| v316_kilt_petal_04.stl | 53.6 x 47.2 x 87.9 | 5.7 | 0.0 |
| v316_kilt_petal_05.stl | 45.2 x 54.1 x 87.9 | 6.0 | 0.0 |
| v316_kilt_petal_06.stl | 32.3 x 55.9 x 87.9 | 5.8 | 0.0 |
| v316_kilt_petal_07.stl | 45.2 x 54.1 x 87.9 | 6.0 | 0.0 |
| v316_kilt_petal_08.stl | 53.6 x 46.9 x 87.9 | 5.7 | 0.0 |
| v316_kilt_petal_09.stl | 52.6 x 37.4 x 87.9 | 5.6 | 0.0 |

## Print (Bambu P1S, green matte PLA)
- Petals: as exported = UPSIDE DOWN, the top lip flat on the bed, hem points up. The flare is <= 36 deg from vertical, so NO supports. 0.2 mm layers, 3 walls (the 1.2 mm petal is all perimeters), 0 % infill needed, brim 3 mm. All 10 fit on one plate (~2.5-3 h).
- kilt_band: as exported = upside down (rolled rim on the bed), no supports, 0.2 mm, 3 walls, 20 % infill (~1 h).
- Felt look: matte green PLA (or 'silk-matte' moss); optional light sanding / flocking spray on the outer faces.
- TPU option: print the same petal STLs in 95A TPU (2 walls, 20 mm/s): then they flex instead of swinging and can be glued straight onto the rim.

## Assembly
- Replace the hip ring with kilt_band (same fit, same 14 holes/groove).
- Hook each petal's top lip over the rolled rim (petal 00-02 = front arc, 03-09 = back arc, numbered anticlockwise from the robot's right front seen from above). The lip is the hinge: petals swing OUT freely (a leg or hand pushing from inside lifts them) but rest against the rim so they cannot swing IN onto the legs.
- Optional retention: a 1.75 mm filament ring threaded through the lips, or a dab of E6000 on one lip corner (keeps the hinge free).
- Power switch / USB-C charger (back-left / back): lift the back petals (they swing up on the rim) - no tools; the rim leaves the charger notch free.
- Arm slots: the elbows rest against the hip ring, so there are no petals at |az| 46-93 deg each side (covered by the arms in normal poses).

## Clearance checks (kilt fixed at rest = worst case; contacts from the legs only push petals outward)
- Sim gaits (max-speed + energy-aware, nominal + 2 randomized each, 10 s, 1500 poses): leg contacts 0, arm contacts 0.
- Single-leg stance (weight shift) 14 poses: 0 contacts.
- collide_v3 gait sets: single-leg 7/120, both-legs 1/120, arms+legs 1/80 leg contacts (foot vs a front petal at extreme knee+thigh, pushes it out = swings), arm contacts 0.
- Full joint ranges (contact = petal swings out): left_hip_roll [-25.0, -17.0]; left_hip_pitch [-70.0, -70.0]; left_knee [90.0, 90.0]; right_hip_roll [15.0, 23.0]; right_hip_pitch [70.0, 70.0]; right_knee [-90.0, 90.0]; shoulder_L [-56.0, -16.0]; elbow_L [-20.0, -16.0]; shoulder_R [-56.0, -16.0]; elbow_R [-20.0, -16.0]. Arm contacts only with the shoulder swung back past -16 deg or the elbow hyper-extended past -16 deg (both outside the -5 / 0 deg soft limits).
