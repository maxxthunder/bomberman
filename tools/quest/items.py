"""Rip the bag-menu icons (16 x 16, Game Boy Color colours) of every weapon, equipment and item the save holds.
Input: the out dir of tools/quest/items.lua (page<n>.png + page<n>.ram: VRAM 16 KB, both banks, then SCY, SCX); the
icons are 2 x 2 tiles of the window map ($9800, drawn at the screen's top left) at the page's slots (weapons 7 x 4 from map cell (1,1); equipment 4 x 4 from (1,1); items
two 4 x 2 panels from (1,1) and (10,1)), drawn from VRAM (bank and flips from the bank-1 attribute map), each colour
index painted with the screenshot colour it shows most often in that icon, colour 0 kept (the page's square).
Usage: python tools/quest/items.py <items.lua out dir> <out dir>"""
import json, os, subprocess, sys
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
src, dst = sys.argv[1:3]
os.makedirs(dst, exist_ok=True)
js = """import {WEAPONS, EQUIPMENT, ITEMS} from './password.mjs'; console.log(JSON.stringify([WEAPONS, EQUIPMENT, ITEMS]))"""
W, E, I = json.loads(subprocess.run(["node", "--input-type=module", "-e", js], cwd=here, capture_output=True, text=True).stdout)
# page -> [(map row, map col, entry)], the layout the test_items.py check confirmed
weap = W[7:] + W[:7]
SLOTS = {0: [(1 + 2 * (i // 7), 1 + 2 * (i % 7), e) for i, e in enumerate(weap)],
         1: [(1 + 2 * (i // 4), 1 + 2 * (i % 4), e) for i, e in enumerate(E)],
         2: [(1 + 2 * (i // 8), (1 if i % 8 < 4 else 10) + 2 * (i % 4), e)
             for i, e in enumerate(I[0:4] + I[8:12] + I[4:8] + I[12:16])]}
# the slot the cursor highlights when pages 1 and 2 open (Silver Armor, Armored Jacket): taken from page<n>b instead
CURSOR = {1: 0, 2: 4}
for p, slots in SLOTS.items():
  for n, (r, c, e) in enumerate(slots):
        f = "page%d%s" % (p, "b" if CURSOR.get(p) == n else "")
        shot = Image.open(os.path.join(src, f + ".png")).convert("RGBA")
        d = open(os.path.join(src, f + ".ram"), "rb").read()
        idx, votes = {}, {}
        for k, (dx, dy) in enumerate([(0, 0), (8, 0), (0, 8), (8, 8)]):
            m = 0x1800 + (r + dy // 8) * 32 + c + dx // 8
            t, a = d[m], d[0x2000 + m]
            base = (0x2000 if a & 8 else 0) + (0x1000 + t * 16 if t < 0x80 else t * 16)   # LCDC bit 4 clear
            for y in range(8):
                for x in range(8):
                    xx, yy = (7 - x if a & 0x20 else x), (7 - y if a & 0x40 else y)
                    o = base + yy * 2
                    i = (d[o] >> (7 - xx) & 1) | (d[o + 1] >> (7 - xx) & 1) << 1
                    idx[dx + x, dy + y] = i
                    rgb = shot.getpixel((c * 8 + dx + x, r * 8 + dy + y))   # the menu is the window ($9800 map) at 0, 0
                    v = votes.setdefault(i, {}); v[rgb] = v.get(rgb, 0) + 1
        pal = {i: max(v, key=v.get) for i, v in votes.items()}
        im = Image.new("RGBA", (16, 16))
        for xy, i in idx.items():
            im.putpixel(xy, pal[i])
        im.save(os.path.join(dst, e["icon"] + ".png"))
  print("page", p, len(slots), "icons")
