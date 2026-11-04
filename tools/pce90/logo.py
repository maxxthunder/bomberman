"""Render PC Engine VDC/VCE dumps (vdump.lua output) to PNG.

python logo.py bat <out.txt> <png>                     whole 128x64 BAT, every tile with its own palette
python logo.py crop <out.txt> <png> x y w h [pals]     tiles of the BAT area (in tiles), colour 0 transparent;
                                                        pals = comma list of BG palettes to keep (others transparent)
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


if __name__ == "__main__":
    d = load(sys.argv[2])
    if sys.argv[1] == "bat":
        render(d, 0, 0, 128, 64, transparent=False).save(sys.argv[3])
    else:
        x, y, w, h = map(int, sys.argv[4:8])
        keep = set(map(int, sys.argv[8].split(","))) if len(sys.argv) > 8 else None
        im = render(d, x, y, w, h, keep=keep)
        im.crop(im.getbbox()).save(sys.argv[3])
