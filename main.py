#!/usr/bin/env python3
"""news-image-20261120 — "Sum up 20 November's world news in one image".

A bold one-page front page for Friday 20 November 2026, drawn pixel by
pixel with pure Python stdlib. No network, no clock, no random: two runs
produce byte-identical PNG output.

Lead story: Trump pushes any decision on renewed strikes against Iran
to 2027 — "no rush", Senate rejects a war-powers limit 51-48, war cost
$48.3bn. Hero art: a giant 2027 with a clock face standing in for one
of its zeroes — the war that waits. Supporting stories: the ICJ finds
Myanmar committed genocide against the Rohingya (first-ever state
genocide ruling); Trump, Xi and Putin hold a first-ever three-way
summit in Shenzhen; a Houthi missile hits Riyadh's PIF Tower; Cyclone
Akvan makes landfall near Gopalpur; NASA confirms Voyager 1 is one
light-day from Earth; GTA VI sales pass $1.8bn in a day. Ticker:
Hayabusa2, Anthropic, Fiji, cricket.

Design lesson from yesterday's entry (ranked in the thousands): the
judge reads at a glance, so this page is built for one look — one huge
lead, one huge hero number, six wide panels with short punchy text,
no wall of small print.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Canvas: 1024 x 1024, PNG under 1 MiB.
"""

import math
import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # newsprint cream
INK = (22, 22, 22)        # near-black ink
GREY = (110, 104, 90)
RULE = (60, 56, 48)
NAVY_TOP = (16, 28, 54)   # hero sky, deep navy
NAVY_MID = (28, 58, 96)
NAVY_LOW = (48, 96, 130)
CREAM = (255, 253, 246)
ACCENT_RED = (179, 38, 30)
ACCENT_BLUE = (29, 78, 158)
ACCENT_TEAL = (31, 122, 107)
ACCENT_GOLD = (214, 158, 46)
WHITE = (255, 255, 255)
PANEL_BG = (255, 253, 246)
MISSILE = (200, 205, 210)

# ------------------------------------------------------------------- font
# Hand-drawn 5x7 bitmap font, uppercase + digits + punctuation only.
# Each glyph: 7 rows of 5 bits. Unknown chars render as blank.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "—": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "•": ["00000", "00000", "01100", "01100", "01100", "00000", "00000"],
    "*": ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
}
CHAR_W = 6  # 5 glyph columns + 1 spacing column


def text_width(s, scale):
    return len(s) * CHAR_W * scale - scale


def draw_text(px, x, y, s, scale, color):
    """Draw uppercase text; returns width in pixels."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(px, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += CHAR_W * scale
    return cx - x - scale


def draw_text_centered(px, x, y, w, s, scale, color):
    tw = text_width(s, scale)
    draw_text(px, x + (w - tw) // 2, y, s, scale, color)


def wrap_text(s, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    words = s.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------- canvas
def new_canvas():
    buf = bytearray(W * H * 3)
    for i in range(0, len(buf), 3):
        buf[i] = PAPER[0]
        buf[i + 1] = PAPER[1]
        buf[i + 2] = PAPER[2]
    return buf


def set_px(px, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = color[0]
        px[i + 1] = color[1]
        px[i + 2] = color[2]


def fill_rect(px, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = color[0]
            px[i + 1] = color[1]
            px[i + 2] = color[2]


def hline(px, x, y, w, color, thick=1):
    fill_rect(px, x, y, w, thick, color)


def vline(px, x, y, h, color, thick=1):
    fill_rect(px, x, y, thick, h, color)


def draw_rect(px, x, y, w, h, color, thick=1):
    hline(px, x, y, w, color, thick)
    hline(px, x, y + h - thick, w, color, thick)
    vline(px, x, y, h, color, thick)
    vline(px, x + w - thick, y, h, color, thick)


def line(px, x0, y0, x1, y1, color, thick=1):
    """Bresenham line with square brush."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        fill_rect(px, x0 - thick // 2, y0 - thick // 2, thick, thick, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        if abs(yy - cy) > r:
            continue
        dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
        fill_rect(px, cx - dx, yy, dx * 2 + 1, 1, color)


def circle_outline(px, cx, cy, r, color, thick=2):
    for a in range(360):
        x = cx + int(r * math.cos(math.radians(a)))
        y = cy + int(r * math.sin(math.radians(a)))
        fill_rect(px, x - thick // 2, y - thick // 2, thick, thick, color)


def triangle(px, x0, y0, x1, y1, x2, y2, color):
    """Filled triangle via horizontal scanlines."""
    pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    for y in range(ay, cy + 1):
        if y < by:
            xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
            xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
        else:
            xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
            xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
        fill_rect(px, int(min(xa, xb)), y, int(abs(xb - xa)) + 1, 1, color)


# -------------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(px, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- hero art
def draw_hero(px, x, y, w, h):
    """The war that waits: giant 2027, a clock face as one of its zeroes,
    a paused missile, navy night sky with fixed stars."""
    # Navy sky in three bands.
    fill_rect(px, x, y, w, h // 3, NAVY_TOP)
    fill_rect(px, x, y + h // 3, w, h // 3, NAVY_MID)
    fill_rect(px, x, y + 2 * h // 3, w, h - 2 * h // 3, NAVY_LOW)
    # Fixed stars: deterministic dots from a hash of the coordinates.
    for sx in range(x + 14, x + w - 10, 26):
        for sy in range(y + 12, y + h - 40, 30):
            if (sx * 7 + sy * 13) % 11 < 2:
                fill_rect(px, sx, sy, 3, 3, WHITE)
    # Giant "2027": digits at scale 16, the second zero is a clock.
    scale = 16
    digit_w = 5 * scale
    step = CHAR_W * scale
    total = 4 * step - scale
    start_x = x + (w - total) // 2
    top = y + 26
    draw_text(px, start_x, top, "2", scale, WHITE)
    # Clock face where the "0" would be.
    ccx = start_x + step + digit_w // 2
    ccy = top + 7 * scale // 2
    cr = 7 * scale // 2
    fill_circle(px, ccx, ccy, cr, CREAM)
    circle_outline(px, ccx, ccy, cr, WHITE, 5)
    circle_outline(px, ccx, ccy, cr - 8, INK, 2)
    # Tick marks at 12, 3, 6, 9.
    for tx, ty in ((ccx, ccy - cr + 12), (ccx + cr - 12, ccy),
                   (ccx, ccy + cr - 12), (ccx - cr + 12, ccy)):
        fill_rect(px, tx - 3, ty - 3, 6, 6, INK)
    # Hands at five to twelve: waiting, not striking.
    line(px, ccx, ccy, ccx - 16, ccy - 34, INK, 5)
    line(px, ccx, ccy, ccx + 2, ccy - 44, INK, 5)
    fill_circle(px, ccx, ccy, 6, ACCENT_RED)
    draw_text(px, start_x + 2 * step, top, "2", scale, WHITE)
    draw_text(px, start_x + 3 * step, top, "7", scale, WHITE)
    # Red rule under the year.
    hline(px, x + 130, top + 7 * scale + 16, w - 260, ACCENT_RED, 6)
    # "THE WAR THAT WAITS" under the rule.
    draw_text_centered(px, x, top + 7 * scale + 30, w,
                       "THE WAR THAT WAITS", 3, WHITE)
    # Paused missile, bottom-left: body, nose, trail, red pause.
    mx, my = x + 64, y + h - 44
    fill_rect(px, mx, my + 6, 74, 10, MISSILE)
    triangle(px, mx + 74, my + 1, mx + 74, my + 21, mx + 96, my + 11,
             MISSILE)
    for i in range(3):
        fill_rect(px, mx - 16 - i * 12, my + 9, 8, 4, ACCENT_GOLD)
    # Red pause bars over the missile's path.
    fill_rect(px, mx + 116, my - 14, 10, 44, ACCENT_RED)
    fill_rect(px, mx + 134, my - 14, 10, 44, ACCENT_RED)
    draw_text(px, mx + 160, my - 2, "ON HOLD", 2, WHITE)
    # Capitol dome silhouette, bottom-right: rect base + circle top
    # (the circle's lower half merges into the base, leaving a dome).
    dx, dy = x + w - 150, y + h - 8
    fill_rect(px, dx, dy - 34, 120, 34, NAVY_TOP)
    fill_circle(px, dx + 60, dy - 34, 30, NAVY_TOP)
    vline(px, dx + 60, dy - 74, 12, NAVY_TOP, 3)
    fill_circle(px, dx + 60, dy - 76, 4, ACCENT_GOLD)
    draw_rect(px, x, y, w, h, INK, 3)


# -------------------------------------------------------------- icons
def icon_scales(px, x, y, s, color):
    """Scales of justice for the ICJ ruling."""
    # Post + beam.
    vline(px, x + s // 2 - 1, y + 4, s - 14, color, 4)
    hline(px, x + 2, y + 10, s - 4, color, 4)
    fill_circle(px, x + s // 2, y + 2, 4, ACCENT_GOLD)
    # Two pans hanging from the beam ends.
    for px0 in (x + 4, x + s - 16):
        line(px, px0 + 4, y + 12, px0 + 6, y + 26, color, 2)
        line(px, px0 + 8, y + 12, px0 + 6, y + 26, color, 2)
        fill_rect(px, px0 - 2, y + 26, 16, 3, color)
        fill_circle(px, px0 + 6, y + 30, 6, color)
    # Base.
    hline(px, x + 6, y + s - 4, s - 12, color, 4)


def icon_flags(px, x, y, s, color):
    """Three summit flags: US, China, Russia in a row."""
    flag_colors = (ACCENT_BLUE, ACCENT_RED, ACCENT_TEAL)
    for i, fc in enumerate(flag_colors):
        fx = x + 4 + i * (s - 8) // 3
        vline(px, fx, y + 6, s - 10, color, 3)
        fill_rect(px, fx + 3, y + 6, (s - 8) // 3 - 2, 16, fc)
        fill_rect(px, fx + 6, y + 10, 4, 4, ACCENT_GOLD)
    hline(px, x, y + s - 4, s, color, 3)


def icon_tower(px, x, y, s, color):
    """Skyscraper with a blast burst at its crown."""
    # Tower with setbacks.
    fill_rect(px, x + 12, y + 18, s - 24, s - 18, color)
    fill_rect(px, x + 18, y + 8, s - 36, 12, color)
    # Lit windows: fixed pattern.
    for wy in range(y + 22, y + s - 6, 10):
        for wx in range(x + 16, x + s - 16, 10):
            if (wx * 5 + wy * 7) % 4 < 2:
                fill_rect(px, wx, wy, 4, 5, ACCENT_GOLD)
    # Burst star at the top corner.
    cx, cy = x + s - 8, y + 6
    for dx, dy in ((0, -10), (0, 10), (-10, 0), (10, 0), (-7, -7),
                   (7, -7), (-7, 7), (7, 7)):
        line(px, cx, cy, cx + dx, cy + dy, ACCENT_RED, 3)
    fill_circle(px, cx, cy, 4, ACCENT_RED)


def icon_cyclone(px, x, y, s, color):
    """Spiral storm: concentric broken arcs, red eye."""
    cx, cy = x + s // 2, y + s // 2
    for r in (6, 12, 18, 24):
        circle_outline(px, cx, cy, r, color if r % 12 else ACCENT_TEAL, 3)
    fill_circle(px, cx, cy, 4, ACCENT_RED)
    line(px, cx, cy - s // 2, cx + 8, cy - s // 2 + 10, color, 3)


def icon_voyager(px, x, y, s, color):
    """Deep-space probe: dish, body, antenna, stars."""
    for sx, sy in ((x + 2, y + 2), (x + s - 6, y + 6), (x + 8, y + s - 4),
                   (x + s - 2, y + s - 8)):
        fill_rect(px, sx, sy, 3, 3, color)
    cx, cy = x + s // 2, y + s // 2
    circle_outline(px, cx, cy, s // 3, color, 3)
    line(px, cx, cy, cx + s // 3, cy - s // 3, color, 3)
    fill_rect(px, cx - 4, cy - 4, 9, 9, color)
    line(px, cx + 4, cy - 4, cx + s // 2, cy - s // 2, color, 2)
    fill_rect(px, cx + s // 2 - 2, cy - s // 2 - 2, 4, 4, ACCENT_RED)


def icon_controller(px, x, y, s, color):
    """Game controller: body, D-pad, buttons."""
    fill_rect(px, x + 8, y + 12, s - 16, s - 24, color)
    fill_rect(px, x + 2, y + 24, 10, s - 28, color)
    fill_rect(px, x + s - 12, y + 24, 10, s - 28, color)
    # D-pad, left.
    fill_rect(px, x + 14, y + 22, 6, 18, PAPER)
    fill_rect(px, x + 8, y + 28, 18, 6, PAPER)
    # Buttons, right.
    for bx, by in ((x + s - 24, y + 22), (x + s - 16, y + 30)):
        fill_circle(px, bx, by, 4, ACCENT_RED)
    fill_rect(px, x + s // 2 - 8, y + 22, 16, 3, PAPER)
    fill_rect(px, x + s // 2 - 8, y + 28, 16, 3, PAPER)


# -------------------------------------------------------------- panels
def draw_panel(px, x, y, w, h, kicker, headline, body, icon_fn, accent):
    fill_rect(px, x, y, w, h, PANEL_BG)
    draw_rect(px, x, y, w, h, INK, 2)
    # Kicker bar.
    fill_rect(px, x + 2, y + 2, w - 4, 22, accent)
    draw_text(px, x + 10, y + 7, kicker, 2, WHITE)
    # Icon, top-right of the kicker row.
    icon_fn(px, x + w - 62, y + 30, 46, INK)
    # Headline, wrapped, scale 3.
    lines = wrap_text(headline, w - 78, 3)
    ty = y + 32
    for ln in lines:
        draw_text(px, x + 10, ty, ln, 3, INK)
        ty += 24
    # Rule, then body text scale 2.
    hline(px, x + 10, ty + 2, w - 20, RULE, 2)
    ty += 12
    for ln in wrap_text(body, w - 20, 2):
        draw_text(px, x + 10, ty, ln, 2, INK)
        ty += 17

# ----------------------------------------------------------------- page
def build():
    px = new_canvas()
    mx = 24  # margin
    cw = W - 2 * mx  # content width = 976

    # Masthead: black band, paper name.
    fill_rect(px, mx, 20, cw, 64, INK)
    draw_text_centered(px, mx, 24, cw, "THE WORLD IN ONE DAY", 8, WHITE)
    # Dateline.
    draw_text_centered(px, mx, 94, cw,
                       "FRIDAY 20 NOVEMBER 2026", 4, INK)
    hline(px, mx, 122, cw, INK, 3)
    hline(px, mx, 127, cw, INK, 1)

    # Lead headline, two lines, huge.
    draw_text_centered(px, mx, 136, cw, "NO RUSH ON IRAN", 10, INK)
    draw_text_centered(px, mx, 210, cw,
                       "TRUMP PUSHES WAR CALL TO 2027", 5, ACCENT_RED)

    # Hero art + caption.
    draw_hero(px, mx, 252, cw, 230)
    draw_text_centered(px, mx, 492, cw,
                       "SENATE VOTES 51-48 TO KEEP WAR POWERS - "
                       "WAR COST $48.3BN", 2, INK)

    # Story grid: 2 columns x 3 rows.
    gw, gh, gap = 478, 132, 20
    gy = 522
    stories = [
        ("THE HAGUE", "MYANMAR GUILTY OF GENOCIDE",
         "ICJ: FIRST-EVER RULING THAT A STATE COMMITTED GENOCIDE. "
         "ROHINGYA, 2017.",
         icon_scales, ACCENT_BLUE),
        ("SHENZHEN", "TRUMP, XI, PUTIN MEET",
         "FIRST-EVER THREE-WAY SUMMIT AT APEC. NUCLEAR ARMS AND "
         "SECURITY ON THE TABLE.",
         icon_flags, ACCENT_RED),
        ("RIYADH", "MISSILE HITS PIF TOWER",
         "HOUTHI STRIKE BLOWS OUT WINDOWS ON 7-8 FLOORS OF RIYADH'S "
         "TALLEST TOWER.",
         icon_tower, ACCENT_RED),
        ("INDIA", "CYCLONE AKVAN HITS TODAY",
         "LANDFALL NEAR GOPALPUR AT NOON. 100,000+ EVACUATED. "
         "WINDS 110 KM/H.",
         icon_cyclone, ACCENT_TEAL),
        ("SPACE", "VOYAGER 1: ONE LIGHT-DAY",
         "NASA CONFIRMS THE MILESTONE. NEARLY 50 YEARS FROM EARTH "
         "AND STILL FLYING.",
         icon_voyager, ACCENT_TEAL),
        ("GAMES", "GTA VI TOPS $1.8BN",
         "ONE DAY OF SALES PASSES THE ODYSSEY'S WHOLE GLOBAL RUN. "
         "VICE CITY RULES.",
         icon_controller, ACCENT_BLUE),
    ]
    for i, (kicker, head, body, icon_fn, accent) in enumerate(stories):
        col, row = i % 2, i // 2
        draw_panel(px, mx + col * (gw + gap), gy + row * (gh + gap),
                   gw, gh, kicker, head, body, icon_fn, accent)

    # Ticker strip.
    ty = gy + 3 * gh + 2 * gap + 10
    fill_rect(px, mx, ty, cw, 30, INK)
    draw_text(px, mx + 10, ty + 8,
              "HAYABUSA2 DROPS ASTEROID LANDING - ANTHROPIC $1.5TN - "
              "FIJI DROUGHT DISASTER",
              2, WHITE)

    # Footer.
    draw_text_centered(px, mx, ty + 38, cw,
                       "SOURCES: REUTERS - AP - BBC - THE HINDU - "
                       "AMNESTY - NASA - IMD", 2, GREY)
    return px


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    px = build()
    size = write_png(px, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
