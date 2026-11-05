"""Rip the power-up icons of Bomberman (NES) from an in-game PPU dump (vdump.lua) at native size, real palette,
colour 0 transparent: python tools/nes1/items.py <rom.nes> <dump.txt> <outdir>   -> <outdir>/<item>.png

The item cells are map types 41-48 (item kind 1-8, `$CEF2`); their 2x2 tiles come from the metatile table $D9C6
(4 tile numbers per type, US) and their BG palette from $D994 (one byte per type): palette 2 for all eight.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import logo, m6502

NAMES = ["bomb", "fire", "speed", "wallpass", "detonator", "bombpass", "flamepass", "mystery"]
rom, d, out = m6502.prg(sys.argv[1]), logo.load(sys.argv[2]), sys.argv[3]
# the tables sit at the same offsets from the 'LDA $D9C6,X' code in both carts: find them by that instruction
mt = rom.find(bytes([0xBD]), rom.find(bytes([0xAE, 0x03, 0x06])))
mt = rom[mt + 1] | rom[mt + 2] << 8
pt = rom.find(bytes([0xA8, 0x0A, 0x0A, 0x85, 0x1A, 0xB9])) + 6
pt = rom[pt] | rom[pt + 1] << 8
os.makedirs(out, exist_ok=True)
table = 1 if d["CTRL"][0] & 0x10 else 0
for k, name in enumerate(NAMES):
    t = 41 + k
    tiles = list(rom[mt - 0xC000 + 4 * t:mt - 0xC000 + 4 * t + 4])
    logo.metatiles(d, rom[pt - 0xC000 + t], table, [tiles]).save(os.path.join(out, name + ".png"))
    print(name, f"type {t}", "tiles", " ".join("%02X" % x for x in tiles), "palette", rom[pt - 0xC000 + t])
