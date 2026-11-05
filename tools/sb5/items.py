"""Rip the bomb, fire, speed and 9 item icons of the Config Battle ability editor to docs/img/items/sb5/.

    MESEN=<portable Mesen.exe> SCRATCH=<dir> python tools/sb5/items.py

Icons are 2x2 4bpp tiles on BG1 (tilemap $3000, chr $0000), real CGRAM, colour 0 clear. Row 12: bomb, fire, speed
at tile x 7/15/23; row 16: the 4 visible items at x 17/20/23/26 (item order = SB5.ITEMS, see items.lua for the scroll).
"""
import os, subprocess
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "docs" / "img" / "items" / "sb5"
SLOTS = (17, 20, 23, 26)
ICONS = {"bomb": (0, 7, 12), "fire": (0, 15, 12), "speed": (0, 23, 12)}   # name: (dump, tile x, tile y)
NAMES = ["remote", "pierce", "mine", "homing", "bombpass", "softpass", "glove", "kick", "punch"]
for i, n in enumerate(NAMES):
    ICONS[n] = (0, SLOTS[i], 16) if i < 4 else (4, SLOTS[3], 16) if i == 4 else (8, SLOTS[i - 5], 16)

scratch = Path(os.environ["SCRATCH"]) / "sb5_items"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "items.lua").write_text("KEEPSRAM=true\n" + (HERE / "lib.lua").read_text(encoding="utf-8") + (HERE / "items.lua").read_text(encoding="utf-8"), encoding="utf-8")
log = subprocess.run(["sh", str(HERE / "run.sh"), str(scratch / "items.lua")], capture_output=True, text=True, check=True).stdout
d = {}
for line in log.splitlines():
    k, _, v = line.partition(" ")
    if k.startswith(("VRAM", "CGRAM")):
        d[k] = bytes.fromhex(v.strip())


def icon(n, x, y):
    vram, cg = d["VRAM%d" % n], d["CGRAM%d" % n]
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for ty in range(2):
        for tx in range(2):
            a = 0x6000 + 2 * ((y + ty) * 32 + x + tx)
            e = vram[a] | vram[a + 1] << 8
            t, p, hf, vf = e & 0x3FF, e >> 10 & 7, e >> 14 & 1, e >> 15
            for py in range(8):
                o = t * 32 + 2 * (7 - py if vf else py)
                for px in range(8):
                    b = 7 - px if not hf else px
                    c = sum((vram[o + 16 * (k // 2) + (k & 1)] >> b & 1) << k for k in range(4))
                    if c:
                        w = cg[2 * (16 * p + c)] | cg[2 * (16 * p + c) + 1] << 8
                        im.putpixel((8 * tx + px, 8 * ty + py), ((w & 31) * 255 // 31, (w >> 5 & 31) * 255 // 31, (w >> 10 & 31) * 255 // 31, 255))
    return im


OUT.mkdir(parents=True, exist_ok=True)
for name, (n, x, y) in ICONS.items():
    icon(n, x, y).save(OUT / (name + ".png"))
print("wrote %d icons to %s" % (len(ICONS), OUT))
