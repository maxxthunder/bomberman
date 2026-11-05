"""Title logo for Bomberman GB 2 / Bomberman GB: the logo shares the title's window map with the clouds and trees, so
the window tiles 0-19 x 0-8 are rendered and everything reachable from the picture's edge without crossing the logo's
black outline is made transparent (flood fill over non-black pixels).
Usage: python tools/gb2/logo.py <title.vram> <out.png>   (title.vram: vdump() on the title screen)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram

im = gbvram.render_map(gbvram.load(sys.argv[1]), 0, 0, 20, 9, window=True)
w, h = im.size
px = im.load()
seen, todo = set(), [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
while todo:
    x, y = todo.pop()
    if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or px[x, y][:3] == (0, 0, 0):
        continue
    seen.add((x, y))
    px[x, y] = (0, 0, 0, 0)
    todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
im.crop(im.getbbox()).save(sys.argv[2])
