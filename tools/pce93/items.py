"""Rip the fire, bomb and skate icons to docs/img/items/pce93/ (2x2 BG tiles, real palette, colour 0 clear).

    MESEN=<portable Mesen.exe> SCRATCH=<dir> python tools/pce93/items.py

items.lua bombs soft blocks it filled with those items on US 1-1; the icon is the BAT 2x2 at (2x, 2y) of the item's
cell (64-wide BAT; fire: VRAM tiles $780/$781/$790/$791, bomb $782.., skate $786.., palette 11).
"""
import os, subprocess
from pathlib import Path
from PIL import Image
from vram_render import load, tile

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "docs" / "img" / "items" / "pce93"
ICONS = {"fire": (1, 3, 1), "bomb": (1, 2, 2), "skate": (2, 3, 1)}   # name: (dump, cell x, cell y)

scratch = Path(os.environ["SCRATCH"]) / "pce93_items"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "items.lua").write_text((HERE / "items.lua").read_text(encoding="utf-8"), encoding="utf-8")
subprocess.run(["sh", str(HERE / "run.sh"), str(scratch / "items.lua"), "us"], check=True, capture_output=True)
OUT.mkdir(parents=True, exist_ok=True)
for name, (n, x, y) in ICONS.items():
    vram, pal, _ = load(str(scratch / ("items%d" % n)))
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for ty in range(2):
        for tx in range(2):
            e = vram[(2 * y + ty) * 64 + 2 * x + tx]
            for py, row in enumerate(tile(vram, (e & 0xFFF) * 16)):
                for px, c in enumerate(row):
                    if c:
                        im.putpixel((8 * tx + px, 8 * ty + py), pal[(e >> 12) * 16 + c])
    im.save(OUT / (name + ".png"))
    print("wrote", OUT / (name + ".png"))
