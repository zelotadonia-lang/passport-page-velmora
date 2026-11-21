# Draws entry.png: an invented passport spread for the Republic of Velmora.
# Pure PIL (DejaVu / Liberation fonts). Run: python3 draw_entry.py
# Output: ../repo/entry.png  (1024x1024, PNG, <= 1 MiB)
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "repo")
OUT = os.path.join(REPO, "entry.png")

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

# ---- palette (ui-ux-pro-max: restrained document palette, one ink family) ----
INK = (38, 34, 28)          # near-black warm ink
INK_SOFT = (74, 68, 58)
GREY = (122, 114, 100)
PAPER = (247, 243, 231)     # cream passport paper
PAPER_R = (243, 238, 222)
BG = (34, 38, 44)           # dark desk surface
GOLD = (146, 110, 46)
BLUE = (28, 66, 120)
GREEN = (28, 92, 60)
PURPLE = (112, 38, 74)
RED = (150, 40, 32)

# ---- MRZ (ICAO 9303, check digits computed, not guessed) ----
def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)

def mrz_lines():
    name = "SOLEN<<ELIN<MAREK"
    l1 = ("P<VEL" + name).ljust(44, "<")
    doc = "VM4829137"
    dob = "940314"
    exp = "360601"
    pers = "<" * 14
    l2core = doc + mrz_check(doc) + "VEL" + dob + mrz_check(dob) + "F" + exp + mrz_check(exp) + pers + mrz_check(pers)
    l2 = l2core + mrz_check(l2core)
    assert len(l1) == 44 and len(l2) == 44, (len(l1), len(l2))
    return l1, l2

# ---- text helpers ----
def draw_spaced(d, xy, text, font, fill, spacing=0):
    """Draw text with extra letter spacing; returns width used."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing
    return x - xy[0] - spacing

def text_w(d, text, font, spacing=0):
    return sum(d.textlength(c, font=font) + spacing for c in text) - spacing

def center(d, cx, y, text, font, fill, spacing=0):
    w = text_w(d, text, font, spacing)
    draw_spaced(d, (cx - w / 2, y), text, font, fill, spacing)

def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

# ---- canvas: dark desk, open spread, gutter shadow ----
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
# subtle vertical gradient on the desk
for y in range(H):
    t = y / H
    shade = int(34 - 10 * t)
    d.line([(0, y), (W, y)], fill=(shade, shade + 4, shade + 9))
random.seed(20261121)

PAGE_Y0, PAGE_Y1 = 104, 904
LX0, LX1 = 40, 492
RX0, RX1 = 532, 984
PAGE_H = PAGE_Y1 - PAGE_Y0

def guilloche(dr, x0, y0, x1, y1, color, amp=3.0, step=7):
    for yy in range(y0, y1, step):
        pts = []
        for x in range(x0, x1 + 1, 6):
            pts.append((x, yy + amp * math.sin((x - x0) / 46.0 + yy / 31.0)))
        dr.line(pts, fill=color, width=1)
        pts = []
        for x in range(x0, x1 + 1, 6):
            pts.append((x, yy + amp * math.sin((x - x0) / 46.0 + yy / 31.0)))
        dr.line(pts, fill=color, width=1)

def paper_page(x0, x1, tint):
    pg = Image.new("RGB", (x1 - x0, PAGE_H), tint)
    pd = ImageDraw.Draw(pg)
    guilloche(pd, 8, 8, x1 - x0 - 8, PAGE_H - 8, (230, 224, 206), amp=2.0, step=13)
    # faint watermark: large lighthouse ghost, centre
    return pg

left = paper_page(LX0, LX1, PAPER)
right = paper_page(RX0, RX1, PAPER_R)
img.paste(left, (LX0, PAGE_Y0))
img.paste(right, (RX0, PAGE_Y0))
d = ImageDraw.Draw(img)
# page edge shadows + gutter
d.rectangle([LX0, PAGE_Y0, LX1, PAGE_Y1], outline=(20, 18, 14), width=2)
d.rectangle([RX0, PAGE_Y0, RX1, PAGE_Y1], outline=(20, 18, 14), width=2)
for i in range(18):
    a = int(60 * (1 - i / 18))
    d.line([(LX1 + 2 + i, PAGE_Y0), (LX1 + 2 + i, PAGE_Y1)], fill=(0, 0, 0, a) if False else (10, 10, 12))
    d.line([(RX0 - 3 - i, PAGE_Y0), (RX0 - 3 - i, PAGE_Y1)], fill=(10, 10, 12))
# re-draw pages' inner shadow near gutter
d.rectangle([LX1 - 3, PAGE_Y0, LX1, PAGE_Y1], fill=(214, 206, 188))
d.rectangle([RX0, PAGE_Y0, RX0 + 3, PAGE_Y1], fill=(210, 201, 182))
d = ImageDraw.Draw(img, "RGBA")

# ================= LEFT PAGE: DATA PAGE =================
LCX = (LX0 + LX1) // 2  # 266

def emblem(cx, cy, r, color):
    """Coat of arms: lighthouse on waves inside a double ring."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], outline=color, width=1)
    # waves
    for k, yy in enumerate((cy + r - 16, cy + r - 10)):
        pts = []
        for x in range(cx - r + 10, cx + r - 9, 4):
            pts.append((x, yy + 2.5 * math.sin((x - cx) / 7.0 + k)))
        d.line(pts, fill=color, width=1)
    # tower
    d.polygon([(cx - 7, cy + r - 18), (cx - 4, cy - r + 16), (cx + 4, cy - r + 16), (cx + 7, cy + r - 18)], fill=color)
    # lamp room + light beams
    d.rectangle([cx - 6, cy - r + 8, cx + 6, cy - r + 16], fill=color)
    d.polygon([(cx - 6, cy - r + 10), (cx - r + 8, cy - r + 2), (cx - r + 8, cy - r + 18)], outline=color)
    d.polygon([(cx + 6, cy - r + 10), (cx + r - 8, cy - r + 2), (cx + r - 8, cy - r + 18)], outline=color)
    d.ellipse([cx - 3, cy - r + 10, cx + 3, cy - r + 16], fill=PAPER)
    # stars flanking
    for sx in (cx - r - 16, cx + r + 16):
        d.text((sx - 4, cy - 7), "*", font=F(SERIF_B, 16), fill=color)

emblem(LCX, 152, 26, GOLD)
center(d, LCX, 186, "REPUBLIC OF VELMORA", F(SERIF_B, 24), INK, spacing=1)
center(d, LCX, 218, "PASSPORT", F(SERIF, 19), INK, spacing=9)
d.line([(LX0 + 28, 252), (LX1 - 28, 252)], fill=INK, width=1)
d.line([(LX0 + 28, 255), (LX1 - 28, 255)], fill=INK, width=1)

# Type / Code / Number row
def label_value(x, y, label, value, vfont):
    d.text((x, y), label, font=F(SANS, 8), fill=GREY)
    d.text((x, y + 11), value, font=vfont, fill=INK)

label_value(LX0 + 28, 268, "TYPE", "P", F(SERIF_B, 15))
label_value(LX0 + 132, 268, "CODE", "VEL", F(SERIF_B, 15))
label_value(LX0 + 236, 268, "PASSPORT No.", "VM4829137", F(SERIF_B, 15))
d.line([(LX0 + 28, 306), (LX1 - 28, 306)], fill=(170, 160, 140), width=1)

# ---- portrait (supersampled, drawn figure of a lighthouse keeper) ----
PW, PH = 170, 208
PX0, PY0 = LX0 + 28, 322
S = 2  # supersample
pw, ph = PW * S, PH * S
por = Image.new("RGB", (pw, ph), (198, 208, 214))
pd = ImageDraw.Draw(por)
# backdrop: soft vertical gradient + faint horizontal blind lines
for yy in range(ph):
    t = yy / ph
    pd.line([(0, yy), (pw, yy)], fill=(int(206 - 22 * t), int(214 - 20 * t), int(220 - 16 * t)))
for yy in range(0, ph, 14):
    pd.line([(0, yy), (pw, yy)], fill=(190, 198, 205), width=1)
skin = (216, 164, 128)
skin_sh = (196, 140, 104)
skin_hi = (230, 184, 150)
hair_c = (58, 40, 28)
jacket = (38, 52, 84)
jacket_d = (28, 40, 66)
shirt = (238, 234, 224)
cxp = pw // 2
# shoulders / jacket
pd.polygon([(30, ph), (110, 300), (150, 268), (190, 268), (230, 300), (310, ph)], fill=jacket)
pd.polygon([(110, 300), (150, 268), (170, 330), (150, 360), (110, 330)], fill=jacket_d)
pd.polygon([(230, 300), (190, 268), (170, 330), (190, 360), (230, 330)], fill=jacket_d)
pd.polygon([(150, 268), (190, 268), (178, 330), (162, 330)], fill=shirt)
pd.polygon([(150, 268), (170, 292), (162, 330), (150, 300)], fill=(222, 218, 208))
pd.polygon([(190, 268), (170, 292), (178, 330), (190, 300)], fill=(222, 218, 208))
# neck + collar shadow
pd.rectangle([152, 238, 188, 272], fill=skin_sh)
pd.rectangle([152, 238, 188, 250], fill=skin)
# hair bun behind head (top centre-back)
pd.ellipse([148, 56, 194, 104], fill=hair_c)
# head
pd.ellipse([118, 92, 222, 252], fill=skin)
# ears
pd.ellipse([112, 168, 126, 198], fill=skin)
pd.ellipse([214, 168, 228, 198], fill=skin)
# hair: cap with a lower hairline, plus side strands to the jaw
pd.pieslice([110, 96, 230, 224], 180, 360, fill=hair_c)
pd.polygon([(110, 150), (122, 100), (140, 92), (136, 158)], fill=hair_c)
pd.polygon([(230, 150), (218, 100), (200, 92), (204, 158)], fill=hair_c)
pd.polygon([(112, 158), (120, 210), (128, 246), (118, 246), (110, 200)], fill=hair_c)
pd.polygon([(228, 158), (220, 210), (212, 246), (222, 246), (230, 200)], fill=hair_c)
pd.arc([118, 100, 222, 214], 200, 340, fill=(30, 20, 14), width=3)
# brows (lower, straighter)
pd.arc([132, 152, 162, 170], 205, 335, fill=(52, 36, 24), width=4)
pd.arc([178, 152, 208, 170], 205, 335, fill=(52, 36, 24), width=4)
# eyes: white, iris, pupil, lash line above (not through) the eye
for ex in (136, 182):
    pd.ellipse([ex, 168, ex + 24, 182], fill=(245, 242, 235))
    pd.ellipse([ex + 7, 168, ex + 17, 182], fill=(74, 52, 30))
    pd.ellipse([ex + 10, 171, ex + 14, 179], fill=(16, 12, 10))
    pd.arc([ex - 2, 160, ex + 26, 180], 200, 340, fill=(40, 28, 20), width=2)
# nose: soft shadow line + nostril hint
pd.line([(170, 184), (166, 214), (172, 218)], fill=skin_sh, width=3)
pd.line([(164, 218), (176, 218)], fill=(150, 100, 74), width=2)
# lips: closed mouth, gentle curve, faint lower-lip light
pd.arc([150, 228, 190, 244], 20, 160, fill=(164, 92, 76), width=3)
pd.ellipse([158, 240, 182, 248], fill=(222, 176, 148))
# cheek shading (soft, small) + jaw light
pd.ellipse([130, 200, 148, 216], fill=(222, 172, 140))
pd.ellipse([192, 200, 210, 216], fill=(222, 172, 140))
# portrait frame
por = por.resize((PW, PH), Image.LANCZOS)
img.paste(por, (PX0, PY0))
d.rectangle([PX0, PY0, PX0 + PW, PY0 + PH], outline=INK, width=2)
d.rectangle([PX0 + 4, PY0 + 4, PX0 + PW - 4, PY0 + PH - 4], outline=(150, 140, 120), width=1)
# ghost security print over portrait corner
d.text((PX0 + 8, PY0 + 6), "VELMORA", font=F(SANS_B, 11), fill=(96, 114, 132))

# signature under portrait
d.line([(PX0, PY0 + PH + 26), (PX0 + PW, PY0 + PH + 26)], fill=INK, width=1)
d.text((PX0, PY0 + PH + 31), "ELIN MAREK SOLEN", font=F(SERIF_I, 15), fill=(44, 52, 88))
d.text((PX0, PY0 + PH + 50), "HOLDER'S SIGNATURE", font=F(SANS, 7), fill=GREY)

# ---- data fields, two columns right of portrait ----
FX = LX0 + 218
COL_W = 100
fields_a = [
    ("SURNAME", "SOLEN"),
    ("GIVEN NAMES", "ELIN MAREK"),
    ("NATIONALITY", "VELMORAN"),
    ("DATE OF BIRTH", "14 MAR 1994"),
    ("PLACE OF BIRTH", "SARELLE"),
]
fields_b = [
    ("SEX", "F"),
    ("OCCUPATION", "LIGHTHOUSE KEEPER"),
    ("DATE OF ISSUE", "02 JUN 2026"),
    ("DATE OF EXPIRY", "01 JUN 2036"),
    ("AUTHORITY", "MINISTRY OF THE INTERIOR"),
]
def field_col(x, items, y0):
    y = y0
    for lab, val in items:
        d.text((x, y), lab, font=F(SANS, 7), fill=GREY)
        for j, ln in enumerate(wrap(d, val, F(SERIF_B, 12), COL_W)):
            d.text((x, y + 10 + j * 14), ln, font=F(SERIF_B, 12), fill=INK)
        y += 46
    return y
field_col(FX, fields_a, 326)
field_col(FX + 108, fields_b, 326)
d.line([(FX, 326 + 5 * 46 - 6), (LX1 - 28, 326 + 5 * 46 - 6)], fill=(170, 160, 140), width=1)

# ---- notice box ----
NY0 = 640
d.rectangle([LX0 + 28, NY0, LX1 - 28, NY0 + 74], outline=(150, 140, 120), width=1)
d.text((LX0 + 38, NY0 + 8), "NOTICE", font=F(SANS_B, 9), fill=INK)
note = ("This passport remains the property of the Republic of Velmora. "
        "It must be produced on demand to any Velmoran officer and "
        "surrendered when a new passport is issued.")
for j, ln in enumerate(wrap(d, note, F(SERIF, 11), LX1 - LX0 - 76)):
    d.text((LX0 + 38, NY0 + 22 + j * 14), ln, font=F(SERIF, 11), fill=INK_SOFT)

# ---- MRZ ----
l1, l2 = mrz_lines()
MZ0 = 800
d.rectangle([LX0 + 28, MZ0 - 8, LX1 - 28, MZ0 + 52], fill=(232, 227, 212))
d.text((LX0 + 38, MZ0), l1, font=F(MONO, 14), fill=INK)
d.text((LX0 + 38, MZ0 + 20), l2, font=F(MONO, 14), fill=INK)
d.text((LX0 + 28, PAGE_Y1 - 22), "11", font=F(SANS, 9), fill=GREY)

# ================= RIGHT PAGE: VISAS & STAMPS =================
RCX = (RX0 + RX1) // 2  # 758
center(d, RCX, 138, "VISAS", F(SERIF, 20), INK, spacing=10)
d.text((RX1 - 52, 138), "12", font=F(SANS, 10), fill=GREY)
d.line([(RX0 + 28, 176), (RX1 - 28, 176)], fill=INK, width=1)
d.line([(RX0 + 28, 179), (RX1 - 28, 179)], fill=INK, width=1)

# ---- conditions box: the telling detail of paperwork ----
BX0, BY0, BX1 = RX0 + 28, 196, RX1 - 28
d.rectangle([BX0, BY0, BX1, BY0 + 96], outline=(150, 140, 120), width=1)
d.rectangle([BX0 + 3, BY0 + 3, BX1 - 3, BY0 + 93], outline=(190, 180, 160), width=1)
d.text((BX0 + 12, BY0 + 8), "CONDITIONS OF ISSUE", font=F(SANS_B, 9), fill=INK)
cond = ("The holder may not take paid work aboard fishing vessels without a "
        "harbour permit. Holders travelling to the Outer Isles must carry a "
        "harbour permit issued at Sarelle. This passport is not valid for "
        "travel to the Northern Reaches.")
for j, ln in enumerate(wrap(d, cond, F(SERIF, 11), BX1 - BX0 - 24)):
    d.text((BX0 + 12, BY0 + 24 + j * 14), ln, font=F(SERIF, 11), fill=INK_SOFT)

# ---- stamps: one translucent ink layer each, slight rotation ----
def stamp(x, y, w, h, angle, color, country, kind, place, date):
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    cx, cy = (w + 40) // 2, (h + 40) // 2
    ink = color + (215,)
    sd.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=8, outline=ink, width=3)
    sd.rounded_rectangle([24, 24, 16 + w, 16 + h], radius=6, outline=ink, width=1)
    sd.text((cx, 20 + 10), country, font=F(SANS_B, 14), fill=ink, anchor="ma")
    sd.text((cx, 20 + 30), kind, font=F(SANS_B, 12), fill=ink, anchor="ma")
    sd.line([(30, 20 + 50), (10 + w, 20 + 50)], fill=ink, width=1)
    sd.text((cx, 20 + 54), place, font=F(SANS, 10), fill=ink, anchor="ma")
    sd.text((cx, 20 + 68), date, font=F(SANS_B, 12), fill=ink, anchor="ma")
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    layer = layer.filter(ImageFilter.GaussianBlur(0.5))
    img.paste(layer, (x - 20, y - 20), layer)

SW, SH = 196, 96
stamps = [
    (GREEN,  "VELMORA",   "DEPARTURE", "SARELLE", "17 JUN 2026"),
    (BLUE,   "KARSTOVIA", "ENTRY",     "ZVENKOV", "18 JUN 2026"),
    (BLUE,   "KARSTOVIA", "EXIT",      "ZVENKOV", "25 JUN 2026"),
    (GREEN,  "VELMORA",   "ARRIVAL",   "SARELLE", "26 JUN 2026"),
    (PURPLE, "TESSALIN",  "ENTRY",     "HALDOR",  "09 SEP 2026"),
    (PURPLE, "TESSALIN",  "EXIT",      "HALDOR",  "21 SEP 2026"),
]
angles = [-6, 5, -4, 7, -7, 4]
SX0, SY0 = RX0 + 34, 316
for i, (color, country, kind, place, date) in enumerate(stamps):
    col, row = i % 2, i // 2
    x = SX0 + col * (SW + 16)
    y = SY0 + row * (SH + 22)
    stamp(x, y, SW, SH, angles[i], color, country, kind, place, date)

# ---- circular harbour-fee stamp, overlapping the last row ----
fee = Image.new("RGBA", (190, 190), (0, 0, 0, 0))
fd = ImageDraw.Draw(fee)
fink = RED + (205,)
fd.ellipse([10, 10, 180, 180], outline=fink, width=3)
fd.ellipse([26, 26, 164, 164], outline=fink, width=1)
fd.text((95, 52), "HARBOUR FEE", font=F(SANS_B, 13), fill=fink, anchor="ma")
fd.text((95, 70), "PAID", font=F(SANS_B, 15), fill=fink, anchor="ma")
fd.line([(48, 92), (142, 92)], fill=fink, width=1)
fd.text((95, 98), "12 VLD", font=F(SERIF_B, 17), fill=fink, anchor="ma")
fd.text((95, 122), "SARELLE", font=F(SANS, 10), fill=fink, anchor="ma")
fd.text((95, 136), "02 JUN 2026", font=F(SANS_B, 11), fill=fink, anchor="ma")
fee = fee.rotate(-12, resample=Image.BICUBIC, expand=False)
fee = fee.filter(ImageFilter.GaussianBlur(0.5))
img.paste(fee, (795, 680), fee)

d.text((RX0 + 28, PAGE_Y1 - 22), "OFFICIAL STAMPS ONLY — UNAUTHORISED MARKS VOID THIS PAGE",
       font=F(SANS, 7), fill=GREY)
d.text((RX1 - 52, PAGE_Y1 - 22), "12", font=F(SANS, 9), fill=GREY)

# ---- paper grain + vignette over the whole spread ----
noise = Image.effect_noise((W, H), 16).convert("L")
img.paste(Image.merge("RGB", (noise, noise, noise)), (0, 0),
          Image.new("L", (W, H), 0).point(lambda v: 8))
# (desk gradient above already gives depth; no extra vignette)
os.makedirs(REPO, exist_ok=True)
img.save(OUT, format="PNG", optimize=True)
size = os.path.getsize(OUT)
print("wrote", OUT, size, "bytes; MRZ:", l1, "|", l2)
assert size <= 1048576, "over 1 MiB"
assert img.size == (1024, 1024)
print("OK: 1024x1024, under 1 MiB")
