"""Decode and render the stage layouts of Bomberman (PC Engine 1990, US/JP) and Users Battle.

Usage: python tools/pce90/maps.py <rom.pce> <outdir> [prefix]      -> <outdir>/<prefix>r<R>-<S>.png, index on stdout

Format (US addresses; the JP card and Users Battle use the same tables, found by pattern below):
- Stage headers, bank $0C at $4000 (`$00:ED94`): $4028 + 2*round -> table of 8 stage pointers -> 2 bytes
  [layout type, soft-block count]. Round index 8 is the battle arena (one stage).
- Layout types 0-3: $4000 + 4*type = four `slot:block` nibble pairs ($FF = none). Slots are 16x16-cell quarters of
  the 32x32 map at $244A (slot 0 top left, 1 top right, 4 bottom left, 5 bottom right; `$00:EEC5`).
  $4020/$4024 + type = the X/Y range the soft blocks are scattered over (random, `$00:ED19`, avoiding cells whose
  graphic is 5 or 7 and anything not floor), so soft blocks are not part of the map data.
- Blocks, bank $0D/$0E at $4000 (`$00:EE4A`): $00:EED5 + 2*round -> 8 block pointers; a block is 16 rows, each
  row RLE-coded into 16 tile numbers (`$00:EF1C`): $F0 ends the row early, $F1 n a b = the pair a b n times,
  $F2-$FF = the next byte (low nibble + 1) times, anything else is one tile. Tile 0-7 = floor with graphic t
  (map byte t*32 | $0A), 8 and up = solid (map byte $01), the number picking the wall graphic (`$00:EF99`).
Render: solid cells grey (shade = tile number), floor green, floor graphics 2-7 numbered (5/6/7 are the shadow
cells next to walls); the orange box is the soft-block scatter area. Unused blocks are drawn as a pair (0+1 side by
side, as layout type 3 would place them).
"""
import os, re, sys
from PIL import Image, ImageDraw

rom = open(sys.argv[1], "rb").read()
B = lambda bank, addr: bank * 0x2000 + (addr & 0x1FFF)
w16 = lambda o: rom[o] | rom[o + 1] << 8

# the round -> block-table pointer list: `LDA $284A / ASL A / TAX / LDA $xxxx,X / STA $61` in bank 0 ($00:EE55 US; `LDA $2849 ... STA $58` at $00:ED8A in Users Battle)
i = re.search(rb"\xad[\x49\x4a]\x28\x0a\xaa\xbd..\x85[\x58\x61]", rom[:0x2000], re.S).start()
blk_tab = w16(i + 6) - 0xE000   # bank 0 is mapped at $E000
HB = 0x0C                       # stage headers: bank $0C at $4000


def mem45(addr):                # banks $0D/$0E mapped at $4000/$6000 ($00:E6FC with A = $0D)
    return B(0x0D + ((addr - 0x4000) >> 13), addr)


def block(rnd, bid):
    o = mem45(w16(mem45(w16(blk_tab + 2 * rnd)) + 2 * bid))
    start, rows = o, []
    for _ in range(16):
        row = []
        while len(row) < 16:
            b = rom[o]; o += 1
            if b == 0xF0:
                break
            if b == 0xF1:
                n, a, c = rom[o:o + 3]; o += 3; row += [a, c] * n
            elif b >= 0xF2:
                row += [rom[o]] * ((b & 15) + 1); o += 1
            else:
                row.append(b)
        rows.append((row + [0] * 16)[:16])
    return start, rows


def addr(o):                    # rom offset in banks $0D/$0E -> bank:logical
    return f"{o >> 13:02X}:{0x4000 + (o - 0x1A000):04X}" if 0x1A000 <= o < 0x1E000 else f"{o >> 13:02X}:{o & 0x1FFF:04X}"


C = lambda a: B(HB, a)
types = [list(rom[C(0x4000) + 4 * t:C(0x4000) + 4 * t + 4]) for t in range(4)]
rx = list(rom[C(0x4020):C(0x4024)]); ry = list(rom[C(0x4024):C(0x4028)])
SLOT = {0: (0, 0), 1: (16, 0), 4: (0, 16), 5: (16, 16)}
SOLID = (110, 110, 110)
FLOOR = [(40, 140, 40), (60, 160, 60), (30, 120, 30), (80, 150, 70), (50, 130, 90), (25, 100, 25), (90, 170, 90), (20, 90, 60)]


def render(grid, title, sub, fn, area=None):
    S = 12
    wc = 32 if any(grid[y][16] is not None for y in range(32)) else 16
    hc = 32 if grid[16][0] is not None else 16
    im = Image.new("RGB", (max(wc * S, 330), hc * S + 28), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(32):
        for x in range(32):
            t = grid[y][x]
            if t is None:
                continue
            g = 70 + (t * 37) % 110
            d.rectangle([x * S, y * S, x * S + S - 1, y * S + S - 1], fill=(g, g, g + 20) if t >= 8 else FLOOR[t])
            if t < 8 and t > 1:
                d.text((x * S + 3, y * S), "%X" % t, fill=(255, 255, 255))
    if area:
        d.rectangle(area, outline=(230, 140, 40))
    d.text((2, hc * S + 2), title, fill=(255, 255, 255))
    d.text((2, hc * S + 14), sub, fill=(200, 200, 200))
    im.save(fn)


os.makedirs(sys.argv[2], exist_ok=True)
pre = sys.argv[3] if len(sys.argv) > 3 else ""
used = set()
for rnd in range(9):
    stab = C(w16(C(0x4028 + 2 * rnd)))
    for st in range(8 if rnd < 8 else 1):
        h = C(w16(stab + 2 * st))
        typ, soft = rom[h], rom[h + 1]
        grid = [[None] * 32 for _ in range(32)]
        parts = []
        for sb in types[typ]:
            if sb == 0xFF:
                continue
            slot, bid = sb >> 4, sb & 15
            o, rows = block(rnd, bid)
            used.add((rnd, bid))
            parts.append(f"slot{slot}=blk{bid}@{addr(o)}")
            ox, oy = SLOT[slot]
            for y in range(16):
                grid[oy + y][ox:ox + 16] = rows[y]
        name = "battle" if rnd == 8 else f"{rnd + 1}-{st + 1}"
        fn = f"{pre}{'battle' if rnd == 8 else 'r' + name}.png"
        title = f"{name}  header {HB:02X}:{0x4000 + (h & 0x1FFF):04X}  type {typ}  soft blocks {soft}"
        # soft blocks: random cell (1 + random(rx), 1 + random(ry)) (`$00:ED6A`: random(X) at $E966 is 0..X-1)
        render(grid, title, " ".join(parts), os.path.join(sys.argv[2], fn), [12, 12, (rx[typ] + 1) * 12, (ry[typ] + 1) * 12])
        print(f"{name}\t{HB:02X}:{0x4000 + (h & 0x1FFF):04X}\ttype {typ}\tsoft {soft}\t{' '.join(parts)}\t{fn}")
# blocks in each round's table that no stage uses
for rnd in range(9):
    for bid in range(8):
        if (rnd, bid) in used:
            continue
        p = mem45(w16(blk_tab + 2 * rnd)) + 2 * bid
        tgt = w16(p)
        if not 0x4000 <= tgt < 0x8000:
            continue
        o, rows = block(rnd, bid)
        grid = [[None] * 32 for _ in range(32)]
        for y in range(16):
            grid[y][16 * (bid & 1):16 * (bid & 1) + 16] = rows[y]
        name = f"unused_r{rnd + 1}_blk{bid}" if rnd < 8 else f"unused_battle_blk{bid}"
        render(grid, f"round {rnd + 1 if rnd < 8 else 'battle'} block {bid} (no stage uses it)", f"pointer {addr(p)} -> {addr(o)}",
               os.path.join(sys.argv[2], pre + name + ".png"))
        print(f"unused\t{name}\tpointer {addr(p)}\tdata {addr(o)}\t{pre + name}.png")
