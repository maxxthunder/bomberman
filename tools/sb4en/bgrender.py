"""Render one SNES mode-1 4bpp BG layer from VRAM/CGRAM dumps (Mesen byte addresses).
Usage: python bgrender.py vram.bin cgram.bin <map byte addr> <chr byte addr> <16x16: 0/1> out.png [hscroll vscroll]
Transparent where the pixel is colour 0. Output is the 256x224 visible window."""
import sys
from PIL import Image
vram = open(sys.argv[1], 'rb').read(); cg = open(sys.argv[2], 'rb').read()
mapa, chra, big = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5] == '1'
hs, vs = (int(sys.argv[7]), int(sys.argv[8])) if len(sys.argv) > 8 else (0, 0)
pal = []
for i in range(256):
    c = cg[2 * i] | cg[2 * i + 1] << 8
    pal.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31, 255))
def px(tile, x, y):  # 4bpp 8x8 tile
    b = (chra + tile * 32) & 0xFFFF
    r0, r1, r2, r3 = vram[b + y * 2], vram[b + y * 2 + 1], vram[b + 16 + y * 2], vram[b + 17 + y * 2]
    s = 7 - x
    return (r0 >> s & 1) | (r1 >> s & 1) << 1 | (r2 >> s & 1) << 2 | (r3 >> s & 1) << 3
ts = 16 if big else 8
img = Image.new('RGBA', (256, 224), (0, 0, 0, 0))
for sy in range(224):
    for sx in range(256):
        X, Y = (sx + hs) % (32 * ts), (sy + vs) % (32 * ts)
        e = vram[mapa + 2 * ((Y // ts) * 32 + X // ts)] | vram[mapa + 2 * ((Y // ts) * 32 + X // ts) + 1] << 8
        t, p, hf, vf = e & 1023, e >> 10 & 7, e >> 14 & 1, e >> 15 & 1
        x, y = X % ts, Y % ts
        if hf: x = ts - 1 - x
        if vf: y = ts - 1 - y
        if big: t += (x >= 8) + 16 * (y >= 8)
        c = px(t, x % 8, y % 8)
        if c: img.putpixel((sx, sy), pal[p * 16 + c])
img.save(sys.argv[6])
