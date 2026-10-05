"""Pixel-art eye expressions for the 480x480 round displays.
Art frame = what the viewer sees: 40x40 'LED' cells of 12 px (1.35 mm) centred on the eye APERTURE, up = world up, x = viewer's right.
Outputs: ../eyes-art/frames/*.png (480x480), contact_sheet.png, preview.gif, and ../firmware/TwigletEyes/eye_bitmaps.h (same bitmaps)."""
import os, math, numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "eyes-art"); FW = os.path.join(os.path.dirname(HERE), "firmware", "TwigletEyes")
N, CELL, DOT = 40, 12, 10                  # 40x40 cells, 12 px pitch, 10 px dot (2 px dark gap -> dot-matrix look)
ORANGE = (255, 122, 0); BG = (0, 0, 0)
R_OUT, R_IN = 13.6, 6.4                    # ring: ~36.7 mm OD, ~17 mm pupil (photo: ring OD ~0.55 x the 67 mm eye disc)
VIS_R = 17.0                               # cells: visible aperture radius (56 mm / 2 / 1.35 = 20.7), minus the 4.1 mm panel offset margin
c = (np.arange(N) - (N - 1) / 2.0)         # cell centres, in cells from the aperture centre
X, Y = np.meshgrid(c, -c)                  # row 0 = top
RR = np.hypot(X, Y)
def ring(dx=0.0, dy=0.0, ro=R_OUT, ri=R_IN):
    r = np.hypot(X - dx, Y - dy); return (r <= ro) & (r >= ri)
def lids(img, top, bot):
    """blink: keep rows between the lids (top/bot in cells from the centre)."""
    m = img & (Y <= top) & (Y >= bot)
    return m
def closed():
    return (np.abs(Y + 0.0) <= 1.5) & (np.abs(X) <= R_OUT - 0.5)   # 3-cell thick closed-lid line
def happy():
    r = np.hypot(X, Y + 5.0)                                    # ^ : bold upper arch (closed happy eye)
    return (r <= R_OUT + 0.4) & (r >= R_OUT - 5.0) & (Y + 5.0 >= 1.5)
def angry(side):
    """ring clipped by a lid that slants DOWN towards the nose, plus a 2-cell brow edge (Twiglet glare). side L = robot's left eye (viewer's right)."""
    inner = -X if side == "L" else X                           # L eye: nose is on the viewer's left (-x)
    lid = 5.0 - 0.55 * inner                                   # lid line height (cells), lower at the nose side
    base = ring(0, -1.0, R_OUT - 0.4, R_IN - 0.6) & (Y <= lid - 1.0)
    brow = (Y > lid - 1.0) & (Y <= lid + 1.5) & (np.hypot(X, Y + 1.0) <= R_OUT + 0.6)
    return base | brow
def heart(scale=1.0, dy=0.0):
    x = X / (12.5 * scale); y = (Y - dy) / (12.5 * scale) + 0.12
    return (x * x + (y - np.sqrt(np.abs(x)) * 0.9) ** 2) <= 1.0
def wide():
    return ring(0, 0, R_OUT + 1.5, R_IN - 2.5)
def clipvis(m): return m & (RR <= VIS_R)
def render(m, glow=False, aperture=True):
    im = Image.new("RGB", (480, 480), BG); d = ImageDraw.Draw(im)
    for i in range(N):
        for j in range(N):
            if m[i, j]:
                x0 = j * CELL + 1; y0 = i * CELL + 1
                d.rounded_rectangle([x0, y0, x0 + DOT - 1, y0 + DOT - 1], radius=2, fill=ORANGE)
    return im
FR = {}
FR["ring"] = ring()
FR["look_left"] = ring(-4.0, 0); FR["look_right"] = ring(4.0, 0); FR["look_up"] = ring(0, 3.5); FR["look_down"] = ring(0, -3.5)
for k, (t, b) in enumerate([(99, -99), (8, -11), (3, -6), (None, None), (3, -6), (8, -11), (99, -99)]):
    FR[f"blink_{k}"] = closed() if t is None else lids(ring(), t, b)
FR["happy"] = happy(); FR["angry_L"] = angry("L"); FR["angry_R"] = angry("R"); FR["heart"] = heart(); FR["heart_small"] = heart(0.8, -0.5); FR["wide"] = wide()
FR = {k: clipvis(v) for k, v in FR.items()}
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
for k, m in FR.items(): render(m).save(os.path.join(OUT, "frames", f"{k}.png"))
# contact sheet with the aperture outline
font = ImageFont.load_default()
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except Exception: pass
keys = list(FR); cols = 6; th = 240; rows = math.ceil(len(keys) / cols)
sheet = Image.new("RGB", (cols * (th + 20) + 20, rows * (th + 50) + 70), (30, 22, 14)); ds = ImageDraw.Draw(sheet)
ds.text((20, 18), "Twiglet digital eyes - 480x480 frames (art frame: centred on the aperture, as seen from the front). Grey circle = 56 mm aperture.", fill=(230, 230, 230), font=font)
for n, k in enumerate(keys):
    im = render(FR[k]); dd = ImageDraw.Draw(im); ra = 28.0 / 1.35 * CELL / 1.0 / 1.0
    dd.ellipse([240 - ra * 12 / CELL, 240 - ra * 12 / CELL, 240 + ra * 12 / CELL, 240 + ra * 12 / CELL], outline=(90, 90, 90), width=3)
    x = 20 + (n % cols) * (th + 20); y = 60 + (n // cols) * (th + 50)
    sheet.paste(im.resize((th, th), Image.LANCZOS), (x, y)); ds.text((x, y + th + 6), k, fill=(255, 190, 120), font=font)
sheet.save(os.path.join(OUT, "contact_sheet.png"))
# GIF: both eyes as seen from the front (robot's R eye on the viewer's left)
def pair(kl, kr, sz=240):
    im = Image.new("RGB", (2 * sz + 60, sz + 20), (60, 38, 20)); d = ImageDraw.Draw(im)
    for n, k in enumerate((kr, kl)):
        e = render(FR[k]).resize((sz, sz), Image.NEAREST); mask = Image.new("L", (sz, sz), 0); ImageDraw.Draw(mask).ellipse([4, 4, sz - 4, sz - 4], fill=255)
        x = 20 + n * (sz + 20); d.ellipse([x - 6, 4, x + sz + 6, sz + 16], fill=(10, 10, 10)); im.paste(e, (x, 10), mask)
    return im
seq = [("ring", "ring", 900)] + [(f"blink_{k}", f"blink_{k}", 60) for k in range(7)] + [("ring", "ring", 500), ("look_left", "look_left", 700), ("look_right", "look_right", 700),
       ("ring", "ring", 400), ("happy", "happy", 1000), ("angry_L", "angry_R", 1000), ("ring", "ring", 300), ("heart", "heart", 350), ("heart_small", "heart_small", 250),
       ("heart", "heart", 350), ("heart_small", "heart_small", 250), ("heart", "heart", 700), ("wide", "wide", 500)] + [(f"blink_{k}", f"blink_{k}", 60) for k in range(7)]
frames = [pair(a, b) for a, b, t in seq]
frames[0].save(os.path.join(OUT, "preview.gif"), save_all=True, append_images=frames[1:], duration=[t for a, b, t in seq], loop=0)
# firmware header: 40x40 bitmaps, row-major, MSB first, 5 bytes per row
names = ["ring", "happy", "angry_L", "angry_R", "heart", "heart_small", "wide"]
with open(os.path.join(FW, "eye_bitmaps.h"), "w") as f:
    f.write("// generated by scripts/eyes_art.py - 40x40 cells (12 px), art frame (viewer's view, up = up), centred on the aperture\n#pragma once\n#include <stdint.h>\n")
    f.write(f"#define EYE_N {N}\n#define EYE_CELL {CELL}\n#define EYE_DOT {DOT}\n#define EYE_R_OUT {R_OUT}f\n#define EYE_R_IN {R_IN}f\n#define EYE_VIS_R {VIS_R}f\n")
    for nm in names:
        b = np.packbits(FR[nm].astype(np.uint8), axis=1)
        f.write(f"static const uint8_t BMP_{nm.upper()}[{N}][{N // 8}] = {{\n" + ",\n".join("  {" + ",".join(f"0x{v:02X}" for v in row) + "}" for row in b) + "\n};\n")
print("frames", len(FR), "->", OUT)
