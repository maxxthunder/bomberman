"""Title logo: BG tiles 0-19 x 0-7 of the title screen (the menu box starts on row 8, Bomberman is sprites), cropped.
The white background is made transparent by a flood fill from the edges, so the white inside the letters stays.
DMG shades (the game run as a plain Game Boy).
Usage: python tools/pocket/logo.py <title.vram> <out.png>   (title.vram: vdump('title') once the title menu shows)"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram
im = gbvram.render_map(gbvram.load(sys.argv[1]), 0, 0, 20, 8)
w, h = im.size
for x, y in [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]:
    if im.getpixel((x, y)) == (255, 255, 255, 255):
        ImageDraw.floodfill(im, (x, y), (0, 0, 0, 0), thresh=0)
im.crop(im.getbbox()).save(sys.argv[2])
