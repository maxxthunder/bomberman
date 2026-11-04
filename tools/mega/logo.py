"""Rip the Mega Bomberman title logo from a title-screen VRAM/CRAM dump (tools/mega/vdpdump.lua).

The logo is plane-mapped at VRAM $E000 (64x32 cells), palette line 2, sharing cells with the comet streak behind it.
Only the letter colours are kept (the streak's light blue, blue, greys and white are dropped); colour 0 is transparent.
Usage: python logo.py DUMPDIR out.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import vdp
d, out = sys.argv[1], sys.argv[2]
v = open(os.path.join(d, 'VRAM.bin'), 'rb').read(); P = vdp.palette(open(os.path.join(d, 'CRAM.bin'), 'rb').read())
im, _ = vdp.plane(v, 0xE000, 64, 32)
keep = {35, 36, 37, 38, 39, 40, 41, 42, 43, 46}            # yellow/orange/red/brown fill and the black outline
im.putdata([p - 32 if p in keep else 0 for p in im.getdata()])
px = im.load()                                              # drop stray streak pixels that share a letter colour
for y in range(128):
    for x in range(256):
        if px[x, y] and not any(px[x + i, y + j] for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j) and 0 <= x + i < 512 and 0 <= y + j < 256):
            px[x, y] = 0
im = im.crop(im.crop((0, 0, 256, 128)).getbbox())
im.putpalette([x for c in P[32:48] for x in c]); im.info['transparency'] = 0
im.save(out, transparency=0, optimize=True)
print(out, im.size)
