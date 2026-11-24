"""World news cover for Tuesday 24 November 2026.

Draws a 1024x1024 newspaper front page with its own 5x7 bitmap font
and its own PNG writer. Standard library only, no network, fully
deterministic: two runs write identical bytes.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 229)
INK = (24, 24, 28)
NAVY = (22, 35, 63)
NAVY_LT = (38, 58, 96)
GOLD = (198, 156, 66)
RED = (178, 34, 34)
GREY = (96, 96, 100)
BLUE = (52, 110, 168)
SKY = (178, 214, 235)
SEA = (36, 84, 138)
ORANGE = (232, 126, 32)
WHITE = (250, 250, 246)

FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(bg * w * h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, color)

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, color)

    def ring(self, cx, cy, r, color, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.px(xx, yy, color)

    def poly(self, pts, color):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.px(x, y, color)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def wrap(self, s, scale, max_w):
        words = s.upper().split()
        lines = []
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def block(self, x, y, s, scale, color, max_w, leading, max_lines=None):
        lines = self.wrap(s, scale, max_w)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * leading, ln, scale, color)
        return len(lines)


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def save_png(path, cv):
    raw = b"".join(
        b"\x00" + bytes(cv.pix[y * cv.w * 3:(y + 1) * cv.w * 3])
        for y in range(cv.h))
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)


def draw_ship(cv, x0, y0, x1, y1):
    """Warship at sea with a blast above it, inside the given box."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, SKY)
    cv.rect(x0, y1 - 62, x1 - x0, 62, SEA)
    # waves
    for k in range(3):
        wy = y1 - 48 + k * 18
        for xx in range(x0, x1, 8):
            cv.rect(xx, wy + (4 if (xx // 8) % 2 else 0), 8, 3, WHITE)
    # hull
    hull = [(x0 + 30, y1 - 62), (x1 - 30, y1 - 62),
            (x1 - 70, y1 - 26), (x0 + 70, y1 - 26)]
    cv.poly(hull, INK)
    # deck + superstructure
    cv.rect(x0 + 90, y1 - 118, 150, 56, NAVY_LT)
    cv.rect(x0 + 120, y1 - 152, 40, 34, NAVY_LT)
    cv.rect(x0 + 250, y1 - 96, 12, 34, INK)
    # blast: orange core, yellow heart, dark smoke
    bx, by = x0 + 290, y0 + 62
    cv.circle(bx, by, 44, (70, 70, 74))
    cv.circle(bx, by, 34, ORANGE)
    cv.circle(bx, by, 20, GOLD)
    cv.circle(bx, by, 9, WHITE)
    for dx, dy in ((-58, -18), (56, -26), (-40, 30), (48, 22), (0, -56)):
        cv.circle(bx + dx, by + dy, 10, ORANGE)
    # small drone boat on the water
    cv.rect(x0 + 36, y1 - 52, 46, 12, RED)
    cv.line(x0 + 36, y1 - 52, x0 + 82, y1 - 40, RED)


def icon_stars(cv, x, y, s):
    cv.rect(x, y, s, s, NAVY)
    cx, cy = x + s // 2, y + s // 2
    r = s // 2 - 10
    for k in range(12):
        import math
        a = math.pi * 2 * k / 12 - math.pi / 2
        cv.circle(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)),
                  4, GOLD)


def icon_bars(cv, x, y, s):
    cv.rect(x, y, s, s, (232, 226, 210))
    base = y + s - 12
    for i, h in enumerate((26, 44, 62)):
        cv.rect(x + 12 + i * 20, base - h, 14, h, RED if i == 2 else NAVY)


def icon_factory(cv, x, y, s):
    cv.rect(x, y, s, s, (232, 226, 210))
    cv.rect(x + 10, y + s - 34, s - 20, 24, GREY)
    cv.rect(x + 12, y + 14, 10, s - 40, GREY)
    cv.circle(x + 17, y + 8, 6, GREY)
    for i in range(3):
        cv.rect(x + 16 + i * 16, y + s - 26, 8, 8, PAPER)


def icon_chip(cv, x, y, s):
    cv.rect(x, y, s, s, (232, 226, 210))
    cv.rect(x + 16, y + 16, s - 32, s - 32, NAVY)
    cv.rect(x + 28, y + 28, s - 56, s - 56, GOLD)
    for i in range(4):
        cv.rect(x + 20 + i * 12, y + 8, 5, 8, INK)
        cv.rect(x + 20 + i * 12, y + s - 16, 5, 8, INK)
        cv.rect(x + 8, y + 20 + i * 12, 8, 5, INK)
        cv.rect(x + s - 16, y + 20 + i * 12, 8, 5, INK)


def icon_globe(cv, x, y, s):
    cv.rect(x, y, s, s, (232, 226, 210))
    cx, cy = x + s // 2, y + s // 2
    cv.ring(cx, cy, s // 2 - 6, BLUE, 4)
    cv.line(cx - s // 2 + 6, cy, cx + s // 2 - 6, cy, BLUE)
    cv.line(cx, cy - s // 2 + 6, cx, cy + s // 2 - 6, BLUE)
    cv.circle(cx - 12, cy - 10, 7, BLUE)
    cv.circle(cx + 12, cy + 12, 7, BLUE)


def draw():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.rect(0, 0, W, 118, NAVY)
    title = "WORLD NEWS"
    cv.text((W - cv.text_width(title, 8)) // 2, 16, title, 8, WHITE)
    date = "TUESDAY, 24 NOVEMBER 2026"
    cv.text((W - cv.text_width(date, 3)) // 2, 86, date, 3, GOLD)
    cv.rect(0, 118, W, 4, GOLD)

    # ---- lead story ----
    cv.frame(24, 134, 976, 318, INK, 2)
    cv.rect(40, 150, 168, 26, RED)
    cv.text(52, 156, "LEAD STORY", 2, WHITE)
    lx, lw = 40, 580
    n = cv.block(lx, 192, "UKRAINE SAYS IT SANK RUSSIAN WARSHIP OFF LIBYA",
                 4, INK, lw, 36)
    body = ("KYIV CLAIMS DRONE BOATS SANK A RUSSIAN WARSHIP AND DAMAGED "
            "A CARGO VESSEL OFF THE LIBYAN COAST, A SHARP ESCALATION IN "
            "LONG-RANGE STRIKES ON RUSSIAN ASSETS.")
    cv.block(lx, 192 + n * 36 + 14, body, 2, INK, lw, 20)
    cv.line(628, 150, 628, 436, GREY)
    draw_ship(cv, 644, 150, 1000, 436)

    # ---- five more stories ----
    stories = [
        # (tag, colour, headline, body, icon)
        ("EUROPE", RED, "EU UNVEILS 22ND SANCTIONS ON RUSSIA",
         "BRUSSELS PROPOSES BANNING RUSSIAN TEAMS UNDER THE FLAG AND "
         "CURBS ON BANKS AND CRYPTO.",
         icon_stars),
        ("THE WAR", RED, "RUSSIAN WAR DEAD NEARS 700,000",
         "LEAKED GOVERNMENT DATA STUDIED BY MEDIA PUTS RUSSIA'S WAR "
         "DEAD NEAR 700,000.",
         icon_bars),
        ("CLIMATE", RED, "COP31 TALKS STALL IN TURKIYE",
         "OIL PRODUCERS CLASH WITH CLIMATE ADVOCATES OVER FOSSIL "
         "FUELS IN ANTALYA.",
         icon_globe),
        ("ASIA", RED, "INDONESIA FACTORY FIRE KILLS SEVERAL",
         "A BLAZE AT AN INDUSTRIAL PLANT LEAVES SEVERAL DEAD AND "
         "WORKERS MISSING AS RESCUERS SEARCH THE SITE.",
         icon_factory),
        ("TECH", RED, "NVIDIA REINSTATES JENSEN HUANG AS CEO",
         "THE BOARD BRINGS BACK ITS FOUNDER DAYS AFTER HIS SHOCK "
         "RESIGNATION, AND SHARES JUMP ON THE NEWS.",
         icon_chip),
    ]
    # left column: three stories
    ly = 468
    for tag, col, head, body, icon in stories[:3]:
        cv.frame(24, ly, 476, 130, INK, 2)
        icon(cv, 32, ly + 37, 56)
        tx = 124
        cv.text(tx, ly + 10, tag, 2, col)
        nh = cv.block(tx, ly + 30, head, 3, INK, 360, 21)
        cv.block(tx, ly + 30 + nh * 21 + 6, body, 2, INK, 360, 17,
                 max_lines=3)
        ly += 137
    # right column: two stories
    ry = 468
    for tag, col, head, body, icon in stories[3:]:
        cv.frame(524, ry, 476, 196, INK, 2)
        icon(cv, 536, ry + 54, 88)
        tx = 640
        cv.text(tx, ry + 14, tag, 2, col)
        nh = cv.block(tx, ry + 38, head, 3, INK, 344, 22)
        cv.block(tx, ry + 38 + nh * 22 + 8, body, 2, INK, 344, 18)
        ry += 208

    # ---- also today ----
    cv.rect(0, 888, W, 136, NAVY)
    cv.text(24, 904, "ALSO TODAY", 3, GOLD)
    also = [
        "ZELENSKY URGES FOUR-PARTY PEACE TALKS",
        "SOUTH AFRICANS VOTE AS ANC FACES ANGER",
        "MIGRANT BOAT CAPSIZES OFF SENEGAL",
        "MELAT KIROS, 29, FIRST GEN Z ELECTED",
    ]
    for i, item in enumerate(also):
        ax = 24 + (i % 2) * 500
        ay = 946 + (i // 2) * 36
        cv.rect(ax, ay + 3, 10, 10, GOLD)
        cv.text(ax + 20, ay, item, 2, WHITE)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw()
    save_png(os.path.join(out_dir, "entry.png"), cv)


if __name__ == "__main__":
    main()
