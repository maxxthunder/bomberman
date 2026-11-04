"""Images for docs/img/sb4/unused/: the 2bpp debug font at $D1:BC16, the debug PARAMETER text ($C4:6E69)
drawn with that font (a mock-up: the game has no code that draws it), and the two unused item icons.
Usage: python unused_img.py <rom> <battle cgram.bin> <outdir>"""
import sys
from PIL import Image
rom = open(sys.argv[1], 'rb').read(); cg = open(sys.argv[2], 'rb').read(); out = sys.argv[3]
def tile(o, bpp, pal):
    im = Image.new('RGB', (8, 8))
    for y in range(8):
        p = [rom[o + 2*y], rom[o + 2*y + 1]] + ([rom[o + 16 + 2*y], rom[o + 17 + 2*y]] if bpp == 4 else [])
        for x in range(8): im.putpixel((x, y), pal[sum((p[k] >> (7 - x) & 1) << k for k in range(bpp))])
    return im
FONT = 0x11BC16  # $D1:BC16, tile n = character $20+n
grey = [(0, 0, 0), (24, 24, 56), (170, 170, 170), (255, 255, 255)]  # colour 1 is the glyph background
sheet = Image.new('RGB', (16 * 9 + 1, 4 * 9 + 1), (60, 0, 60))
for n in range(64): sheet.paste(tile(FONT + 16 * n, 2, grey), (1 + n % 16 * 9, 1 + n // 16 * 9))
sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(f'{out}/debug_font_D1BC16.png')
txt = rom[0x46E69:rom.index(b'$', 0x46E69)].decode('ascii').split('&')
scr = Image.new('RGB', (8 * 17, 8 * len(txt)), (0, 0, 0))
for r, line in enumerate(txt):
    for k, ch in enumerate(line): scr.paste(tile(FONT + 16 * (ord(ch) - 0x20), 2, grey), (8 + 8 * k, 8 * r))
scr.resize((scr.width * 2, scr.height * 2), Image.NEAREST).save(f'{out}/debug_menu_mockup.png')
pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in (cg[2*i] | cg[2*i+1] << 8 for i in range(64, 80))]
ic = Image.new('RGB', (2 * 16 + 3, 16), (60, 0, 60))
for k, a in enumerate((0x11C558, 0x11C598)):  # power bomb, question mark: tiles t, t+1, t+16, t+17
    for q, d in enumerate((0, 32, 512, 544)): ic.paste(tile(a + d, 4, pal), (k * 19 + q % 2 * 8, q // 2 * 8))
ic.resize((ic.width * 4, ic.height * 4), Image.NEAREST).save(f'{out}/item_icons_D1C558_D1C598.png')
