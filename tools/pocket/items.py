"""Rip the bomb-up and fire-up item boxes (what the power-up passwords raise: bombs and fire) from a VRAM dump taken in
play (e.g. vdump() in any stage). They are BG tiles $88-$8B (bomb) and $8C-$8F (fire), 2 x 2 in row order, drawn into
the map where a destroyed bush leaves an item. Native 16 x 16, DMG shades (BGP $E4), colour 0 transparent.
Usage: python tools/pocket/items.py <play.vram> <out dir>"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram
v = gbvram.load(sys.argv[1])
os.makedirs(sys.argv[2], exist_ok=True)
for name, base in (("bomb", 0x88), ("fire", 0x8C)):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for k, (dx, dy) in enumerate([(0, 0), (8, 0), (0, 8), (8, 8)]):
        for y, row in enumerate(gbvram.tile(v["vram"], gbvram.bg_tile(v, base + k))):
            for x, c in enumerate(row):
                if c:
                    im.putpixel((dx + x, dy + y), gbvram.shade(0xE4, c) + (255,))
    im.save(os.path.join(sys.argv[2], name + ".png"))
print("2 icons")
