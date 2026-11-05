"""Render PC Engine VDC/VCE dumps (vdump.lua output) to PNG.

python logo.py bat <out.txt> <png>                     whole 128x64 BAT, every tile with its own palette
python logo.py crop <out.txt> <png> x y w h [pals]     tiles of the BAT area (in tiles), colour 0 transparent;
                                                        pals = comma list of BG palettes to keep (others transparent)
python logo.py spr <out.txt> <png> [pals] [y0 y1]    sprites from the SAT on a 256x240 screen, colour 0 transparent, cropped;
                                                        pals = sprite palettes (0-15) to keep, y0-y1 = screen rows of the sprite tops
Tiles are 4bpp planar (32 bytes: words 0-7 planes 0/1, words 8-15 planes 2/3); BAT word = palette<<12 | tile.
VCE colour = 9-bit GGGRRRBBB, palette n entry c at word 16n+c.
"""
import sys
from PIL import Image


def load(path):
    d = {}
    for line in open(path):
        k, _, v = line.partition(" ")
        if k in ("VRAM", "PAL", "SAT"):
            d[k] = bytes.fromhex(v.strip())
    return d


def colour(pal, i):
    w = pal[2 * i] | pal[2 * i + 1] << 8
    g, r, b = w >> 6 & 7, w >> 3 & 7, w & 7
    return (r * 255 // 7, g * 255 // 7, b * 255 // 7, 255)


def tile(vram, n):
    o = n * 32
    rows = []
    for y in range(8):
        p0, p1 = vram[o + 2 * y], vram[o + 2 * y + 1]
        p2, p3 = vram[o + 16 + 2 * y], vram[o + 17 + 2 * y]
        rows.append([(p0 >> (7 - x) & 1) | (p1 >> (7 - x) & 1) << 1 | (p2 >> (7 - x) & 1) << 2 | (p3 >> (7 - x) & 1) << 3
                     for x in range(8)])
    return rows


def render(d, x0, y0, w, h, cols=128, keep=None, transparent=True):
    vram, pal = d["VRAM"], d["PAL"]
    im = Image.new("RGBA", (w * 8, h * 8), (0, 0, 0, 0))
    px = im.load()
    for ty in range(h):
        for tx in range(w):
            a = 2 * ((y0 + ty) * cols + x0 + tx)
            e = vram[a] | vram[a + 1] << 8
            p, t = e >> 12, e & 0xFFF
            if keep is not None and p not in keep:
                continue
            for y, row in enumerate(tile(vram, t)):
                for x, c in enumerate(row):
                    if c or not transparent:
                        px[tx * 8 + x, ty * 8 + y] = colour(pal, 16 * p + c if c else 0)
    return im


def sprites(d, keep=None, y0=-64, y1=999):
    """SAT: 64 x 4 words (Y+64, X+32, pattern<<1, attributes). 16x16 cells of 64 words: plane p row r at word 16p+r,
    bit 15 = leftmost pixel. Attr bits 0-3 palette (16+n), 8 width 32, 12-13 height 16/32/64, 11 X flip, 15 Y flip.
    Entry 0 is drawn on top, so draw from 63 down."""
    vram, pal, sat = d["VRAM"], d["PAL"], d["SAT"]
    im = Image.new("RGBA", (256, 240), (0, 0, 0, 0))
    px = im.load()
    for n in range(63, -1, -1):
        w = [sat[8 * n + 2 * k] | sat[8 * n + 2 * k + 1] << 8 for k in range(4)]
        y, x, pat, a = (w[0] & 0x3FF) - 64, (w[1] & 0x3FF) - 32, w[2] >> 1 & 0x3FF, w[3]
        p = a & 15
        if (keep is not None and p not in keep) or not y0 <= y <= y1:
            continue
        cw, ch = (2 if a & 0x100 else 1), (1, 2, 4, 4)[a >> 12 & 3]
        pat &= ~(cw - 1) & ~((ch - 1) * 2)
        for cy in range(ch):
            for cx in range(cw):
                o = (pat + cx + cy * 2) * 128
                for r in range(16):
                    planes = [vram[o + 32 * q + 2 * r] | vram[o + 32 * q + 2 * r + 1] << 8 for q in range(4)]
                    for c in range(16):
                        v = sum((planes[q] >> (15 - c) & 1) << q for q in range(4))
                        if not v:
                            continue
                        sx, sy = cx * 16 + c, cy * 16 + r
                        if a & 0x800:
                            sx = cw * 16 - 1 - sx
                        if a & 0x8000:
                            sy = ch * 16 - 1 - sy
                        X, Y = x + sx, y + sy
                        if 0 <= X < 256 and 0 <= Y < 240:
                            px[X, Y] = colour(pal, 256 + 16 * p + v)
    return im


if __name__ == "__main__" and sys.argv[1] == "spr":
    d = load(sys.argv[2])
    keep = set(map(int, sys.argv[4].split(","))) if len(sys.argv) > 4 and sys.argv[4] != "all" else None
    y0, y1 = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (-64, 999)
    im = sprites(d, keep, y0, y1)
    im.crop(im.getbbox()).save(sys.argv[3])
elif __name__ == "__main__":
    d = load(sys.argv[2])
    if sys.argv[1] == "bat":
        render(d, 0, 0, 128, 64, transparent=False).save(sys.argv[3])
    else:
        x, y, w, h = map(int, sys.argv[4:8])
        keep = set(map(int, sys.argv[8].split(","))) if len(sys.argv) > 8 else None
        im = render(d, x, y, w, h, keep=keep)
        im.crop(im.getbbox()).save(sys.argv[3])
