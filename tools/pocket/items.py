"""Rip the bomb-up and fire-up item boxes (what the power-up passwords raise: bombs and fire) in Game Boy Color colours.
They are BG tiles $88-$8B (bomb) and $8C-$8F (fire), 2 x 2 in row order, drawn into the map where a destroyed bush
leaves an item. Input: a screenshot taken in play in CGB mode with the item on screen, and a dump taken the same frame
(<name>.ram: VRAM 16 KB, both banks, then SCY, SCX). The tiles are drawn from VRAM (bank and flips from the bank-1
attribute map), each colour index painted with the screenshot colour it shows most often in the box (Mesen's CGB
colours like the other rips; a sprite over part of the box doesn't leak in), colour 0 transparent.
Usage: python tools/pocket/items.py <shot.png> <dump.ram> <out dir>   (writes whichever of bomb/fire is on screen)"""
import os, sys
from PIL import Image
shot = Image.open(sys.argv[1]).convert("RGBA")
d = open(sys.argv[2], "rb").read()
scy, scx = d[0x4000], d[0x4001]
os.makedirs(sys.argv[3], exist_ok=True)


def pix(t, a, x, y):  # colour index of tile t (>= $80, so $8800 either addressing mode) under attribute a
    if a & 0x20: x = 7 - x
    if a & 0x40: y = 7 - y
    o = (0x2000 if a & 8 else 0) + t * 16 + y * 2
    return (d[o] >> (7 - x) & 1) | (d[o + 1] >> (7 - x) & 1) << 1


for name, base in (("bomb", 0x88), ("fire", 0x8C)):
    m = next((m for m in range(0x400) if d[0x1800 + m] == base), None)
    if m is None:
        continue
    sx, sy = ((m % 32) * 8 - scx) % 256, ((m // 32) * 8 - scy) % 256
    idx, votes = {}, {}
    for k, (dx, dy) in enumerate([(0, 0), (8, 0), (0, 8), (8, 8)]):
        c = (m + dx // 8 + dy // 8 * 32) % 0x400
        assert d[0x1800 + c] == base + k, (name, hex(d[0x1800 + c]))
        for y in range(8):
            for x in range(8):
                i = idx[dx + x, dy + y] = pix(base + k, d[0x3800 + c], x, y)
                v = votes.setdefault(i, {}); rgb = shot.getpixel((sx + dx + x, sy + dy + y)); v[rgb] = v.get(rgb, 0) + 1
    pal = {i: max(v, key=v.get) for i, v in votes.items()}
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for xy, i in idx.items():
        if i:
            im.putpixel(xy, pal[i])
    im.save(os.path.join(sys.argv[3], name + ".png"))
    print(name, "at", sx, sy, "attr %02x" % d[0x3800 + m])
