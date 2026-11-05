"""Rip the fire, bomb and roller-skate icons to docs/img/items/pce90/ (2x2 BG tiles, real palette, colour 0 clear).

    MESEN=<portable Mesen.exe> SCRATCH=<dir> python tools/pce90/items.py

items.lua bombs soft blocks it filled with those items on 1-1; the icon is the BAT 2x2 at (2x, 2y) of the item's cell
(128-wide BAT; fire: VRAM tiles $400/$401/$410/$411, bomb $402.., skate $406.., palette 12).
"""
import os, subprocess
from pathlib import Path
from logo import render

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "docs" / "img" / "items" / "pce90"
ICONS = {"fire": (1, 3, 1), "bomb": (1, 2, 2), "skate": (2, 3, 1)}   # name: (dump, cell x, cell y)

scratch = Path(os.environ["SCRATCH"]) / "pce90_items"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "items.lua").write_text((HERE / "items.lua").read_text(encoding="utf-8"), encoding="utf-8")
log = subprocess.run(["sh", str(HERE / "run.sh"), str(scratch / "items.lua")], capture_output=True, text=True, check=True).stdout
dumps = {}
for line in log.splitlines():
    k, _, v = line.partition(" ")
    if k[:-1] in ("VRAM", "PAL"):
        dumps.setdefault(int(k[-1]), {})[k[:-1]] = bytes.fromhex(v.strip())
OUT.mkdir(parents=True, exist_ok=True)
for name, (n, x, y) in ICONS.items():
    render(dumps[n], 2 * x, 2 * y, 2, 2).save(OUT / (name + ".png"))
    print("wrote", OUT / (name + ".png"))
