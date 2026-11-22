#!/usr/bin/env python3
"""The World Today - Sunday 22 November 2026.

Draws one 1024x1024 newspaper front page summing up the day's world
news: 4 lead stories plus 26 compact items, all verified against web
reporting for 21-22 November 2026, with the day's three stories that
happened on Sunday itself leading the page. Pure Python 3.13 stdlib:
the image is rendered with a hand-built 5x7 bitmap font and encoded
to PNG with zlib. Deterministic: no randomness, no clock, no network.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (253, 252, 247)
INK = (17, 17, 17)
SOFT = (70, 70, 70)
RED = (176, 0, 0)
GRAY = (120, 120, 120)
LIGHT = (238, 236, 230)
BORDER = (200, 198, 192)

# 5x7 bitmap font, one row per string, '1' = ink. Written by hand.
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
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

LEADS = [
    ("GULF CRISIS",
     "IRAN STRIKES U.S. BASES IN BAHRAIN AND KUWAIT",
     "IRGC hit U.S. sites with missiles and drones early "
     "Sunday. CENTCOM: defences held, no casualties."),
    ("CLIMATE",
     "COP31 DRAGS INTO SUNDAY AS TALKS STALL",
     "Antalya talks pass Friday's deadline with no deal. "
     "130 nations demand fossil-fuel text; draft drops it."),
    ("ISRAEL",
     "EISENKOT INVITES LIKUD TO COALITION TALKS",
     "Yashar leader Gadi Eisenkot invites Netanyahu's Likud "
     "for intensive talks to break the deadlock."),
    ("AFRICA",
     "G20 OPENS IN JOHANNESBURG, FIRST ON AFRICAN SOIL",
     "Ramaphosa hosts the 20th G20 summit. "
     "The U.S. stays away; Modi attends. "
     "Debt, disaster relief top agenda."),
]

COMPACT = [
    ("MEXICO RAIDS LEAVE 11 DEAD",
     "4 soldiers, 7 gunmen killed in raids."),
    ("BRAZIL STORM TOLL RISES TO FOUR",
     "162 hurt; 8,000 homes hit, Tupancireta."),
    ("AI CLAIMS PROOF OF RIEMANN HYPOTHESIS",
     "Proof posted in Lean; checks under way."),
    ("ASHES DAY ONE: 19 WICKETS FALL",
     "Starc 7-58, Stokes 5-23 in Perth chaos."),
    ("ENGLAND 37-12 ALL BLACKS",
     "Hosts win at Twickenham on Saturday."),
    ("NEWCASTLE 2-2 ARSENAL",
     "Madueke rescues point; Raya hurt."),
    ("PSG 3-2 NICE; DOUE SERIOUSLY HURT",
     "Leaders win; Doue faces a long layoff."),
    ("ZELENSKY: BRIDGE STRIKE WAS FAIR",
     "Kyiv calls Kerch attack 'fair response'."),
    ("BOLSONARO IN ICU, CONDITION STABLE",
     "Ex-president has bowel obstruction."),
    ("FRENCH PROTEST FOR SIXTH SATURDAY",
     "Rallies over living costs and services."),
    ("PALESTINIAN SHOT DEAD IN WEST BANK",
     "Settler guards blamed, authorities say."),
    ("FINLAND PROBES RUSSIAN HELICOPTER",
     "Suspected airspace violation probed."),
    ("RUSSIAN CARGO SHIP ABLAZE IN BALTIC",
     "Sparta II hit in suspected drone strike."),
    ("EU AND INDONESIA SIGN TRADE DEALS",
     "CEPA and investment pacts signed."),
    ("EU BUDGET PLAN: 1.78 TRILLION EURO",
     "Costa draft for 2028-34 heads to summit."),
    ("EBOLA FIGHT HAMPERED IN DR CONGO",
     "Violence and distrust slow the response."),
    ("BASRA POWER STATION FIRE KILLS FOUR",
     "Blast at Hartha plant injures 35 people."),
    ("MAMDANI: CLOSE RIKERS BY 2032",
     "NYC mayor unveils jail closure plan."),
    ("HOUSE DEMOCRATS PROBE NVIDIA",
     "Probe over Megaspeed chip inquiry."),
    ("MODI OPENS NITISH SETU BRIDGE",
     "19.7 km Ganga bridge opens in Bihar."),
    ("CYCLONE AKVAN DISRUPTS EAST INDIA",
     "Flights cancelled after Odisha landfall."),
    ("SNOW ISOLATES 1,400 IN FUKUSHIMA",
     "Fallen trees cut off village in Japan."),
    ("SAUDI TO TRIPLE CRUDE STORED IN JAPAN",
     "24m barrels; Tokyo buys 8m for reserve."),
    ("CHINA TO JAPAN: CHANGE 'ATTITUDE'",
     "Beijing cools ties after Xi snub."),
    ("BTS WIN FIVE AT MAMA AWARDS",
     "K-pop stars triumph at Osaka ceremony."),
    ("WASHINGTON'S HAIR SELLS FOR $4,000",
     "Lock from 1799 fetches $4,000."),
]


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines = []
    for word in text.split(" "):
        if not lines or len(lines[-1]) + 1 + len(word) > max_chars:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


def draw_text(img, x, y, text, scale, color, bold=False):
    """Draw text left-aligned at (x, y). Glyph advance is 6*scale."""
    rgb = bytes(color)
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    px = x + col * scale
                    py = y + row * scale
                    wide = scale + 1 if bold else scale
                    for dy in range(scale):
                        base = ((py + dy) * W + px) * 3
                        img[base:base + wide * 3] = rgb * wide
        x += 6 * scale
    return x


def fill_rect(img, x, y, w, h, color):
    rgb = bytes(color)
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        img[base:base + w * 3] = rgb * w


def hline(img, x0, x1, y, color, thick=1):
    fill_rect(img, x0, y, x1 - x0, thick, color)


def png_bytes(img):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += img[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp)
            + chunk(b"IEND", b""))


def draw_page():
    img = bytearray(bytes(PAPER)) * (W * H)
    # Top rule and masthead.
    hline(img, 28, 996, 16, INK, 2)
    title = "THE WORLD TODAY"
    draw_text(img, (W - text_width(title, 6)) // 2, 26, title, 6, INK)
    date = "SUNDAY, 22 NOVEMBER 2026"
    draw_text(img, (W - text_width(date, 2)) // 2, 76, date, 2, INK)
    sub = "30 STORIES FROM AROUND THE WORLD"
    draw_text(img, (W - text_width(sub, 2)) // 2, 96, sub, 2, RED)
    hline(img, 28, 996, 118, INK, 3)
    # Four lead stories, 2x2.
    for i, (kicker, headline, body) in enumerate(LEADS):
        cx = 28 + (i % 2) * 488
        cy = 130 + (i // 2) * 134
        fill_rect(img, cx, cy, 480, 122, LIGHT)
        fill_rect(img, cx, cy, 480, 1, BORDER)
        fill_rect(img, cx, cy + 121, 480, 1, BORDER)
        fill_rect(img, cx, cy, 1, 122, BORDER)
        fill_rect(img, cx + 479, cy, 1, 122, BORDER)
        draw_text(img, cx + 10, cy + 4, kicker, 2, RED, bold=True)
        head_lines = wrap(headline, 26)
        assert len(head_lines) <= 2, head_lines
        for j, line in enumerate(head_lines):
            draw_text(img, cx + 10, cy + 22 + j * 24, line, 3, INK, bold=True)
        body_lines = wrap(body, 38)
        assert len(body_lines) <= 3, body_lines
        for j, line in enumerate(body_lines):
            draw_text(img, cx + 10, cy + 72 + j * 16, line, 2, INK)
        print("LEAD", i + 1, head_lines, body_lines)
    # Section header.
    hline(img, 28, 996, 398, INK, 2)
    section = "AROUND THE WORLD - THE DAY IN BRIEF"
    draw_text(img, (W - text_width(section, 2)) // 2, 406, section, 2, INK, bold=True)
    # Compact grid: 2 columns x 13 rows.
    assert len(COMPACT) == 26, len(COMPACT)
    for i, (headline, detail) in enumerate(COMPACT):
        cx = 28 + (i % 2) * 488
        cy = 428 + (i // 2) * 44
        assert len(headline) <= 40, headline
        assert len(detail) <= 40, detail
        draw_text(img, cx, cy + 4, headline, 2, INK, bold=True)
        draw_text(img, cx, cy + 22, detail, 2, SOFT)
    hline(img, 28, 996, 1008, INK, 2)
    return img


def main():
    img = draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(img)
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
