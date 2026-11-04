"""Render raw SNES tiles as a sheet: python tilesheet.py <file> <offset hex> <count> <bpp 2/4> out.png [cgram.bin|"" pal#] [cols]
File can be a VRAM dump or the ROM. Without cgram a grey ramp is used. Scale 2, 1px grid."""
import sys
from PIL import Image
d = open(sys.argv[1], 'rb').read(); off, n, bpp, out = int(sys.argv[2], 16), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[8]) if len(sys.argv) > 8 else 16
if len(sys.argv) > 7 and sys.argv[6]:
    cg = open(sys.argv[6], 'rb').read(); base = int(sys.argv[7]) * (1 << bpp)
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in (cg[2*i] | cg[2*i+1] << 8 for i in range(base, base + (1 << bpp)))]
else:
    pal = [(i * 255 // ((1 << bpp) - 1),) * 3 for i in range(1 << bpp)]
pal[0] = (40, 0, 40)
sz = 8 * bpp; rows = (n + cols - 1) // cols
img = Image.new('RGB', (cols * 9 + 1, rows * 9 + 1), (90, 90, 90))
for t in range(n):
    b = off + t * sz
    if b + sz > len(d): break
    for y in range(8):
        p = [d[b + 2*y], d[b + 2*y + 1]] + ([d[b + 16 + 2*y], d[b + 17 + 2*y]] if bpp == 4 else [])
        for x in range(8):
            c = sum((p[k] >> (7 - x) & 1) << k for k in range(bpp))
            img.putpixel((t % cols * 9 + 1 + x, t // cols * 9 + 1 + y), pal[c])
img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(out)
