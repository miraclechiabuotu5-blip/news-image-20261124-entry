"""Sum up 24 November 2026 world news in one image.

Python 3.13, standard library only, no network, no randomness, no time.
Writes a deterministic 1024x1024 PNG to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png when set for local testing).
"""
import os
import struct
import zlib

W = 1024
H = 1024

WHITE = (255, 255, 255)
NAVY = (11, 31, 58)
GOLD = (201, 162, 39)
DARK = (20, 20, 20)
GREY = (90, 90, 90)
LIGHT = (238, 240, 243)
RED = (178, 34, 34)
TEAL = (0, 128, 128)
BLUE = (30, 90, 170)
GREEN = (34, 120, 60)
PURPLE = (90, 60, 140)
ORANGE = (200, 100, 20)

# 5x7 bitmap font, each character is 7 rows of 5 bits.
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
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
    ",": ["00000", "00000", "00000", "00000", "00110", "00100", "01000"],
    ":": ["00000", "00100", "00000", "00000", "00000", "00100", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
}


def make_canvas():
    buf = bytearray(W * H * 3)
    for i in range(0, len(buf), 3):
        buf[i] = 255
        buf[i + 1] = 255
        buf[i + 2] = 255
    return buf


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o] = color[0]
        buf[o + 1] = color[1]
        buf[o + 2] = color[2]


def fill_rect(buf, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(buf, xx, yy, color)


def draw_text(buf, x, y, text, scale, color):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            set_px(buf, cx + col * scale + dx, y + row * scale + dy, color)
        cx += 6 * scale


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_centered(buf, y, text, scale, color):
    w = text_width(text, scale)
    draw_text(buf, (W - w) // 2, y, text, scale, color)


def wrap(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        if cur == "":
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur = cur + " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


STORIES = [
    (RED, "RIYADH HIT", "HOUTHIS STRIKE RIYADH TOWER AGAIN, 11 HURT", "SECOND STRIKE IN 5 DAYS, FIGHTERS NEAR ADEN"),
    (BLUE, "LIBYA SEA BATTLE", "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA", "CORVETTE MERKURY SUNK, UN URGES PROBE"),
    (ORANGE, "ZAPORIZHZHIA", "RUSSIAN STRIKE KILLS 2, WOUNDS 40", "APARTMENT HIT, 4 CHILDREN AMONG WOUNDED"),
    (PURPLE, "GAZA", "ISRAELI STRIKES KILL HAMAS SECURITY CHIEF", "NAEEM ABU NAHEL KILLED, 6 OTHERS DEAD"),
    (TEAL, "ESTONIA WARNING", "RUSSIA WARNS OF OPEN WAR OVER BORDER", "TALLINN TO CLOSE CROSSINGS ON 1 DEC"),
    (GREEN, "NVIDIA", "HUANG RETURNS AS CEO, SHARES JUMP 30 PCT", "BOARD REINSTATES HUANG AFTER RESIGNATION"),
]


def draw_image():
    buf = make_canvas()
    # Header
    fill_rect(buf, 0, 0, W, 176, NAVY)
    fill_rect(buf, 0, 176, W, 6, GOLD)
    draw_centered(buf, 28, "THE WORLD", 10, WHITE)
    draw_centered(buf, 108, "TUESDAY 24 NOVEMBER 2026", 4, GOLD)
    # Subheader
    draw_centered(buf, 198, "ONE DAY IN ONE IMAGE", 3, DARK)
    # Story panels: 2 columns x 3 rows
    px = [24, 524]
    py = [236, 492, 748]
    # panel height 240, footer starts at 1004? use 236+3*256=1004, footer 20px
    for idx, (color, kicker, headline, detail) in enumerate(STORIES):
        col = idx % 2
        row = idx // 2
        x = px[col]
        y = py[row]
        fill_rect(buf, x, y, 476, 240, LIGHT)
        fill_rect(buf, x, y, 476, 12, color)
        draw_text(buf, x + 16, y + 28, kicker, 3, color)
        lines = wrap(headline, 24)
        ly = y + 72
        for line in lines:
            draw_text(buf, x + 16, ly, line, 3, DARK)
            ly += 28
        # Detail line, smaller, grey, below the headline
        dlines = wrap(detail, 36)
        ly += 12
        for line in dlines:
            draw_text(buf, x + 16, ly, line, 2, GREY)
            ly += 20
        # small icon: numbered marker in corner
        fill_rect(buf, x + 420, y + 28, 40, 40, color)
        draw_text(buf, x + 432, y + 38, str(idx + 1), 2, WHITE)
    # Footer, larger text for legibility
    fill_rect(buf, 0, 1000, W, 24, NAVY)
    draw_centered(buf, 1005, "COP31 FAILS - SENEGAL WIN AFCON - NATO SPACE DEFENCE", 2, WHITE)
    return buf


def png_bytes(buf):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        start = y * W * 3
        raw.extend(buf[start:start + W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", comp)
    out += chunk(b"IEND", b"")
    return out


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(draw_image())
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)


if __name__ == "__main__":
    main()
