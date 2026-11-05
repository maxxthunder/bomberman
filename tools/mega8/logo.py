"""Rip the demo's title text from a splash-screen VRAM/CRAM dump (tools/mega8/vdpdump.lua).

The splash is one bitmap mapped on plane A at VRAM $C000 (64x32 cells), palette line 0. The demo has no Mega
Bomberman logo; its title is the two text lines at the top ("Mega Bomberman" / "special 8-player-demo"), kept
here down to the first blank pixel row after them. Colour 0 is transparent. Usage: python logo.py DUMPDIR out.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import vdp
d, out = sys.argv[1], sys.argv[2]
v = open(os.path.join(d, 'VRAM.bin'), 'rb').read(); P = vdp.palette(open(os.path.join(d, 'CRAM.bin'), 'rb').read())
im, _ = vdp.plane(v, 0xC000, 64, 32)
im = im.crop((0, 0, 320, 224))
rows = [y for y in range(224) if any(im.getpixel((x, y)) for x in range(320))]
bands = []                                                  # runs of non-empty pixel rows = text lines
for y in rows:
    if bands and y == bands[-1][1] + 1: bands[-1][1] = y
    else: bands.append([y, y])
top, bot = bands[0][0], bands[1][1]                         # first two lines
im = im.crop((0, top, 320, bot + 1)); im = im.crop(im.getbbox())
im.putpalette([x for c in P[0:16] for x in c]); im.info['transparency'] = 0
im.save(out, transparency=0, optimize=True)
print(out, im.size, 'text lines at', bands[:4])
