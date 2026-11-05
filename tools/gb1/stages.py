"""Arena layouts of Bomberman GB (JP) / Wario Blast: the 40 entries of the stage table and what uses them.
Usage: python tools/gb1/stages.py <rom.gb> [<cdl> ...] > disasm/gb1/stages_<ver>.tsv
$00:1570 (run in bank 8) -> $00:1608: word table $08:5C19 (Wario $00:173C, $08:5FA3) indexed by $C3F0. Entry =
8-byte header (pointers to the 64-byte map, the metablock table (4 sub-blocks each), the sub-block tiles (2 x 2
tiles), a 4th table) + the map: 8 x 8 metablocks of 4 x 4 tiles = the whole 32 x 32 BG map. 0-31 are the game's stages (n / 4 + 1 = round, n % 4 =
stage, 3 = boss); 32-39 the multitap battle arenas ($09:47C3: $C3F0 = $20 | ($C3EF & $0F)). The table ends at
$08:6927 in JP (zeros follow), and the first header follows the table in both. Soft blocks are placed at random afterwards ($01:4C19: count $01:4C9D, keep-free cells
$01:4CC5)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import sm83

rom = open(sys.argv[1], "rb").read()
cdl = sm83.load_cdl(sys.argv[2:], len(rom))
f = lambda a: 8 * 0x4000 + a - 0x4000
w = lambda a: rom[f(a)] | rom[f(a) + 1] << 8
k = rom.find(bytes.fromhex("6F260029 5D5421".replace(" ", "")), 0, 0x4000)   # the table lookup at $00:1608 / $00:173C
tab = rom[k + 7] | rom[k + 8] << 8
print("entry\tuse\theader\tmap\tmap read\tshared with")
first = {}
for i in range(40):
    p = w(tab + 2 * i)
    m = w(p)
    use = f"round {i // 4 + 1} {'boss' if i % 4 == 3 else 'stage %d' % (i % 4 + 1)}" if i < 32 else f"battle arena {i - 31}"
    rd = sum(cdl[f(m) + k] >> 1 & 1 for k in range(64))
    print(f"{i}\t{use}\t08:{p:04X}\t08:{m:04X}\t{rd}/64\t{first.get(p, '')}")
    first.setdefault(p, i)
