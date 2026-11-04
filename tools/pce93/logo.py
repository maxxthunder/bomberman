"""Title logo from a title-screen VRAM/SAT/palette dump (vdump in mesen.py): python logo.py <base> <us|jp|sp> out.png
The logo is all sprites: every sprite with palette 2 (BOMBER MAN '93), plus in the US the TM sprite next to it
(the one at screen y 96; the other TM sprite is in the copyright line) and in the Special Version the
SPECIAL VERSION banner (palette 4, screen y 96-119). Colour 0 transparent, cropped tight, native resolution.
"""
import sys
from vram_render import load, sprites

base, ver, out = sys.argv[1:4]
vram, pal, sat = load(base)
keep = bytearray(len(sat))
for n in range(64):
    y, x, p, a = [sat[8 * n + 2 * k] | sat[8 * n + 2 * k + 1] << 8 for k in range(4)]
    y, pl = (y & 0x3FF) - 64, a & 15
    if not 0 <= y < 240 or not 0 <= (x & 0x3FF) - 32 < 256:   # off-screen (unused SAT entries)
        continue
    if pl == 2 or (ver == "us" and pl == 3 and y == 96) or (ver == "sp" and pl == 4 and 96 <= y < 120):
        keep[8 * n:8 * n + 8] = sat[8 * n:8 * n + 8]
im = sprites(vram, pal, bytes(keep))
im.crop(im.getbbox()).save(out)
