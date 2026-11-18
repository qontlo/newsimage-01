#!/usr/bin/env python3
"""newsimage-01 — "Tuesday 17 November 2026: 48 stories, six continents,
one front page" (our own front-page design).

Draws a 1024x1024 newspaper front page summing up the world news of
Tuesday 17 November 2026 and writes /output/entry.png.

Run contract (kit starter): MAKEFUN_OUTPUT_DIR stands in for /output
outside the grader container, e.g.
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

Deterministic: no random, no clock, no network, no time-dependent
content. Same input = same bytes. Stdlib + Pillow only.
"""

import hashlib
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
CREAM = (247, 241, 227)      # newsprint ground
PAPER = (252, 248, 238)      # cell ground
INK = (24, 24, 22)           # near-black text
NAVY = (15, 43, 70)          # masthead band, Europe
NAVY_DK = (10, 30, 50)
TEAL = (14, 124, 107)        # Middle East, accents
TEAL_DK = (10, 94, 82)
OCHRE = (180, 110, 16)       # Asia, accents
OCHRE_LT = (214, 158, 46)
GOLD = (201, 162, 39)
SLATE = (71, 85, 105)        # Global
STEEL = (47, 102, 144)       # Americas
SLATE_NV = (62, 92, 118)     # US
OLIVE = (106, 122, 45)       # Africa
PLUM = (107, 78, 122)        # Russia
INDIGO = (91, 91, 138)       # Space
SEA = (207, 224, 232)        # map/panel sea
LAND = (217, 201, 163)       # map/panel land
LAND2 = (201, 185, 138)
RULE = (24, 24, 22)
GREY = (96, 96, 90)

REGION_COLOURS = {
    "EUROPE": NAVY,
    "MIDDLE EAST": TEAL,
    "ASIA": OCHRE,
    "AFRICA": OLIVE,
    "AMERICAS": STEEL,
    "GLOBAL": SLATE,
    "US": SLATE_NV,
    "RUSSIA": PLUM,
    "SPACE": INDIGO,
}

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


def f_serif(size):
    return font(f"{FD}/DejaVuSerif.ttf", size)


def f_serif_b(size):
    return font(f"{FD}/DejaVuSerif-Bold.ttf", size)


def f_sans(size):
    return font(f"{FD}/DejaVuSans.ttf", size)


def f_sans_b(size):
    return font(f"{FD}/DejaVuSans-Bold.ttf", size)


def f_lib(size):
    return font(f"{FL}/LiberationSerif-Regular.ttf", size)


def f_lib_b(size):
    return font(f"{FL}/LiberationSerif-Bold.ttf", size)


# ---------------------------------------------------------------- text helpers
def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = cur + " " + word
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def draw_wrapped(d, xy, text, fnt, fill, max_w, max_lines=None, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    x, y = xy
    lh = leading if leading is not None else int(fnt.size * 1.22)
    lines = wrap(text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def text_h(fnt, lines=1, leading=None):
    lh = leading if leading is not None else int(fnt.size * 1.22)
    return lh * lines


def centred(d, cx, y, text, fnt, fill):
    w = fnt.getlength(text)
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + int(fnt.size * 1.22)


def spaced(d, x, y, text, fnt, fill, tracking=2):
    """Draw capitals with letter spacing; returns the width used."""
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += fnt.getlength(ch) + tracking
    return cx - x


# ---------------------------------------------------------------- data
# Headlines and decks are rephrased in our own words; facts kept exact.
LEADS = [
    {
        "n": 1, "region": "EUROPE", "topic": "UKRAINE WAR",
        "headline": "Crimean Bridge span drops into the sea",
        "deck": "Kyiv says the Kerch crossing was hit for a second day "
                "running; Zelensky calls it an unprecedented operation "
                "as Moscow vows to rebuild.",
        "panel": "kerch",
    },
    {
        "n": 2, "region": "MIDDLE EAST", "topic": "IRAN WAR",
        "headline": "Iran drones target US radar; US hits back",
        "deck": "Bahrain and the US say every drone was shot down; US jets "
                "then hit Qeshm, and Tehran blames mines for tanker "
                "blasts in Hormuz.",
        "panel": "gulf",
    },
    {
        "n": 3, "region": "ASIA", "topic": "DIPLOMACY",
        "headline": "Trump hosts first Quad summit in Manila",
        "deck": "The four leaders unveil critical-minerals deals; Putin "
                "heads to Shenzhen ahead of Thursday's talks with "
                "Trump and Xi.",
        "panel": "quad",
    },
]

GRID = [
    {"n": 4, "region": "AFRICA", "topic": "HEALTH",
     "headline": "Congo Ebola tally passes 11,000",
     "deck": "WHO says cases more than doubled in three months; "
             "about 5,400 dead."},
    {"n": 5, "region": "GLOBAL", "topic": "CLIMATE",
     "headline": "COP31 split over fossil-fuel phase-out",
     "deck": "Nations weigh a first draft at Antalya; the talks "
             "run until Friday."},
    {"n": 6, "region": "AMERICAS", "topic": "HEALTH",
     "headline": "Three nations lose measles-free status",
     "deck": "PAHO blames a year of spread; the US counts more "
             "than 5,700 cases in 2026."},
    {"n": 7, "region": "US", "topic": "BUSINESS",
     "headline": "Nvidia sales double to $115.8bn",
     "deck": "Figures land after the close; earlier the Dow slid "
             "849 points, down 1.6%."},
    {"n": 8, "region": "MIDDLE EAST", "topic": "GAZA",
     "headline": "Gaza truce close to collapse, UN told",
     "deck": "UN agencies warn 1.4 million people face acute hunger."},
    {"n": 9, "region": "ASIA", "topic": "POLITICS",
     "headline": "Mongolia's president to step down",
     "deck": "Khurelsukh denies a $25m claim; parliament must "
             "accept his resignation."},
    {"n": 10, "region": "EUROPE", "topic": "POLITICS",
     "headline": "Serbia's student-led bloc takes its seats",
     "deck": "Student List holds 140 of 250 seats; Vucic's party "
             "moves into opposition."},
    {"n": 11, "region": "ASIA", "topic": "LABOUR",
     "headline": "Bangladesh police tear-gas garment workers",
     "deck": "Workers seek Tk 30,000 a month, up from 12,500; "
             "37 factories shut."},
    {"n": 12, "region": "RUSSIA", "topic": "AIR CRASH",
     "headline": "Russian An-12 crash kills all 19 aboard",
     "deck": "The air force plane came down near Kemerovo; a "
             "fault is suspected."},
    {"n": 13, "region": "AFRICA", "topic": "JUSTICE",
     "headline": "Mozambique tries opposition leader",
     "deck": "Venancio Mondlane faces five charges over the "
             "deadly 2024 protests."},
    {"n": 14, "region": "SPACE", "topic": "",
     "headline": "Voyager 1 nears one light-day from Earth",
     "deck": "The probe crosses the mark early Wednesday, a first."},
    {"n": 15, "region": "EUROPE", "topic": "BANKING",
     "headline": "Deutsche Bank falls 6% on leaked files",
     "deck": "Frankfurt shares slide as the leak spreads."},
]

# Index lines, one per story, kept short so each fits one line.
INDEX = [
    (16, "Russia: record 1,441 drones downed in a night."),
    (17, "Kyiv: missiles hit two Dnipro bridges."),
    (18, "UN: Ukraine civilian deaths pass 2025 total."),
    (19, "Prague: two trains collide; 46 hurt."),
    (20, "France: public-sector strike; 146,000 march."),
    (21, "Poland: Tusk survives no-confidence vote."),
    (22, "Moldova shuts airspace as drone nears capital."),
    (23, "Turkey: police seize broadcaster Sozcu TV."),
    (24, "Vatican: Pope Leo XIV back from S. America."),
    (25, "UK sanctions 8 settlement firms and Tzav 9."),
    (26, "Israel: Kahana elected Knesset speaker, 66-52."),
    (27, "West Bank: settlers kill woman, 72, near Jericho."),
    (28, "Oman: Iran's Araghchi in shipping-safety talks."),
    (29, "India: Cyclone Akvan strengthens; Odisha flees."),
    (30, "India: bus falls into gorge; 8 dead."),
    (31, "Japan scrambles jets as Russia breaches airspace."),
    (32, "China-Canada: more tariff cuts after talks."),
    (33, "Malaysia: Macron visit seals partnership."),
    (34, "Thailand to scrap tariffs on US goods."),
    (35, "S. Korea: IMF lifts 2026 growth call to 3.9%."),
    (36, "Sudan: UN verifies 2,230 drone deaths, Jan-Oct."),
    (37, "Kenya: WFP feeds 30,000 who fled Ethiopia."),
    (38, "Haiti: Aristide's party fields no candidates."),
    (39, "US Senate: Van Hollen challenges Schumer."),
    (40, "Australia eases backpacker visa curbs."),
    (41, "Indonesia: M6.6 Banda Sea quake; no tsunami."),
    (42, "Apple: Pay, iCloud, App Store down; 'not a hack'."),
    (43, "Cook Islands: Cyclone Xavier hits Category 4."),
    (44, "Football: India beat Pakistan 2-1, SAFF final."),
    (45, "Football: Togo beat Algeria 3-0, AFCON qualifier."),
    (46, "Football: Norway beat Denmark 3-2; Haaland x2."),
    (47, "Football: Brazil beat Singapore 7-0; Vinicius x3."),
    (48, "US: JPMorgan bug hits Zelle; 'not cyber'."),
]

# Six stats figures, different from the reference entry's strip.
STATS = [
    ("5,400", "EBOLA DEAD IN DR CONGO"),
    ("5,700+", "US MEASLES CASES IN 2026"),
    ("140", "OF 250 SEATS — STUDENT LIST"),
    ("2,230", "SUDAN DRONE DEATHS VERIFIED BY UN"),
    ("146k", "MARCHERS IN FRANCE STRIKE"),
    ("6%", "DEUTSCHE BANK FALL"),
]

# Map pins: (story number, region, lon, lat, dx, dy). dx/dy shift a pin
# away from its true spot with a leader line, for pins that would
# otherwise sit on top of each other (Antalya 5 and Gaza 8).
PINS = [
    (1, "EUROPE", 37.5, 45.3, 14, -10),
    (2, "MIDDLE EAST", 50.6, 26.2, 16, -6),
    (3, "ASIA", 121.0, 14.6, 0, 0),
    (4, "AFRICA", 23.0, -2.0, 0, 0),
    (5, "GLOBAL", 30.7, 36.9, -16, 8),
    (6, "AMERICAS", -100.0, 30.0, 0, 0),
    (7, "US", -74.0, 40.7, 0, 0),
    (8, "MIDDLE EAST", 34.5, 31.5, 2, 20),
    (9, "ASIA", 106.9, 47.9, 0, 0),
    (10, "EUROPE", 20.5, 44.8, -6, -20),
    (11, "ASIA", 90.4, 23.8, 0, 0),
    (12, "RUSSIA", 86.0, 55.3, 0, 0),
    (13, "AFRICA", 32.6, -25.9, 0, 0),
    (15, "EUROPE", 8.7, 50.1, -14, -12),
]

# Coarse continent silhouettes (lon, lat), equirectangular.
CONTINENTS = {
    "NORTH AMERICA": [
        (-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 72),
        (-100, 73), (-90, 74), (-82, 72), (-76, 68), (-68, 62),
        (-60, 55), (-55, 47), (-60, 44), (-68, 42), (-75, 36),
        (-80, 32), (-81, 26), (-86, 21), (-91, 19), (-97, 16),
        (-94, 17), (-101, 19), (-106, 23), (-112, 28), (-117, 33),
        (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-152, 58),
        (-162, 58), (-168, 61),
    ],
    "SOUTH AMERICA": [
        (-80, 10), (-77, 7), (-74, 3), (-68, 1), (-60, 0), (-52, -3),
        (-44, -5), (-36, -8), (-38, -15), (-40, -22), (-48, -27),
        (-53, -33), (-58, -38), (-62, -41), (-66, -47), (-68, -52),
        (-71, -54), (-73, -44), (-73, -33), (-71, -20), (-77, -12),
        (-81, -6), (-81, 0), (-80, 6),
    ],
    "AFRICA": [
        (-17, 15), (-16, 20), (-10, 30), (-5, 35), (0, 36), (9, 37),
        (15, 32), (20, 32), (25, 32), (30, 31), (34, 28), (37, 22),
        (39, 18), (43, 12), (48, 11), (51, 11), (50, 5), (46, -2),
        (42, -8), (40, -15), (36, -20), (33, -26), (29, -30), (25, -34),
        (20, -35), (17, -32), (15, -27), (13, -20), (12, -14), (9, -2),
        (9, 4), (4, 6), (-3, 5), (-8, 5), (-13, 8), (-17, 12),
    ],
    "EUROPE": [
        (-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 48), (0, 49),
        (2, 51), (4, 53), (7, 55), (8, 57), (10, 59), (14, 58),
        (18, 56), (21, 55), (23, 57), (25, 59), (28, 60), (30, 62),
        (28, 65), (24, 68), (20, 70), (16, 70), (12, 68), (8, 64),
        (6, 61), (4, 58), (2, 55), (0, 52), (-4, 50), (-6, 48),
        (-9, 44), (-10, 40),
    ],
    "ASIA": [
        (30, 62), (32, 66), (40, 68), (48, 69), (55, 71), (62, 72),
        (70, 73), (78, 73), (88, 75), (98, 76), (108, 76), (118, 73),
        (128, 72), (138, 72), (150, 70), (160, 69), (170, 67), (178, 65),
        (173, 64), (170, 60), (163, 58), (158, 53), (156, 51), (148, 48),
        (142, 46), (141, 40), (137, 36), (130, 33), (127, 35), (126, 38),
        (122, 39), (121, 32), (120, 26), (118, 23), (112, 21), (108, 18),
        (105, 10), (103, 8), (100, 7), (99, 12), (97, 16), (94, 17),
        (92, 21), (89, 22), (86, 20), (82, 17), (80, 14), (77, 8),
        (75, 12), (73, 19), (71, 21), (68, 23), (66, 25), (62, 25),
        (58, 26), (56, 27), (54, 27), (52, 28), (50, 29), (48, 30),
        (46, 30), (44, 29), (42, 31), (40, 33), (38, 36), (36, 36),
        (34, 36), (32, 37), (30, 38), (28, 40), (27, 41), (28, 45),
        (29, 48), (29, 52), (29, 56), (29, 60),
    ],
    "AUSTRALIA": [
        (114, -22), (114, -28), (115, -32), (118, -35), (122, -34),
        (126, -32), (130, -32), (134, -33), (137, -35), (140, -38),
        (144, -39), (148, -38), (150, -37), (153, -32), (153, -27),
        (152, -24), (150, -22), (148, -20), (146, -19), (143, -15),
        (142, -11), (140, -13), (137, -12), (134, -12), (131, -12),
        (128, -14), (125, -15), (122, -17), (119, -20), (116, -21),
    ],
}

# ---------------------------------------------------------------- sections
def draw_kicker(d, y):
    f = f_sans_b(11)
    spaced(d, 14, y, "THE WORLD'S NEWS IN ONE PICTURE", f, INK, tracking=2)
    right = "48 STORIES  •  6 CONTINENTS  •  ALL FROM TUESDAY"
    w = sum(f.getlength(ch) + 2 for ch in right) - 2
    spaced(d, W - 14 - w, y, right, f, INK, tracking=2)
    return y + 20


def draw_masthead(d, y):
    h = 74
    d.rectangle([10, y, W - 10, y + h], fill=NAVY)
    d.rectangle([10, y, W - 10, y + 3], fill=OCHRE_LT)
    d.rectangle([10, y + h - 3, W - 10, y + h], fill=OCHRE_LT)
    f = f_serif_b(54)
    centred(d, W // 2, y + 10, "TUESDAY 17 NOVEMBER 2026", f, CREAM)
    return y + h


def draw_stats(d, y):
    h = 68
    d.line([10, y, W - 10, y], fill=RULE, width=2)
    d.line([10, y + h, W - 10, y + h], fill=RULE, width=2)
    cell_w = (W - 20) / 6
    f_num = f_serif_b(40)
    f_cap = f_sans_b(10)
    for i, (num, cap) in enumerate(STATS):
        x0 = 10 + i * cell_w
        if i:
            d.line([x0, y + 8, x0, y + h - 8], fill=(190, 180, 160), width=1)
        centred(d, x0 + cell_w / 2, y + 4, num, f_num, NAVY)
        # caption, wrapped to two short lines
        cap_lines = wrap(cap, f_cap, cell_w - 14)
        cy = y + 44
        for line in cap_lines[:2]:
            centred(d, x0 + cell_w / 2, cy, line, f_cap, GREY)
            cy += 12
    return y + h


def starburst(d, cx, cy, r, colour):
    """Simple 8-point starburst."""
    pts = []
    for i in range(16):
        ang = 3.14159 * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang),
                    cy + rr * math.sin(ang)))
    d.polygon(pts, fill=colour)


def draw_panel_kerch(d, x, y, w, h):
    """Kerch Strait: sea, two land masses, the bridge with a broken span."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # ochre sun + white clouds over the northern shore
    d.ellipse([x + w - 34, y + 8, x + w - 14, y + 28], fill=OCHRE)
    for cx, cy, cr in ((x + 26, y + 12, 9), (x + 42, y + 9, 11),
                       (x + 58, y + 13, 8)):
        d.ellipse([cx - cr, cy - cr * 0.6, cx + cr, cy + cr * 0.6],
                  fill=(255, 255, 255))
    # Russia (top) and Crimea (bottom) land masses
    d.polygon([(x, y), (x + w, y), (x + w, y + 34), (x + w * 0.62, y + 52),
               (x + w * 0.30, y + 44), (x, y + 52)], fill=LAND)
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 30),
               (x + w * 0.55, y + h - 44), (x + w * 0.28, y + h - 36),
               (x, y + h - 26)], fill=LAND2)
    # waves in the strait
    for wx, wy in ((x + 90, y + 66), (x + 130, y + 72), (x + 236, y + 68),
                   (x + 272, y + 72)):
        d.arc([wx, wy, wx + 22, wy + 9], 180, 360, fill=(255, 255, 255), width=2)
    # small ship in the Black Sea lane, behind the bridge deck
    sx, sy = x + 24, y + 72
    d.polygon([(sx, sy), (sx + 34, sy), (sx + 28, sy + 8), (sx + 6, sy + 8)],
              fill=NAVY_DK)
    d.rectangle([sx + 12, sy - 7, sx + 22, sy], fill=NAVY_DK)
    d.line([sx + 17, sy - 14, sx + 17, sy - 7], fill=NAVY_DK, width=2)
    # the bridge, with a gap in the middle
    by = y + h // 2 + 2
    d.line([x + 8, by, x + w * 0.42, by], fill=NAVY, width=5)
    d.line([x + w * 0.58, by, x + w - 8, by], fill=NAVY, width=5)
    for bx in (x + 30, x + w * 0.30, x + w * 0.70, x + w - 30):
        d.line([bx, by, bx, by + 12], fill=NAVY, width=3)
    # pylons + suspension cables over the broken span
    for px in (x + w * 0.42 - 2, x + w * 0.58 - 2):
        d.line([px, by - 20, px, by + 12], fill=NAVY, width=3)
    d.line([x + w * 0.42 - 2, by - 20, x + 30, by], fill=NAVY, width=1)
    d.line([x + w * 0.58 - 2, by - 20, x + w - 30, by], fill=NAVY, width=1)
    # burst + debris
    starburst(d, x + w // 2, by - 2, 17, OCHRE)
    d.ellipse([x + w // 2 - 4, by - 6, x + w // 2 + 4, by + 2], fill=(255, 255, 255))
    for dx, dy, dr in ((-26, -14, 3), (-14, -20, 2), (20, -16, 3), (30, -8, 2),
                       (-32, 4, 2), (34, 6, 3), (-8, -24, 2), (10, -22, 2)):
        d.ellipse([x + w // 2 + dx - dr, by + dy - dr,
                   x + w // 2 + dx + dr, by + dy + dr], fill=(120, 116, 108))
    # gulls over the strait
    for gx, gy in ((x + 88, y + 54), (x + 108, y + 50), (x + 252, y + 52)):
        d.arc([gx, gy, gx + 10, gy + 6], 180, 360, fill=NAVY, width=1)
        d.arc([gx + 10, gy, gx + 20, gy + 6], 180, 360, fill=NAVY, width=1)
    f = f_sans_b(10)
    d.text((x + 10, y + 6), "SEA OF AZOV", font=f, fill=NAVY)
    d.text((x + 10, y + h - 30), "BLACK SEA", font=f, fill=NAVY)
    lab = "CRIMEAN BRIDGE"
    d.text((x + w - f.getlength(lab) - 8, by - 22), lab, font=f, fill=NAVY)
    # caption bar
    d.rectangle([x, y + h - 14, x + w, y + h], fill=NAVY)
    centred(d, x + w / 2, y + h - 12, "KERCH STRAIT  •  SPAN IN THE SEA",
            f_sans_b(10), CREAM)


def draw_panel_gulf(d, x, y, w, h):
    """Persian Gulf: Iran top, Arabia below, Bahrain and Qeshm marked."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # Iran (top land) and Arabia (bottom land)
    d.polygon([(x, y), (x + w, y), (x + w, y + 40), (x + w * 0.72, y + 52),
               (x + w * 0.40, y + 44), (x, y + 48)], fill=LAND)
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 26),
               (x + w * 0.60, y + h - 52), (x + w * 0.34, y + h - 44),
               (x, y + h - 34)], fill=LAND2)
    # Qeshm island
    d.ellipse([x + w * 0.52, y + h * 0.52, x + w * 0.68, y + h * 0.62],
              fill=LAND)
    # tankers in the shipping lane
    for tx, ty in ((x + 52, y + 58), (x + 246, y + 64)):
        d.polygon([(tx, ty), (tx + 34, ty), (tx + 28, ty + 7), (tx + 6, ty + 7)],
                  fill=NAVY_DK)
        d.rectangle([tx + 10, ty - 6, tx + 20, ty], fill=NAVY_DK)
        d.line([tx + 15, ty - 12, tx + 15, ty - 6], fill=NAVY_DK, width=2)
        d.rectangle([tx + 24, ty - 4, tx + 28, ty], fill=OCHRE)
    # waves
    for wx, wy in ((x + 14, y + 74), (x + 180, y + 54), (x + 286, y + 76)):
        d.arc([wx, wy, wx + 22, wy + 9], 180, 360, fill=(255, 255, 255), width=2)
    # dashed drone track from Iran toward Bahrain
    bx, by = x + w * 0.30, y + h * 0.72
    for i in range(7):
        t0 = i / 7
        t1 = (i + 0.55) / 7
        d.line([bx + (x + w * 0.58 - bx) * t0, by + (y + h * 0.52 - by) * t0,
                bx + (x + w * 0.58 - bx) * t1, by + (y + h * 0.52 - by) * t1],
               fill=TEAL_DK, width=2)
    # drone silhouettes along the track
    for t in (0.25, 0.5, 0.75):
        dx = bx + (x + w * 0.58 - bx) * t
        dy = by + (y + h * 0.52 - by) * t
        d.polygon([(dx, dy - 5), (dx + 9, dy + 3), (dx - 2, dy + 2)], fill=NAVY_DK)
    # radar arcs around Bahrain
    for rr in (9, 15, 21):
        d.ellipse([bx - rr, by - rr, bx + rr, by + rr], outline=TEAL_DK, width=1)
    # Bahrain dot and Qeshm dot
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=NAVY)
    d.ellipse([x + w * 0.60 - 4, y + h * 0.57 - 4,
               x + w * 0.60 + 4, y + h * 0.57 + 4], fill=OCHRE)
    # compass rose, top right
    cx, cy = x + w - 18, y + 14
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=NAVY, width=1)
    d.polygon([(cx, cy - 9), (cx + 3, cy + 2), (cx - 3, cy + 2)], fill=NAVY)
    d.text((cx - 4, cy + 3), "N", font=f_sans_b(10), fill=NAVY)
    f = f_sans_b(10)
    d.text((x + 10, y + 6), "IRAN", font=f, fill=NAVY)
    d.text((x + 10, y + h - 32), "ARABIA", font=f, fill=NAVY)
    d.text((bx + 24, by + 2), "BAHRAIN", font=f, fill=NAVY)
    d.text((x + w * 0.62, y + h * 0.50), "QESHM", font=f, fill=NAVY)
    # caption bar
    d.rectangle([x, y + h - 14, x + w, y + h], fill=NAVY)
    centred(d, x + w / 2, y + h - 12, "THE GULF  •  BAHRAIN  •  QESHM  •  HORMUZ",
            f_sans_b(10), CREAM)


def draw_flag_us(d, x, y, w, h):
    stripe = h / 13
    for i in range(13):
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    cw, ch = w * 0.42, stripe * 7
    d.rectangle([x, y, x + cw, y + ch], fill=NAVY)
    for r in range(4):
        for c in range(5):
            d.ellipse([x + 4 + c * (cw - 8) / 4 - 1, y + 4 + r * (ch - 8) / 3 - 1,
                       x + 4 + c * (cw - 8) / 4 + 1, y + 4 + r * (ch - 8) / 3 + 1],
                      fill=(255, 255, 255))


def draw_flag_jp(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    r = h * 0.30
    d.ellipse([x + w / 2 - r, y + h / 2 - r, x + w / 2 + r, y + h / 2 + r],
              fill=(188, 0, 45))


def draw_flag_in(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 153, 51))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(19, 136, 8))
    r = h * 0.16
    d.ellipse([x + w / 2 - r, y + h / 2 - r, x + w / 2 + r, y + h / 2 + r],
              outline=NAVY, width=2)
    d.ellipse([x + w / 2 - 2, y + h / 2 - 2, x + w / 2 + 2, y + h / 2 + 2],
              fill=NAVY)


def draw_flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
    # Union Jack hint in the canton
    d.rectangle([x, y, x + w * 0.45, y + h * 0.5], fill=(0, 40, 104))
    d.line([x, y, x + w * 0.45, y + h * 0.5], fill=(255, 255, 255), width=3)
    d.line([x + w * 0.45, y, x, y + h * 0.5], fill=(255, 255, 255), width=3)
    d.line([x + w * 0.22, y, x + w * 0.22, y + h * 0.5], fill=(200, 30, 40), width=3)
    d.line([x, y + h * 0.25, x + w * 0.45, y + h * 0.25], fill=(200, 30, 40), width=3)
    # southern cross stars
    for sx, sy, sr in ((0.70, 0.25, 3), (0.82, 0.45, 3), (0.68, 0.62, 3),
                       (0.55, 0.45, 2), (0.88, 0.75, 3)):
        d.ellipse([x + w * sx - sr, y + h * sy - sr,
                   x + w * sx + sr, y + h * sy + sr], fill=(255, 255, 255))


def draw_panel_quad(d, x, y, w, h):
    """Quad flags row under a navy banner naming Manila."""
    banner = 22
    d.rectangle([x, y, x + w, y + banner], fill=NAVY)
    f = f_sans_b(10)
    centred(d, x + w / 2, y + 5, "FIRST QUAD SUMMIT  •  MANILA", f, CREAM)
    d.rectangle([x, y + banner, x + w, y + banner + 2], fill=GOLD)
    d.rectangle([x, y + banner + 2, x + w, y + h], fill=PAPER)
    flags = [(draw_flag_us, "USA"), (draw_flag_jp, "JAPAN"),
             (draw_flag_in, "INDIA"), (draw_flag_au, "AUSTRALIA")]
    fw = (w - 10 * 5) / 4
    fh = h - banner - 28
    fy = y + banner + 10
    # flagpoles with gold finials, joined by a gold cord
    pole_y = y + banner + 2
    xs = []
    for i in range(4):
        fx = x + 10 + i * (fw + 10)
        xs.append(fx + fw / 2)
    d.line([xs[0], pole_y + 2, xs[-1], pole_y + 2], fill=GOLD, width=1)
    for cx in xs:
        d.line([cx, pole_y + 2, cx, fy], fill=GOLD, width=2)
        d.ellipse([cx - 3, pole_y - 1, cx + 3, pole_y + 5], fill=GOLD)
    for i, (fn, name) in enumerate(flags):
        fx = x + 10 + i * (fw + 10)
        fn(d, fx, fy, fw, fh)
        d.rectangle([fx, fy, fx + fw, fy + fh], outline=RULE, width=1)
        centred(d, fx + fw / 2, fy + fh + 4, name, f_sans_b(10), INK)
    d.rectangle([x, y + h - 3, x + w, y + h], fill=GOLD)


PANEL_DRAWERS = {
    "kerch": draw_panel_kerch,
    "gulf": draw_panel_gulf,
    "quad": draw_panel_quad,
}


def draw_leads(d, y):
    col_w = (W - 20 - 2 * 12) / 3
    h = 260
    f_head = f_serif_b(21)
    f_deck = f_serif(12)
    for i, lead in enumerate(LEADS):
        x0 = 10 + i * (col_w + 12)
        col = REGION_COLOURS[lead["region"]]
        # number + label row
        d.ellipse([x0, y, x0 + 24, y + 24], fill=col)
        nf = f_sans_b(13)
        nw = nf.getlength(str(lead["n"]))
        d.text((x0 + 12 - nw / 2, y + 4), str(lead["n"]), font=nf, fill=(255, 255, 255))
        lab = lead["region"] + ("  •  " + lead["topic"] if lead["topic"] else "")
        d.text((x0 + 30, y + 5), lab, font=f_sans_b(11), fill=col)
        # illustrated panel
        py = y + 30
        ph = 120
        d.rectangle([x0, py, x0 + col_w, py + ph], outline=RULE, width=1)
        PANEL_DRAWERS[lead["panel"]](d, x0 + 1, py + 1, col_w - 2, ph - 2)
        # headline + deck
        hy = py + ph + 8
        hy = draw_wrapped(d, (x0, hy), lead["headline"], f_head, INK,
                          col_w, max_lines=2, leading=25)
        draw_wrapped(d, (x0, hy + 3), lead["deck"], f_deck, (50, 50, 46),
                     col_w, max_lines=3, leading=15)
        if i < 2:
            d.line([x0 + col_w + 6, y + 4, x0 + col_w + 6, y + h - 4],
                   fill=(190, 180, 160), width=1)
    d.line([10, y + h, W - 10, y + h], fill=RULE, width=2)
    return y + h

# ---------------------------------------------------------------- grid
def draw_grid(d, y):
    col_w = (W - 20 - 3 * 8) / 4
    row_h = 100
    f_head = f_serif_b(13)
    f_deck = f_serif(11)
    for idx, story in enumerate(GRID):
        r, c = divmod(idx, 4)
        x0 = 10 + c * (col_w + 8)
        y0 = y + r * row_h
        col = REGION_COLOURS[story["region"]]
        d.rectangle([x0, y0, x0 + col_w, y0 + row_h - 6], fill=PAPER,
                    outline=(200, 190, 170), width=1)
        # colour strip at top
        d.rectangle([x0 + 1, y0 + 1, x0 + col_w - 1, y0 + 6], fill=col)
        # number circle + label
        d.ellipse([x0 + 7, y0 + 12, x0 + 27, y0 + 32], fill=col)
        nf = f_sans_b(11)
        nw = nf.getlength(str(story["n"]))
        d.text((x0 + 17 - nw / 2, y0 + 16), str(story["n"]), font=nf,
               fill=(255, 255, 255))
        lab = story["region"] + ("  •  " + story["topic"] if story["topic"] else "")
        d.text((x0 + 32, y0 + 17), lab, font=f_sans_b(10), fill=col)
        # headline + deck
        hy = draw_wrapped(d, (x0 + 7, y0 + 38), story["headline"], f_head,
                          INK, col_w - 14, max_lines=2, leading=16)
        draw_wrapped(d, (x0 + 7, hy + 2), story["deck"], f_deck, (50, 50, 46),
                     col_w - 14, max_lines=2, leading=13)
    return y + 3 * row_h


# ---------------------------------------------------------------- map
# Dot-matrix world map. Technique adapted from the reference entry's
# approach (a 48x28 hand-drawn ASCII mask on a square 7 px grid):
# ours generates the mask from our own CONTINENTS polygons with a
# point-in-polygon test, on a square 7 px grid sized to our wider
# map panel (57 cols x 24 rows). Land reads as dots, not blobs.
MAP_COLS, MAP_ROWS = 57, 24
MAP_PITCH = 7
MAP_DOT_R = 2.2
MAP_LAT_TOP, MAP_LAT_BOT = 75.0, -60.0


def point_in_polygon(px, py, poly):
    """Ray-casting point-in-polygon test; poly is a list of (x, y)."""
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py):
            xint = (xj - xi) * (py - yi) / (yj - yi) + xi
            if px < xint:
                inside = not inside
        j = i
    return inside


def build_dot_mask():
    """Cells of the dot grid whose centre falls on land."""
    cells = []
    for r in range(MAP_ROWS):
        lat = MAP_LAT_TOP - (r + 0.5) * (MAP_LAT_TOP - MAP_LAT_BOT) / MAP_ROWS
        for c in range(MAP_COLS):
            lon = -180.0 + (c + 0.5) * 360.0 / MAP_COLS
            if any(point_in_polygon(lon, lat, poly)
                   for poly in CONTINENTS.values()):
                cells.append((c, r))
    return cells


DOT_MASK = build_dot_mask()


def pin_xy(lon, lat, mx, my):
    """True geographic position of a pin in map pixel space."""
    x = mx + 3.5 + (lon + 180.0) / 360.0 * (MAP_COLS - 1) * MAP_PITCH
    y = my + 3.5 + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) \
        * (MAP_ROWS - 1) * MAP_PITCH
    return x, y


def draw_map(d, x, y, w, h):
    f_title = f_sans_b(11)
    d.text((x, y), "WHERE IT HAPPENED", font=f_title, fill=NAVY)
    d.line([x, y + 16, x + w, y + 16], fill=RULE, width=1)
    mx, my, mw, mh = x, y + 22, w, 170
    d.rectangle([mx, my, mx + mw, my + mh], fill=CREAM)
    # dotted continents
    for c, r in DOT_MASK:
        d.ellipse([mx + 3.5 + c * MAP_PITCH - MAP_DOT_R,
                   my + 3.5 + r * MAP_PITCH - MAP_DOT_R,
                   mx + 3.5 + c * MAP_PITCH + MAP_DOT_R,
                   my + 3.5 + r * MAP_PITCH + MAP_DOT_R], fill=NAVY)
    # pins 1-15 at true positions, spread with leader lines
    for n, region, lon, lat, dx, dy in PINS:
        px, py = pin_xy(lon, lat, mx, my)
        col = REGION_COLOURS[region]
        if dx or dy:
            d.line([px, py, px + dx, py + dy], fill=col, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
            px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col,
                  outline=(255, 255, 255), width=1)
        nf = f_sans_b(10)
        nw = nf.getlength(str(n))
        d.text((px - nw / 2, py - 5), str(n), font=nf, fill=(255, 255, 255))
    # Voyager 1 star, out in the South Pacific, with a full label
    sx, sy = mx + 24, my + mh - 24
    starburst(d, sx, sy, 10, INDIGO)
    d.text((sx + 13, sy - 5), "14 SPACE", font=f_sans_b(10), fill=INDIGO)
    # legend: colour dot + region name, fully inside the section
    ly = my + mh + 6
    f_leg = f_sans(10)
    lx = mx
    for region in ("EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS",
                   "US", "GLOBAL", "RUSSIA", "SPACE"):
        col = REGION_COLOURS[region]
        d.ellipse([lx, ly + 1, lx + 8, ly + 9], fill=col)
        d.text((lx + 11, ly), region, font=f_leg, fill=INK)
        lx += 11 + f_leg.getlength(region) + 12
        if lx > mx + mw - 90:
            lx = mx
            ly += 13
    return y + h


# ---------------------------------------------------------------- index + footer
def draw_index(d, x, y, w, h):
    f_title = f_sans_b(11)
    d.text((x, y), "ALSO ON TUESDAY 17 NOVEMBER", font=f_title, fill=NAVY)
    d.line([x, y + 16, x + w, y + 16], fill=RULE, width=1)
    f_idx = f_sans(10)
    f_num = f_sans_b(10)
    col_w = (w - 12) / 2
    left = INDEX[:17]
    right = INDEX[17:]
    ly = y + 20
    lh = 12
    for col_idx, col_items in enumerate((left, right)):
        cx = x + col_idx * (col_w + 12)
        cy = ly
        for n, line in col_items:
            d.text((cx, cy), str(n), font=f_num, fill=OCHRE)
            d.text((cx + 20, cy), line, font=f_idx, fill=INK)
            cy += lh
    return y + h


def draw_footer(d, y):
    f = f_sans(10)
    line1 = ("Every story here happened or was first reported on Tuesday "
             "17 November 2026. Contested claims are marked as claims.")
    line2 = ("DATE CHECK — Left out on purpose: stories that broke before "
             "Tuesday. Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. "
             "Original drawings.")
    centred(d, W // 2, y, line1, f, GREY)
    centred(d, W // 2, y + 12, line2, f, GREY)
    return y + 24


# ---------------------------------------------------------------- main
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # outer border
    d.rectangle([3, 3, W - 4, H - 4], outline=RULE, width=3)
    y = 12
    y = draw_kicker(d, y)
    y = draw_masthead(d, y + 2)
    y = draw_stats(d, y + 4)
    y = draw_leads(d, y + 4)
    y = draw_grid(d, y + 6)
    # bottom: map left, index right
    bottom_y = y + 4
    bottom_h = 230
    d.line([10, bottom_y, W - 10, bottom_y], fill=RULE, width=2)
    map_w = 400
    draw_map(d, 10, bottom_y + 6, map_w, bottom_h)
    d.line([10 + map_w + 10, bottom_y + 6, 10 + map_w + 10,
            bottom_y + bottom_h], fill=(190, 180, 160), width=1)
    draw_index(d, 10 + map_w + 22, bottom_y + 6, W - 10 - (10 + map_w + 22),
               bottom_h)
    fy = bottom_y + bottom_h + 4
    d.line([10, fy, W - 10, fy], fill=RULE, width=2)
    draw_footer(d, fy + 5)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img = build()
    img.save(out_path, format="PNG")
    data = open(out_path, "rb").read()
    print(f"wrote {out_path}")
    print(f"size: {len(data)} bytes")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    print(f"dimensions: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    sys.exit(main())
