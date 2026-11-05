"""Rip the shop's technique icons (the 8 things the password's shop byte $C38D holds) from a VRAM dump of the shop.
Usage: python tools/gb3/items.py <shop.vram> <out dir>     (shop.vram: items.lua, e.g. v28.vram)
The shop window is BG tiles: icon n of the top row at map (3 + 4n, 8), the bottom row at (3 + 4n, 11), each 2 x 2
tiles. Shop bit order ($0A:7778) = price order on screen ($0D:6AEA): K kick 1, D dash 1, L line bomb 1, F full power (フルパワー) 7,
M1-M4 motorbike levels 2, 3... (prices 1, 2, 2, 3). Native 16 x 16, DMG shades through BGP, colour 0 transparent."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "emu"))
import gbvram

NAMES = ["kick", "dash", "line", "full", "moto1", "moto2", "moto3", "moto4"]   # $C38D bits 0-7
v = gbvram.load(sys.argv[1])
os.makedirs(sys.argv[2], exist_ok=True)
for n, name in enumerate(NAMES):
    gbvram.render_map(v, 3 + 4 * (n % 4), 8 if n < 4 else 11, 2, 2, transparent=True).save(os.path.join(sys.argv[2], name + ".png"))
print(len(NAMES), "icons")
