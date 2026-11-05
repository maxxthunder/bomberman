"""Rip the Bomberman II power-up icons stored in the password (bomb up, fire up) from in-game PPU dumps
(tools/nes1/vdump.lua lines, taken by items.lua when the item is on screen), native size, real palette, colour 0 transparent:
python tools/nes2/items.py <dump.txt> <outdir> [palette]   -> <outdir>/bomb.png, fire.png

The item metatiles (bank 4, per-area tables from $8000; the area 1 copy: $8080 bomb = tiles 60 61 70 71, $8084
fire = 62 63 72 73) sit in pattern table 0 (the playfield's; PPUCTRL read mid-frame may name the status bar's); the palette is the one the attribute table gives the cell where
the item shows up in the dump. An icon that never showed whole in the dumps is drawn with the palette of one that
did (both sit in the same CHR and use the same item palette slot); the script says so. If neither showed, both are
drawn from the first dump with BG palette [palette] (default 0) - the committed PNGs were made that way from the
stage 1-1 dump; palette 0 was later confirmed from the code and a fire-up on screen (see docs/nes2.md).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nes1"))
import logo

ITEMS = {"bomb": [0x60, 0x61, 0x70, 0x71], "fire": [0x62, 0x63, 0x72, 0x73]}
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
dumps = []
for line in open(sys.argv[1]):
    if line.startswith("VDUMP "):
        f = line.split()
        dumps.append({k: bytes.fromhex(v) for k, v in zip(f[2::2], f[3::2])})
found = {}
for name, tiles in ITEMS.items():
    for d in dumps:
        ppu = d["PPU"]
        hit = next((a for a in range(0x2000, 0x3000) if a % 0x400 < 0x3C0 and ppu[a] == tiles[0] and ppu[a + 1] == tiles[1]
                    and ppu[a + 32] == tiles[2]), None)
        if hit is None:
            continue
        base, i = hit & ~0x3FF, hit & 0x3FF
        X, Y = i % 32, i // 32
        p = ppu[base + 0x3C0 + (Y // 4) * 8 + X // 4] >> ((Y % 4 // 2) * 4 + (X % 4 // 2) * 2) & 3
        logo.metatiles(d, p, 1, [tiles]).save(os.path.join(out, name + ".png"))
        print(name, "nametable $%04X" % hit, "palette", p)
        found[name] = (d, p)
        break
if not found:
    found["-"] = (dumps[0], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
for name, tiles in ITEMS.items():
    if name not in found:
        d, p = next(iter(found.values()))
        logo.metatiles(d, p, 1, [tiles]).save(os.path.join(out, name + ".png"))
        print(name, "not on screen in the dumps: drawn from the first dump's CHR with palette", p)
