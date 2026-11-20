#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- Friday 20 November 2026.

A one-page newspaper front page that sums up the day's world news in a
single 1024x1024 PNG. Pure Python standard library, no network, fully
deterministic: two runs write byte-identical files.

Layout, top to bottom:
  * masthead band -- THE WORLD IN ONE DAY
  * dateline -- FRIDAY 20 NOVEMBER 2026
  * lead headline -- TRUMP, XI, PUTIN / DECLARE PEACE
  * lead art panel -- globe, the three flags, the four points
  * four supporting stories in a 2x2 grid
  * wire ticker with the rest of the day
  * sources footer

Run:  python3 main.py            (writes /output/entry.png)
  or:  ENTRY_OUT=entry.png python3 main.py
"""

import hashlib
import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 229)
INK = (20, 20, 20)
NAVY = (22, 41, 77)
NAVY_DARK = (15, 29, 56)
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 193, 90)
RED = (163, 31, 31)
RED_BRIGHT = (178, 32, 32)
BLUE = (29, 78, 158)
TEAL = (14, 122, 107)
GREEN = (31, 122, 51)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LEAF = (143, 181, 115)
FLAG_BLUE = (60, 59, 110)
FLAG_RED = (178, 34, 52)
CHINA_RED = (222, 41, 16)
STAR_YELLOW = (255, 222, 89)
RUSSIA_BLUE = (0, 57, 166)
RUSSIA_RED = (213, 43, 30)


# ------------------------------------------------------------------- font
# A chunky 5x7 pixel font, drawn one pixel at a time. Every glyph is seven
# rows of five cells; "1" is ink, "0" is paper. Lowercase is folded to
# uppercase at render time.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

# Unit outline of a five-pointed star, centred on (0, 0), radius 10.
STAR_POINTS = (
    (0, -10), (2, -3), (9, -4), (4, 2), (6, 9),
    (0, 5), (-6, 9), (-4, 2), (-9, -4), (-2, -3),
)


# ------------------------------------------------------------------ canvas
class Canvas:
    """A plain RGB pixel buffer with a few integer drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def hline(self, x1, x2, y, color, t=1):
        if x2 < x1:
            x1, x2 = x2, x1
        for yy in range(y, y + t):
            for xx in range(x1, x2 + 1):
                self.set(xx, yy, color)

    def vline(self, x, y1, y2, color, t=1):
        if y2 < y1:
            y1, y2 = y2, y1
        for xx in range(x, x + t):
            for yy in range(y1, y2 + 1):
                self.set(xx, yy, color)

    def line(self, x1, y1, x2, y2, color):
        """Bresenham line, one pixel thick."""
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        x, y = x1, y1
        while True:
            self.set(x, y, color)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def outline(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def circle(self, cx, cy, r, color, t=1):
        for rr in range(r, r + t):
            for dy in range(-rr, rr + 1):
                dx = int(math.sqrt(max(0, rr * rr - dy * dy)))
                self.set(cx - dx, cy + dy, color)
                self.set(cx + dx, cy + dy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        steps = max(rx, ry) * 6
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            x = cx + int(rx * math.cos(a))
            y = cy + int(ry * math.sin(a))
            self.set(x, y, color)

    def ellipse_fill(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            span = int(rx * math.sqrt(max(0.0, 1.0 - (dy / ry) ** 2)))
            self.hline(cx - span, cx + span, cy + dy, color)

    def poly(self, points, color):
        """Scanline-filled polygon; points are (x, y) integer pairs."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(math.ceil(xs[j])), int(math.floor(xs[j + 1])), y, color)

    def star(self, cx, cy, s, color):
        pts = [(cx + int(px * s / 10.0), cy + int(py * s / 10.0))
               for (px, py) in STAR_POINTS]
        self.poly(pts, color)


# -------------------------------------------------------------------- text
def text_width(s, scale, spacing=1):
    return len(s) * (5 + spacing) * scale - spacing * scale


def draw_text(cv, x, y, s, scale, color, align="left", spacing=1):
    """Draw one line of the pixel font. Returns the pixel width used."""
    s = s.upper()
    width = text_width(s, scale, spacing)
    if align == "center":
        x -= width // 2
    elif align == "right":
        x -= width
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    cv.rect(cx + col_i * scale, y + row_i * scale,
                            scale, scale, color)
        cx += (5 + spacing) * scale
    return width


def wrap(s, scale, max_w, spacing=1):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    pitch = (5 + spacing) * scale
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) * pitch - spacing * scale <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, s, scale, color, max_w, line_gap, align="left"):
    for i, line in enumerate(wrap(s, scale, max_w)):
        draw_text(cv, x, y + i * (7 * scale + line_gap), line, scale,
                  color, align=align)
    return len(wrap(s, scale, max_w))


# -------------------------------------------------------------------- icons
def icon_scales(cv, x, y, color):
    """Tiny scales of justice, 20x20, drawn in white on a kicker bar."""
    cv.vline(x + 10, y + 1, y + 16, color)
    cv.hline(x + 2, x + 18, y + 3, color)
    cv.hline(x + 1, x + 19, y + 18, color)
    cv.line(x + 3, y + 3, x + 1, y + 10, color)
    cv.line(x + 3, y + 3, x + 5, y + 10, color)
    cv.line(x + 17, y + 3, x + 15, y + 10, color)
    cv.line(x + 17, y + 3, x + 19, y + 10, color)
    cv.hline(x + 1, x + 5, y + 10, color)
    cv.hline(x + 15, x + 19, y + 10, color)


def icon_cyclone(cv, x, y, color):
    """Concentric spiral rings for the cyclone story."""
    cv.circle(x + 10, y + 10, 8, color)
    cv.circle(x + 10, y + 10, 5, color)
    cv.disc(x + 10, y + 10, 2, color)


def icon_capitol(cv, x, y, color):
    """A domed capitol front for the Washington story."""
    cv.ellipse_fill(x + 10, y + 7, 8, 5, color)
    cv.rect(x + 2, y + 7, 16, 2, color)
    cv.rect(x + 4, y + 9, 2, 7, color)
    cv.rect(x + 9, y + 9, 2, 7, color)
    cv.rect(x + 14, y + 9, 2, 7, color)
    cv.rect(x + 1, y + 16, 18, 2, color)


def icon_chart(cv, x, y, color):
    """Three rising bars and an arrow for the markets story."""
    cv.rect(x + 2, y + 12, 4, 6, color)
    cv.rect(x + 8, y + 8, 4, 10, color)
    cv.rect(x + 14, y + 3, 4, 15, color)
    cv.line(x + 1, y + 13, x + 19, y + 2, color)


# -------------------------------------------------------------------- flags
def flag_usa(cv, x, y, w, h):
    stripe = max(1, h // 13)
    for i in range(13):
        color = FLAG_RED if i % 2 == 0 else WHITE
        cv.rect(x, y + i * stripe, w, stripe, color)
    canton_w = int(w * 0.4)
    canton_h = stripe * 7
    cv.rect(x, y, canton_w, canton_h, FLAG_BLUE)
    for row in range(4):
        for col in range(5):
            cv.disc(x + 8 + col * 14, y + 5 + row * 8, 1, WHITE)


def flag_china(cv, x, y, w, h):
    cv.rect(x, y, w, h, CHINA_RED)
    cv.star(x + 34, y + 30, 15, STAR_YELLOW)
    for sx, sy in ((68, 16), (82, 26), (82, 44), (68, 54)):
        cv.star(x + sx, y + sy, 6, STAR_YELLOW)


def flag_russia(cv, x, y, w, h):
    band = h // 3
    cv.rect(x, y, w, band, WHITE)
    cv.rect(x, y + band, w, band, RUSSIA_BLUE)
    cv.rect(x, y + 2 * band, w, h - 2 * band, RUSSIA_RED)


# -------------------------------------------------------------------- scene
def build():
    cv = Canvas(W, H, PAPER)

    # Paper frame: a heavy outer rule and a hairline inner rule.
    cv.outline(10, 10, W - 20, H - 20, INK, 3)
    cv.outline(18, 18, W - 36, H - 36, INK, 1)

    # ---- masthead ------------------------------------------------------
    cv.rect(24, 26, 976, 92, NAVY)
    draw_text(cv, 512, 47, "THE WORLD IN ONE DAY", 7, WHITE, align="center")
    cv.rect(24, 112, 976, 4, GOLD)

    # ---- dateline ------------------------------------------------------
    draw_text(cv, 512, 130, "FRIDAY 20 NOVEMBER 2026", 3, RED,
              align="center")
    cv.hline(60, 268, 139, INK, 2)
    cv.hline(756, 964, 139, INK, 2)

    # ---- lead headline -------------------------------------------------
    draw_text(cv, 512, 156, "TRUMP, XI, PUTIN", 8, INK, align="center")
    draw_text(cv, 512, 220, "DECLARE PEACE", 8, RED_BRIGHT, align="center")

    # ---- lead deck -----------------------------------------------------
    draw_text(cv, 512, 288, "FIRST-EVER THREE-WAY SUMMIT IN SHENZHEN",
              3, INK, align="center")
    draw_text(cv, 512, 313, "FOUR-POINT PACT \u2014 BUT NO WORD ON UKRAINE OR IRAN",
              3, INK, align="center")

    # ---- lead art panel ------------------------------------------------
    px, py, pw, ph = 28, 344, 968, 240
    cv.rect(px, py, pw, ph, NAVY)
    cv.outline(px, py, pw, ph, GOLD, 2)
    for sx, sy in ((60, 368), (300, 366), (960, 368), (980, 420), (60, 562),
                   (310, 560), (960, 562), (292, 420), (956, 500), (70, 470),
                   (318, 470), (700, 366), (52, 420), (972, 368)):
        cv.disc(sx, sy, 2, WHITE)
    draw_text(cv, 512, 362, "THE THREE AT THE TABLE", 2, GOLD_LIGHT,
              align="center")

    # Globe on the left of the panel.
    gx, gy, gr = 200, 462, 70
    cv.circle(gx, gy, gr, WHITE, 3)
    cv.ellipse(gx, gy, 28, gr, WHITE)
    cv.ellipse(gx, gy, gr, 26, WHITE)
    cv.hline(gx - gr, gx + gr, gy, WHITE)
    cv.ellipse_fill(gx - 24, gy - 22, 16, 9, LEAF)
    cv.ellipse_fill(gx + 22, gy + 14, 13, 8, LEAF)
    cv.ellipse_fill(gx - 12, gy + 30, 10, 6, LEAF)

    # The three flags, side by side, meeting at the globe.
    flags = ((330, flag_usa, "USA"),
             (540, flag_china, "CHINA"),
             (750, flag_russia, "RUSSIA"))
    for fx, draw_flag, label in flags:
        draw_flag(cv, fx, 400, 190, 90)
        cv.outline(fx, 400, 190, 90, WHITE, 2)
        draw_text(cv, fx + 95, 498, label, 2, WHITE, align="center")

    # The four points of the declaration, in one gold line.
    draw_text(cv, 512, 544,
              "UN REFORM \u2022 FUEL FOR ALL \u2022 STATE IMMUNITY "
              "\u2022 NUCLEAR-RISK TALKS",
              2, GOLD_LIGHT, align="center")

    # ---- supporting stories, 2x2 grid ----------------------------------
    stories = (
        # kicker, colour, icon, headline, deck
        ("THE HAGUE", BLUE, icon_scales,
         "MYANMAR GUILTY OF GENOCIDE",
         "ICJ: FIRST RULING EVER THAT A STATE COMMITTED GENOCIDE. "
         "ROHINGYA, 2017."),
        ("INDIA", TEAL, icon_cyclone,
         "CYCLONE AKVAN HITS TODAY",
         "LANDFALL NEAR GOPALPUR AT NOON. 300,000+ EVACUATED. "
         "WINDS 110 KM/H."),
        ("WASHINGTON", RED, icon_capitol,
         "SENATE KEEPS IRAN WAR GOING",
         "WAR-POWERS BID FAILS 51-48. PENTAGON: WAR HAS COST $48.3BN."),
        ("MARKETS", GREEN, icon_chart,
         "ANTHROPIC'S $81BN IPO",
         "BIGGEST LISTING EVER. SHARES JUMP 34% ON DEBUT. "
         "VALUED AT $1.5TN."),
    )
    cell_w, cell_h, gap = 472, 148, 24
    origin_x, origin_y = 28, 600
    for i, (kicker, color, icon, headline, deck) in enumerate(stories):
        cx = origin_x + (i % 2) * (cell_w + gap)
        cy = origin_y + (i // 2) * (cell_h + 12)
        cv.rect(cx, cy, cell_w, cell_h, WHITE)
        cv.outline(cx, cy, cell_w, cell_h, INK, 2)
        cv.rect(cx, cy, cell_w, 26, color)
        draw_text(cv, cx + 10, cy + 6, kicker, 2, WHITE)
        icon(cv, cx + cell_w - 30, cy + 3, WHITE)
        draw_wrapped(cv, cx + 10, cy + 36, headline, 4, INK,
                     cell_w - 20, 4)
        draw_wrapped(cv, cx + 10, cy + 104, deck, 2, INK,
                     cell_w - 20, 3)

    # ---- wire ticker ----------------------------------------------------
    ty = 920
    cv.rect(28, ty, 968, 56, INK)
    draw_text(cv, 512, ty + 8,
              "HAITI: 34 KILLED IN GANG OFFENSIVE  \u2022  VENEZUELA SIGNS "
              "US MILITARY DEAL",
              2, WHITE, align="center")
    draw_text(cv, 512, ty + 30,
              "UKRAINE HITS CRIMEA BRIDGE  \u2022  FIJI DROUGHT DISASTER  "
              "\u2022  SEOUL CLEARS EX-PM HAN",
              2, WHITE, align="center")

    # ---- sources --------------------------------------------------------
    draw_text(cv, 512, 986,
              "SOURCES: REUTERS \u2022 AP \u2022 BBC \u2022 CFR \u2022 IMD "
              "\u2022 BLOOMBERG",
              2, GREY, align="center")

    return cv


# ---------------------------------------------------------------------- png
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none, every row
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


def write_png(path, cv):
    data = encode_png(cv)
    with open(path, "wb") as f:
        f.write(data)
    return data


def main():
    out = os.environ.get("ENTRY_OUT", "/output/entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    data = encode_png(build())
    digest = hashlib.sha256(data).hexdigest()
    size = len(data)
    if size > 1024 * 1024:
        print(f"ERROR: {size} bytes, over the 1 MiB cap — not written",
              file=sys.stderr)
        return 1
    with open(out, "wb") as f:
        f.write(data)
    print(f"wrote {out}  {size} bytes  sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
