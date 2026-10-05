# Twiglet head A v3: digital eyes

This is head A v2 (`../head-v2/`, unchanged) with the printed eye cups, orange rings and LED holes replaced by **two 2.1" round 480×480 IPS screens**. The screens show orange pixel-art eyes on black, sit flat behind round black-rimmed openings, and switch instantly between expressions.

Everything that isn't eye-related is head A v2, rebuilt from `scripts/parts_head2_base.py` (a verbatim copy of `head-v2/parts_head2.py`):
- the 170 mm wood ball and split plane
- the snout
- the fringe
- the chin collar
- the ODM neck / roll mount interface
- the hat anchors (groove, magnets, stitch holes)
- the fringe pegs

![front](renders/head_front_ring.png)

## 1. Display choice

| | **Primary: Waveshare ESP32-S3-Touch-LCD-2.1** (flat, SKU 28169) | Backup: Waveshare ESP32-S3-(Touch-)LCD-1.85 |
|---|---|---|
| Panel | 2.1" round IPS, 480×480, ST7701S (16-bit RGB), CST820 touch (unused) | 1.85" round IPS, 360×360, ST77916 (QSPI) |
| Controller | ESP32-S3R8 on the back: 8 MB PSRAM, 16 MB flash, CH343 USB-UART | ESP32-S3R8, 8 MB PSRAM, 16 MB flash |
| Visible (active) area | **Ø53.9 mm** | ~Ø46 mm |
| Outline | Ø75.0 cover glass (0.7 mm), PCB 66.0 × 64.2 × 1.6 | ~55 × 55 mm |
| Depth | 9.5 mm from the glass front to the back of the standoffs (glass + LCD 3.4) | ~11 mm |
| Mounting | 4× M2 threaded standoffs on the back, Ø65 PCD, at (±29.5, +13.6) and (±18.0, −27.1) | 4× M2 |
| Connectors | 12-pin SH1.0 header at (+21.8, +21.8), 45°. 2× USB-C at (±23.6, −22.4), plugs pointing out along the 45° diagonals. TF slot. | SH1.0 UART/I2C, USB-C |
| Price | **US$32.99** each (US$31.79 for 1–9) at [Waveshare](https://www.waveshare.com/esp32-s3-touch-lcd-2.1.htm?sku=28169). **AU:** [Zaitronics](https://zaitronics.com.au/products/esp32-s3-development-board-with-2-1-round-capacitive-touch-display) US$42 (≈AU$63), 5–10 days. SpotPear US$39.90. Amazon AU B0DDPQSKJD was unavailable. Core Electronics doesn't stock it. | ~US$30–36 at [Waveshare](https://www.waveshare.com/esp32-s3-touch-lcd-1.85.htm) |
| Mass | not published; **~40 g estimated** from the STEP (glass + LCD + PCB) | ~25 g est. |

Dimensions come from Waveshare's drawing and STEP file (copies are in `ref/`) and the [wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-2.1).
- Do **not** buy the "2.1B": it has 2.5D curved glass.
- The backup would shrink the eye opening to ~46 mm. Its CAD is not done.

### Why this one
- **Look.** The video's orange pixel look is just pixel art. A 480×480 panel draws it with 12 px "LED dots" (1.35 mm pitch, 40×40 grid, 1 px rounded corners, 2 px black gaps). That matches the fine dot grid in the target photo far better than an 8×8 matrix, and it can show hearts, ^ ^, angry lids and blinks.
- **Size.** Ø53.9 mm active area against the photo-matched 58 mm opening. The 1.85" option would leave a 46 mm window.
- **Controller.** The ST7701 needs a 16-bit parallel RGB bus that the Pi Zero's SPI can't drive. Each board has its own ESP32-S3 on the back, so no separate eye controller is needed. The Pi sends short text commands over one UART line.
- **Tooling.** The official demo is Arduino IDE (esp32 core ≥ 3.0).

### Rejected
- **8×8 MAX7219 60 mm matrices** (~US$2–19): 8×8 is far too coarse for a ring, and a square module doesn't suit a round hole.
- **16×16 WS2812:** 160 mm, way too big.
- **GC9A01 1.28":** too small (Ø32 mm).
- **Round OLEDs:** ≤1.5".
- **Pi-driven SPI TFTs:** the Pi Zero would have to push both eyes, with no 2" round SPI option at this size.

## 2. Head changes (v2 → v3)

**Removed**
- `eye_cup_L/R` and `eye_ring_L/R`.
- The 6 LED holes.

**Kept**
- The v2 eye position: az ±32°, el 19.5°.
- The 67 mm black disc silhouette, so the fringe and photo match are unchanged.

**New parts**

| Part | What it is |
|---|---|
| `eye_bezel_L/R` (black PLA) | The visible black ring: 67 mm OD, flat face, 0.8 mm proud, same outline as v2's eye disc. **Round aperture Ø58 mm at the face**, 1 mm 45° chamfer to Ø56. Its back stops 0.3 mm in front of the cover glass (optional 0.3–0.5 mm black foam ring). Glued into `head_upper`. |
| `display_carrier_L/R` (PETG/PLA) | A ring behind the display's standoffs, with 4× M2 clearance holes and Ø4.4 × 1.5 counterbores. Has a notch for the 12-pin header and reliefs for USB-C plugs. A strut runs back to a foot plate that screws with **2× M3 down into two new posts on `head_lower`'s deck** (M3 heat-set inserts Ø4 × 6). Also has zip-tie slots and driver access holes for the M2 screws. |

**Where the screen sits**
- The screen is recessed **≈4.6 mm** behind the bezel face at the eye centre: 3.1 mm at the nearest rim point, 6.1 mm at the farthest.
- **That's deeper than the 2–4 mm asked for.** The limits are:
  - the Ø75 cover glass has to fit inside the 85 mm-radius, 3 mm-thick ball wall, with ≥1 mm of wood over the glass rim;
  - to clear the stock roll-mount bosses, the Pi Zero (L) and the snout spigot (R), the module axis sits at **az ±30°, el 21.5°**. That puts it **3.6 mm up/inward** of the eye's visual axis (hidden behind the bezel).
- The panel is tilted 0.7° so it can lift straight out without shaving the thin wood at the seam.
- The eye opening and its position are exactly as in v2.
- **Consequence:** the aperture isn't concentric with the active area. A thin crescent of the black non-active glass border shows on the lower-outer side (black on black, hardly visible).
  - The firmware centres the graphics on the aperture using a per-eye pixel offset.
  - The graphics are clipped to a 23 mm radius, so they never fall outside the active area.
- **Display rotation:** L is 90° and R is 180° in the CAD, so the 12-pin header points down/inward on both. The firmware compensates.

**Modified parts**

| Part | Change |
|---|---|
| `head_upper` (dome) | Holds the bezels. Has straight-up clearance cuts so it lifts off over the display pods. |
| `head_lower` | Two M3 posts per eye on the deck. Sockets for the glass and board, with straight-up clearance so each pod lifts out. A cable exit at the header. |
| `snout` | The internal spigot is trimmed where the R display sits. There's a 0.3 mm relief under the R bezel. The outside is unchanged. |

Unchanged: the fringe, chin collars, neck mount, hat anchors, roll bosses and Pi mounting.

**Checks** (`check_report.json`, `scripts/check_head3.py`, on the final grained build)

| Check | Result |
|---|---|
| Rest-pose interference: displays, carriers and bezels vs every head part and every ODM head-assembly part (Pi Zero, roll mount, servo, bearing…) | **0** |
| Display L to Pi Zero | min gap **0.6 mm** (tight; see caveats) |
| Dome lift, dome + fringe + bezels raised 0–80 mm | **0** |
| Pod service path (each pod lifted straight up 0–90 mm with the dome off) | **0** (0.04 mm³ at 1 mm on R, which is numerical noise) |
| Outer 0.8 mm skin compared with v2 | no new holes (one 0.9 mm³ seam sliver at (68, 69, 234), cosmetic; v2 had a similar 0.65 mm³ one) |
| All 10 printed parts watertight, single body, fit the P1S bed | **yes** (`build_report.json`) |

## 3. Mass

| | v2 | v3 |
|---|---|---|
| Printed head parts | 405 g (incl. eye cups 2×20 g + rings 2×4 g) | **382 g** (bezels 2×3 g, carriers 2×11 g) |
| Displays | 6 LEDs (~2 g) | **2 × ~40 g** (estimated) |
| Head assembly (servo, Pi, hat…) | 583 g | **≈653 g (+70 g)** |
| Worst neck_pitch moment | 0.96 N·m (50 % of STS3215 stall) | **1.08 N·m (56 %)** |
| Worst head_pitch | 0.53 N·m (28 %) | 0.61 N·m (32 %) |

The v3 numbers come from `torque_report.json`, using the same model as `head-v2/fit/torque.py`.

## 4. BOM additions

| Qty | Item | ≈Price |
|---|---|---|
| 2 | Waveshare **ESP32-S3-Touch-LCD-2.1** (flat, SKU 28169) | US$66 (Waveshare), or ≈AU$126 from Zaitronics |
| 8 | M2 × 5 pan/button-head screws (display to carrier) | <AU$3 |
| 4 | M3 × 8 socket-head screws + 4 M3 heat-set inserts (M3 × 4 × 5, Ø4 hole) | ~AU$3 |
| 2 | SH1.0 (JST-SH-compatible) 12-pin cable, ~150 mm. Check the box first; you only use 4 wires (GND, 5V, RX, TX), plus TX on the L board. | ~AU$5 |
| 1 | 4-pin inline connector (JST-XH/PH or DuPont) + ~30 cm of 26 AWG wire, to reach the Pi near the deck | ~AU$3 |
| opt | 0.3–0.5 mm black foam tape ring (75 mm OD / 56 mm ID) between the bezel and glass | ~AU$3 |
| — | Black PLA (bezels, ~6 g) + PETG/PLA (carriers, ~22 g) | — |

**Power:** each board takes 5 V on header pin 2 (VBus). Expect ~0.15–0.25 A each with orange-on-black at 80 % backlight (**not measured**). Budget 0.5 A total on the head's 5 V rail and check the ODM 5 V converter has the headroom alongside the Pi.

## 5. Wiring (Pi Zero 2W ↔ eyes)

```
Pi pin 8  GPIO14 TXD ──┬──> L board 12-pin #10 RXD (GPIO44)
                       └──> R board 12-pin #10 RXD (GPIO44)
Pi pin 10 GPIO15 RXD <──── L board 12-pin #9  TXD (GPIO43)     (R board TXD not connected)
Pi pin 6  GND ─────────── both boards pin #1 (or #5) GND
5 V rail ──────────────── both boards pin #2 VBus 5 V
```

**12-pin header**

| Pin | Signal |
|---|---|
| 1 | GND |
| 2 | VBus 5 V |
| 3 | D− / GPIO19 |
| 4 | D+ / GPIO20 |
| 5 | GND |
| 6 | 3V3 |
| 7 | SCL GPIO7 |
| 8 | SDA GPIO15 |
| 9 | TXD GPIO43 |
| 10 | RXD GPIO44 |
| 11 | NC |
| 12 | GPIO0 |

- **Pi setup:**
  - `raspi-config` → Serial: login shell **no**, hardware **yes**.
  - Add `dtoverlay=disable-bt` to `/boot/firmware/config.txt` so `/dev/serial0` is the PL011.
  - The ODM's servo bus runs over USB, so the GPIO UART is free.
  - The helper is `firmware/pi_eyes.py` (pyserial).
- **UART sharing:** GPIO43/44 are also wired to the board's "UART" USB-C port (CH343 through a mux). Unplug that USB-C when the Pi is driving the eyes.
- **Cable route:** the 12-pin header points down/inward through the carrier notch and the cable exit in `head_lower`. Run the cable along the deck to the Pi and zip-tie it through the carrier slots. Put the inline connector near the deck.

## 6. Firmware (`firmware/TwigletEyes/`)

`TwigletEyes.ino`, `st7701_panel.cpp/.h`, `eye_bitmaps.h` (generated by `scripts/eyes_art.py`) and `eye_geometry.h`. Both boards run the same sketch.

**Arduino IDE settings**
- Board: ESP32S3 Dev Module (esp32 core ≥ 3.0; tested to **compile** on 3.3.12)
- PSRAM: **OPI PSRAM**
- Flash: 16 MB; partition "16M Flash (3MB APP/9.9MB FATFS)"
- USB CDC On Boot: **Disabled**, so `Serial` is UART0 on the header and the UART USB-C
- Flash through the "UART" USB-C.

**Protocol:** 115200 8N1, one command per line, case-insensitive. Add `L:` or `R:` in front to address one eye.

| Command | Effect |
|---|---|
| `EYE ring` | default: thick orange ring, dark pupil, auto-blink |
| `EYE heart` | beating pixel heart |
| `EYE happy` | ^ ^ arch |
| `EYE angry` | ring with a lid slanted down toward the nose; mirrored per eye |
| `EYE wide` | surprised |
| `EYE blink` / `BLINK` | one blink: 7 frames × 55 ms |
| `EYE off` | backlight off |
| `EYE test` | calibration pattern |
| `LOOK x y` | x, y from −1 to 1. +x is toward the robot's own left, +y is up. Moves ±4 / ±3.5 dots. |
| `AUTOBLINK 0/1`, `BRIGHT 0..100`, `COLOR ff7a00` | settings |
| `SIDE L/R`, `ROT 0..3`, `MIRROR 0/1`, `CENTER x y`, `SAVE`, `INFO`, `PING`, `ECHO 0/1` | setup and diagnostics |

- Only the L board replies (`OK …`), because only its TX is wired back.
- Settings are saved to NVS with `SAVE`.
- Wi-Fi and BT are off.
- The ST7701 init sequence, pins and timings are ported from Waveshare's official demo.

**First-time setup per board**
1. Flash the sketch.
2. `SIDE L` (or `R`), then `SAVE`.
3. Install the board, send `EYE test`, and look through the opening:
   - The arrow must point up and the green dot must be on the viewer's right.
   - If it's wrong, adjust `ROT` / `MIRROR`.
   - Adjust `CENTER x y` until the grey circle sits concentric with the bezel.
4. `SAVE`.

The defaults in `eye_geometry.h` come from the CAD: L centre (218, 217), rot 2; R centre (263, 262), rot 3. **The panel's native scan orientation isn't documented, so treat these defaults as a starting point.**

## 7. Eye art (`eyes-art/`)

- `frames/*.png`: 480×480, as seen from the front, centred on the aperture.
  - Frames: ring, look_left/right/up/down, blink_0…6, happy, angry_L/angry_R (mirrored), heart, heart_small, wide.
  - Grid: 40 × 40 dots at a 12 px (1.35 mm) pitch.
  - Ring: OD 27 dots (36.7 mm, ~0.55 of the 67 mm eye disc, as in the photo); pupil 13 dots (17 mm).
  - Colour: #FF7A00 on pure black.
- `contact_sheet.png` shows all frames with the 56 mm aperture outline.
- `preview.gif` is a sequence on both eyes: ring → blink → look L/R → happy → angry → beating heart → wide → blink.
- The firmware uses the same bitmaps (`eye_bitmaps.h`), so the PNGs match what's drawn on the screen.

## 8. Assembly

1. Press the M3 inserts into the 4 deck posts on `head_lower` (the display posts).
2. Mount each display to its carrier with 4× M2 × 5 through the carrier ring into the board's standoffs. The carrier notch goes over the 12-pin header.
3. Plug in the 12-pin cable.
4. Drop each pod straight down into `head_lower`. The glass sits in its socket and the foot plate on the two posts. Fit 2× M3 × 8 from above.
5. Route the cables to the Pi along the deck. Zip-tie them through the carrier slots.
6. Glue the black bezels into `head_upper`'s eye openings (CA or epoxy): flat face out, flush 0.8 mm proud like v2. The optional foam ring goes on the bezel's back.
7. Fit the dome as in v2. It lowers straight down over the pods.

**Service:** remove the dome as in v2 (it lifts straight up with the bezels and fringe). Undo 2× M3, lift the pod straight out, and undo 4× M2 on the bench.

## 9. Print settings (Bambu P1S, 0.4 nozzle)

| Part | Material | Orientation | Supports |
|---|---|---|---|
| head_upper, head_lower, snout, fringe, collars | as in v2 (0.2 mm, 3 walls, 15 % gyroid) | as in v2 | as in v2. head_lower also needs "build plate only" tree supports under the display-post undersides. |
| eye_bezel_L/R | matte black PLA, 0.12–0.16 mm layers, 3 walls, 100 % | visible flat face down (smooth PEI gives a clean face) | none |
| display_carrier_L/R | PETG (or PLA), 0.2 mm, 4 walls, 40 % | ring front face (display side) down | tree supports under the foot plate |

## 10. Files

- `stl/twiglet_head_v3_*.stl`: 10 print-oriented parts.
- `build_report.json`: per-part size, mass, watertight, bed fit, colour, orientation.
- `check_report.json`: interference, dome-lift and pod-lift checks.
- `torque_report.json`
- `renders/`:
  - `head_front_ring.png`, `head_three_quarter_ring.png`, `head_front_ring_ghosthat.png`
  - `head_three_quarter_heart.png`, `head_three_quarter_happy.png`, `head_front_angry.png`
  - `compare_side_by_side_photo.png`
  - `exploded_eye_stack.png`, `section_L_eye.png`, `pod_rear_L.png`
  - `head_open_service.png`, `parts_sheet.png`
- `eyes-art/`: frames, contact sheet, GIF.
- `firmware/`:
  - `TwigletEyes/` Arduino sketch
  - `compile_log.txt`
  - `pi_eyes.py`
- `scripts/`:
  - `parts_head3.py` (model; run `python parts_head3.py --nograin` for a fast build)
  - `export_head3.py`, `check_head3.py`, `torque_head3.py`, `render_head3.py` (run with `xvfb-run -a`), `eyes_art.py`
  - `display_model.py` (Waveshare STEP geometry)
  - `parts_head2_base.py` / `render_head2_base.py` (copies of v2)
  - `dev/`: exploration scripts. They were written for the `scripts/` folder, so fix their paths before running them.
- `ref/`: Waveshare dimension drawing (PDF/PNG), tessellated STEP bodies, target photo crop.

**Env:** `$VENV` (trimesh + manifold3d + pyvista). The repo root must be on `sys.path`; the scripts handle this.

## 11. Not tested / caveats

- **No hardware yet.**
  - The firmware compiles, but it hasn't run on a board.
  - The panel's native orientation and exact centre offsets need calibrating with `EYE test`.
  - The mass (40 g per display) and current draw are estimates.
- **L display to Pi Zero:** 0.6 mm at the nearest point, which is tight. Check it on the first fit. If it rubs, the Pi can sit 1–2 mm lower on its standoffs, or `MOD_EL` can go up 0.5°.
- **Recess** is 3.1–6.1 mm (4.6 mm at the centre), against the 2–4 mm requested. A thin black glass-border crescent is visible at the lower-outer part of each opening (black on black).
- The Waveshare STEP is simplified: small parts are modelled as convex hulls grown by 0.4 mm. The **USB-C plug overmolds** are only relieved 0.8 mm into the carrier, so use the UART USB-C with the pod lifted out.
- Only the external surface is shared with v2, so the neck range-of-motion checks from v2 still apply. The eye changes are all inside the ball.
