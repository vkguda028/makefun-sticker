import os, zlib, struct, math

W = H = 1024
buf = bytearray([255]) * (W * H * 3)

NAVY = (20, 17, 43); DARK = (20, 17, 43); WHITE = (255, 255, 255)
MINT = (74, 222, 128); GOLD = (250, 204, 21); PINK = (244, 63, 148)

def draw(x0, y0, x1, y1, sdf, col):
    x0 = max(0, int(x0)); y0 = max(0, int(y0))
    x1 = min(W, int(x1) + 1); y1 = min(H, int(y1) + 1)
    r, g, b = col
    for y in range(y0, y1):
        row = y * W * 3
        for x in range(x0, x1):
            a = 0.5 - sdf(x + 0.5, y + 0.5)
            if a <= 0:
                continue
            i = row + x * 3
            if a >= 1:
                buf[i] = r; buf[i+1] = g; buf[i+2] = b
            else:
                buf[i] = int(buf[i] * (1 - a) + r * a + 0.5)
                buf[i+1] = int(buf[i+1] * (1 - a) + g * a + 0.5)
                buf[i+2] = int(buf[i+2] * (1 - a) + b * a + 0.5)

def circle(cx, cy, rad, col):
    draw(cx - rad - 1, cy - rad - 1, cx + rad + 1, cy + rad + 1,
         lambda x, y: math.hypot(x - cx, y - cy) - rad, col)

def rrect(cx, cy, hw, hh, rad, col):
    def f(x, y):
        qx = abs(x - cx) - (hw - rad); qy = abs(y - cy) - (hh - rad)
        return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - rad
    draw(cx - hw - 1, cy - hh - 1, cx + hw + 1, cy + hh + 1, f, col)

def outlined_rrect(cx, cy, hw, hh, rad, col, o=9):
    rrect(cx, cy, hw + o, hh + o, rad + o, WHITE)
    rrect(cx, cy, hw, hh, rad, col)

# die-cut badge
circle(512, 512, 506, DARK)
circle(512, 512, 488, WHITE)
circle(512, 512, 468, NAVY)

# robot ears, head
rrect(332, 405, 20, 42, 8, PINK); rrect(692, 405, 20, 42, 8, PINK)
outlined_rrect(512, 405, 160, 122, 34, MINT)
# eyes + mouth
for ex in (452, 572):
    rrect(ex, 395, 32, 36, 8, NAVY)
    rrect(ex + 9, 385, 11, 11, 3, WHITE)
rrect(512, 470, 72, 14, 7, NAVY)

# crown
outlined_rrect(512, 253, 92, 17, 6, GOLD, 8)
for sx in (436, 512, 588):
    outlined_rrect(sx, 214, 15, 26, 5, GOLD, 8)
    rrect(sx, 253, 92, 17, 6, GOLD)
    rrect(sx, 214, 15, 26, 5, GOLD)
    circle(sx, 182, 22, WHITE); circle(sx, 182, 14, PINK)

# pixel wordmark
FONT = {
 'm': ["", "", "11010", "10101", "10101", "10101", "10101"],
 'a': ["", "", "01110", "00001", "01111", "10001", "01111"],
 'k': ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
 'e': ["", "", "01110", "10001", "11111", "10000", "01110"],
 '.': ["", "", "", "", "", "", "1"],
 'f': ["00110", "01000", "11110", "01000", "01000", "01000", "01000"],
 'u': ["", "", "10001", "10001", "10001", "10011", "01101"],
 'n': ["", "", "11110", "10001", "10001", "10001", "10001"],
}
TEXT = "make.fun"
C = 18
cols = sum(1 if ch == '.' else 5 for ch in TEXT) + (len(TEXT) - 1)
sx0 = 512 - cols * C // 2
sy0 = 650
cells = []
cx = sx0
for ch in TEXT:
    w = 1 if ch == '.' else 5
    colr = WHITE if ch in "make" else GOLD
    for r, line in enumerate(FONT[ch]):
        for c, v in enumerate(line):
            if v == '1':
                cells.append((cx + c * C, sy0 + r * C, colr))
    cx += (w + 1) * C
for x, y, _ in cells:
    rrect(x + C / 2 + 6, y + C / 2 + 6, C / 2, C / 2, 1, PINK)
for x, y, colr in cells:
    rrect(x + C / 2, y + C / 2, C / 2, C / 2, 1, colr)

# tagline blocks: three small bars (ranking podium)
for i, (bx, h) in enumerate(((432, 56), (512, 90), (592, 40))):
    rrect(bx, 905 - h // 2, 34, h // 2, 6, MINT if i == 1 else WHITE)

# write PNG
raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 3:(y + 1) * W * 3]
def chunk(t, d):
    c = struct.pack(">I", len(d)) + t + d
    return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "entry.png"), "wb") as f:
    f.write(png)
