"""Decode and draw every stage / hub / battle map of Mega Bomberman.
Usage: maps.py rom.md outdir [dumpdir]   (table at $EB556 in both versions: the data above $40000 is shared)
With dumpdir (mapdump.lua output: VRAM/CRAM and $9E6C per tileset), maps are drawn with the game's own tiles: each
cell is 4 name-table words at $9E6C + 8 * cell (top-left, top-right, bottom-left, bottom-right). Without it, or for
a map whose tileset was not dumped, a schematic with the cell numbers is drawn.

Map table $EB556: 59 entries of 6 bytes = compressed data pointer, height, width (cells). The game picks an entry
by $953F: stage rooms = $998C[$9984[area] + stage] + room ($953E, $9966), hubs = area + $2B ($BE9E), battle
stages = $31 + stage ($112BC). Data: LZSS ($CF4/$D4C): bits MSB first; 1 + 8 bits = literal, 0 + 8-bit window
position + 4-bit length (+2) = copy; 256-byte window starting at $EF, cleared to 0. One byte per cell, rows of
`width` cells, into $955C; then $FBE draws each cell from the tileset's cell table.
"""
import os, struct, sys
from PIL import Image, ImageDraw

TABLE = 0xEB556
AREA_BASE = [0x00, 0x03, 0x07, 0x0B, 0x0F, 0x13]          # $9984
STAGE_FIRST = [0x00, 0x01, 0x02, 0x04, 0x05, 0x07, 0x09, 0x0B, 0x0C, 0x0E, 0x11, 0x13, 0x15, 0x18, 0x1A, 0x1C,
               0x1D, 0x1F, 0x22, 0x25, 0x2B]               # $998C (index 20 ends area 6)
STAGES = [3, 4, 4, 4, 4, 1]


def unlz(d, p, n):
    win = bytearray(256); wp = 0xEF; out = bytearray(); buf = d[p]; p += 1; left = 8
    def bits(k):
        nonlocal buf, left, p
        v = 0
        for _ in range(k):
            v = v << 1 | (buf >> 7) & 1; buf = (buf << 1) & 0xFF; left -= 1
            if left == 0: buf = d[p]; p += 1; left = 8
        return v
    while len(out) < n:
        if bits(1):
            c = bits(8); win[wp] = c; wp = (wp + 1) & 0xFF; out.append(c)
        else:
            src = bits(8); k = bits(4) + 2
            while k and len(out) < n:
                c = win[src]; src = (src + 1) & 0xFF; win[wp] = c; wp = (wp + 1) & 0xFF; out.append(c); k -= 1
    return out, p


def entries(d):
    for i in range(59):
        yield (i,) + struct.unpack('>IBB', d[TABLE + 6 * i:TABLE + 6 * i + 6])


def uses():
    u = {}
    for a in range(6):
        for s in range(STAGES[a]):
            k = AREA_BASE[a] + s
            for r in range(STAGE_FIRST[k], STAGE_FIRST[k + 1]):
                u[r] = 'area %d stage %d room %d' % (a + 1, s + 1, r - STAGE_FIRST[k] + 1) if a < 5 else 'area 6 room %d' % (r - STAGE_FIRST[k] + 1)
    for a in range(6): u[0x2B + a] = 'area %d hub' % (a + 1)
    for s in range(10): u[0x31 + s] = 'battle stage %d' % (s + 1)
    return u


COL = {0x0: (40, 40, 48), 0x1: (90, 90, 100), 0x2: (176, 112, 64), 0x6: (60, 140, 60)}


def draw(cells, w, h, title, cs=12):
    im = Image.new('RGB', (w * cs, h * cs + 14), (255, 255, 255)); dr = ImageDraw.Draw(im)
    dr.text((2, 1), title, fill=(0, 0, 0))
    for y in range(h):
        for x in range(w):
            c = cells[y * w + x]; k = c & 0xF
            col = COL.get(k, ((k * 53) % 200 + 40, (k * 97) % 200 + 40, 200))
            dr.rectangle([x * cs, 14 + y * cs, x * cs + cs - 1, 14 + y * cs + cs - 1], fill=col)
            if k not in COL or c & 0xF0: dr.text((x * cs + 1, 14 + y * cs), '%X' % (c >> 4 if k in COL else k), fill=(255, 255, 255))
    return im


def draw_gfx(d, cells, w, h, title, vram, cram, tab):
    from vdp import palette, tile
    pal = palette(cram); im = Image.new('RGB', (w * 16, h * 16 + 14), (255, 255, 255)); px = im.load()
    for y in range(h):
        for x in range(w):
            for q in range(4):
                e = struct.unpack('>H', d[tab + 8 * cells[y * w + x] + 2 * q:tab + 8 * cells[y * w + x] + 2 * q + 2])[0]
                t = tile(vram, e & 0x7FF, e & 0x800, e & 0x1000); pl = (e >> 13) & 3
                ox, oy = x * 16 + (q & 1) * 8, 14 + y * 16 + (q >> 1) * 8
                for yy in range(8):
                    for xx in range(8):
                        px[ox + xx, oy + yy] = pal[pl * 16 + t[yy][xx]] if t[yy][xx] else pal[0]
    ImageDraw.Draw(im).text((2, 1), title, fill=(0, 0, 0))
    return im


def tileset_of(i):
    """$953A in force when map i is shown: the area for its rooms and hub, $112FE[stage] for battle maps."""
    if i >= 0x31: return [7, 2, 8, 0, 4, 9, 3, 1, 10, 11][i - 0x31]
    if i >= 0x2B: return i - 0x2B
    return next(a for a in range(5, -1, -1) if STAGE_FIRST[AREA_BASE[a]] <= i)


if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read(); out = sys.argv[2]; os.makedirs(out, exist_ok=True); u = uses()
    sets = {}   # tileset -> (vram, cram, cell table); hub/battle scenes for their own maps, stage scenes for rooms
    if len(sys.argv) > 3:
        dd = sys.argv[3]
        for l in open(os.path.join(dd, 'scenes.txt')):
            n, ts, mp, tab = l.split(); ts, mp, tab = int(ts), int(mp, 16), int(tab, 16)
            key = ('hub' if n.startswith('hub') else 'room', ts) if not n.startswith('battle') else ('battle', mp)
            sets[key] = (open(os.path.join(dd, n + '.vram'), 'rb').read(), open(os.path.join(dd, n + '.cram'), 'rb').read(), tab, n)
    for i, p, h, w in entries(d):
        cells, end = unlz(d, p, w * h)
        name = u.get(i, 'not used'); ts = tileset_of(i)
        key = ('battle', i) if i >= 0x31 else ('hub', ts) if i >= 0x2B else ('room', ts)
        title = 'map $%02X  $%05X  %dx%d  %s' % (i, p, w, h, name)
        if key in sets:
            v, c, tab, n = sets[key]; im = draw_gfx(d, cells, w, h, title + '  (tiles: ' + n + ')', v, c, tab)
        else: im = draw(cells, w, h, title)
        im.save(os.path.join(out, 'map_%02X.png' % i))
        print('%02X %05X-%05X %2dx%2d %-26s kinds %s' % (i, p, end, w, h, name, ' '.join('%02X' % k for k in sorted(set(cells)))))
