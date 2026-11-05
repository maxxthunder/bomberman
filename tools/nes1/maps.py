"""Dump the stage format of Bomberman (NES): python tools/nes1/maps.py <rom.nes> [first last]  > stages.tsv

The arena is not stored per stage. `$CA72` builds the 13 x 32 map at $0200 from three 32-byte row templates at
$E243 (border, open row, pillar row: 1 = concrete, 0 = floor), then `$CA4B` puts the item (cell type 4) and the exit
(type 5) and then 50 + 2 x stage soft blocks (type 2, an 8-bit count: `LDA #$32 / ADC $58 / ADC $58`) on random free
cells (`$CACF`), the first two under the first soft blocks. Per stage the ROM keeps only:
- the item, $CC03 + stage (1 bombs, 2 fire, 3 speed, 4 wall pass, 5 detonator, 6 bomb pass, 7 flame pass, 8 mystery);
- the enemies, 10 slots (type 1-8, 0 = empty): stages 1-25 at $D708, 26-50 at $D802 (`$D69A`), 10 bytes a stage.
Stages past 50 (password only) read the same formulas past the tables' ends. The random placement retries until it
hits a free cell, and the map has 246 (floor, minus the three start cells). In Mesen stage 95 (240 blocks) built
after 75,814 tries and stage 96 (242) never finished: the game hangs at the stage start with NMIs off. 'hang' marks
counts of 242 and up (a count of 0 means 256), the measured limit rather than the 244 the cell count allows.
Addresses are found by pattern, so the JP cart works too. Columns: stage, item, soft blocks, enemy types (slot 9
first, as loaded), hang.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import m6502

rom = m6502.prg(sys.argv[1])
a, b = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1, 50)
R = lambda x: rom[(x - 0xC000) & 0x3FFF]
it = re.search(rb"\xa6\x58\xbd(..)\x85\x5b", rom, re.S).group(1); IT = it[0] | it[1] << 8        # LDX $58 / LDA tab,X / STA $5B
m = re.search(rb"\xa2(.)\xa0(.)\xd0\x04\xa2(.)\xa0(.)\x86", rom, re.S)                           # LDX #lo / LDY #hi pairs
E2, E1 = m.group(2)[0] << 8 | m.group(1)[0], m.group(4)[0] << 8 | m.group(3)[0]
T = re.search(rb"\xbd(..)\x91\x34\xe6\x34", rom, re.S).group(1); T = T[0] | T[1] << 8              # LDA tmpl,X / STA ($34),Y
rows = [0, 0x20, 0x40] + [0x20, 0x40] * 4 + [0x20, 0]
free = sum(1 for y in range(1, 12) for x in range(1, 32) if R(T + rows[y] + x) == 0 and not (x < 3 and y < 3))
NAMES = ["", "bombs", "fire", "speed", "wall pass", "detonator", "bomb pass", "flame pass", "mystery"]
print("stage\titem\tsoft blocks\tenemies\thang")
for s in range(a, b + 1):
    if s < 26:
        base, t = E1, s
    else:
        base, t = E2, s - 25
    y = (((t - 1) & 255) * 2 & 255) * 5 & 255                      # ASL / STA / ASL / ASL / ADC: 8-bit
    en = [R(base + y + k) for k in range(10)]
    item = R(IT + s)
    print(f"{s}\t{NAMES[item] if item < 9 else '$%02X' % item}\t{(0x32 + 2 * s) & 255}\t{' '.join(map(str, en))}	{'hang' if ((0x32 + 2 * s) & 255 or 256) >= free - 4 else ''}")
