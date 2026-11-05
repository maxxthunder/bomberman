"""Bomberman '93 stage maps: decode every stage record and render it. python tools/pce93/maps.py <us|jp|sp> <outdir> [dumpdir...]

Stage records: bank 2 $8156 (file $4156), 8 bytes per record, index $D1 (Special Version $D8) = (world-1)*8 +
stage-1 in the Normal Game, battle stages after them (02:8066 reads it). Bytes 0-3 = one chunk id per 256-byte page
of the stage block that 02:8010 unpacks to $2FD7-$33D6 (Special Version $2FCE); byte 4 low nibble -> $80, high
nibble selects the palette set; bytes 5-7 are 0.
Chunks: pointer table at $5CC8 (Special Version $5B8E) with bank $0A/$0B at $4000-$7FFF. Packing (01:C33F / C35B):
LZSS with a 256-byte ring buffer (cleared to 0, writing from $EF). A flag byte gives 8 flags, MSB first; flag 1 =
one literal byte; flag 0 = a byte holding the ring offset, and the copy length comes from a shared length byte read
at the first of each pair of copies: the first copy takes its high nibble, the second its low nibble; length = n + 2.
Page 0 is the cell grid: 16 bytes per row, the 13x11 play field at row 1-11, column 2-14 ($2FE9 = row 1 col 2).
After unpacking, 02:80E9 passes every cell through $CF55 / $8126 (soft blocks are placed at random there), so the
rendered maps show the cells as stored, before that step.
dumpdir: Mesen dumps from cov.lua (s<record>.ram/.vram/.pal) give real graphics: each cell value seen in a dumped
grid is matched to the 2x2 BAT tiles drawn for it, and the map is drawn with them; others are drawn as hex.
"""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
ROMS = {"us": "Bomberman '93 (USA).pce", "jp": "Bomberman '93 (Japan).pce", "sp": "Bomberman '93 - Special Version (Japan).pce"}
CHUNKS = {"us": 0x5CC8, "jp": 0x5CC8, "sp": 0x5B8E}
GRID = {"us": 0x2FD7, "jp": 0x2FD7, "sp": 0x2FCE}
RECS = 2 * 0x2000 + 0x156


def chunk(rom, ver, cid):
    t = 0x0A * 0x2000 + (CHUNKS[ver] - 0x4000) + 2 * cid
    p = rom[t] | rom[t + 1] << 8
    off = 0x0A * 0x2000 + (p - 0x4000)
    ring, w, out = bytearray(256), 0xEF, bytearray()
    pos, flags, cnt, half, lenb = off, 0, 0, False, 0

    def put(c):
        nonlocal w
        ring[w] = c
        w = (w + 1) & 0xFF
        out.append(c)
    while len(out) < 256:
        if cnt == 0:
            flags, cnt = rom[pos], 8
            pos += 1
        bit = flags & 0x80
        flags = flags << 1 & 0xFF
        cnt -= 1
        b = rom[pos]
        pos += 1
        if bit:
            put(b)
            continue
        if not half:
            lenb = rom[pos]
            pos += 1
            n = lenb >> 4
        else:
            n = lenb & 15
        half = not half
        src = b
        for _ in range(n + 2):
            c = ring[src]
            src = (src + 1) & 0xFF
            put(c)
    return bytes(out[:256]), off, pos - off


def records(rom):
    out = []
    for i in range(80):
        r = rom[RECS + 8 * i:RECS + 8 * i + 8]
        if r[5:8] != b"\0\0\0" or max(r[:4]) > 0x70:
            break
        out.append(r)
    return out


def name(i):
    return f"world {i // 8 + 1} stage {i % 8 + 1}" if i < 56 else f"world 8 stage {i - 55} (no such world)" if i < 64 else f"battle stage {i - 63}"


def learn(rom, ver, dumpdirs):
    """From Mesen dumps s<record>.vram/.pal (cov.lua): for each record, the BAT width and the offset of the grid on
    the BAT that make the decoded page 0 most consistent (one 2x2 tile group per cell value), then the most common
    tile group per value. Returns {record: (table, vram, pal)}."""
    sys.path.insert(0, HERE)
    import vram_render as vr
    import collections
    recs = records(rom)
    res = {}
    for d in dumpdirs:
        for f in sorted(glob.glob(os.path.join(d, "s*.vram"))):
            base = f[:-5]
            try:
                i = int(os.path.basename(base)[1:])
            except ValueError:
                continue
            if i in res or i >= len(recs):
                continue
            vram, pal, _ = vr.load(base)
            grid = chunk(rom, ver, recs[i][0])[0]
            best = None
            for bw in (32, 64):
                for ox in range(-4, 5):
                    for oy in range(-4, 5):
                        groups = collections.defaultdict(collections.Counter)
                        for r in range(16):
                            for c in range(16):
                                tx, ty = 2 * c + ox, 2 * r + oy
                                if 0 <= tx < bw - 1 and 0 <= ty < 31:
                                    ws = tuple(vram[(ty + dy) * bw + tx + dx] for dy in (0, 1) for dx in (0, 1))
                                    groups[grid[16 * r + c]][ws] += 1
                        score = sum(cn.most_common(1)[0][1] for cn in groups.values()) - 2 * sum(len(cn) for cn in groups.values())
                        if best is None or score > best[0]:
                            best = (score, {v: cn.most_common(1)[0][0] for v, cn in groups.items()})
            res[i] = (best[1], vram, pal)
    return res


def render(grid, table, vram, pal):
    from PIL import Image
    sys.path.insert(0, HERE)
    import vram_render as vr
    im = Image.new("RGB", (16 * 16, 16 * 16), pal[0][:3])
    px = im.load()
    for r in range(16):
        for c in range(16):
            ws = table.get(grid[16 * r + c])
            if ws is None:
                continue
            for k, e in enumerate(ws):
                t, pl = vr.tile(vram, (e & 0xFFF) * 16), e >> 12
                for y in range(8):
                    for x in range(8):
                        ci = t[y][x]
                        px[c * 16 + (k & 1) * 8 + x, r * 16 + (k >> 1) * 8 + y] = pal[pl * 16 + ci][:3] if ci else pal[0][:3]
    return im


def schematic(grid):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (16 * 16, 16 * 16))
    d = ImageDraw.Draw(im)
    for r in range(16):
        for c in range(16):
            v = grid[16 * r + c]
            col = ((v * 73) & 0xFF, (v * 151) & 0xFF, (v * 199) & 0xFF)
            d.rectangle([c * 16, r * 16, c * 16 + 15, r * 16 + 15], fill=col)
            d.text((c * 16 + 1, r * 16 + 3), "%02X" % v, fill=(255, 255, 255) if sum(col) < 380 else (0, 0, 0))
    return im


if __name__ == "__main__":
    ver, out = sys.argv[1:3]
    rom = open(os.path.join(ROOT, "roms", ROMS[ver]), "rb").read()
    os.makedirs(out, exist_ok=True)
    seen = {}
    gfx = learn(rom, ver, sys.argv[3:])
    for i, r in enumerate(records(rom)):
        pages = [chunk(rom, ver, c) for c in r[:4]]
        grid = pages[0][0]
        key = bytes(r[:5])
        print(f"{i:2d} {name(i):28s} record file ${RECS + 8 * i:05X} = {r[:5].hex(' ')}  page 0 chunk ${r[0]:02X} at file ${pages[0][1]:05X} ({pages[0][2]} bytes)"
              + (f"  same as {seen[key]}" if key in seen else ""))
        seen.setdefault(key, i)
        # graphics: this record's own dump, else one of the same world (same tile set), else the hex schematic.
        # The 4 pages are the quadrants of a 2x2-screen field (top-left, top-right, bottom-left, bottom-right);
        # byte 4 (low nibble) says which are used: 0 one screen, 2 two side by side, 3 two stacked, 4 all four.
        src = i if i in gfx else next((j for j in sorted(gfx) if j // 8 == i // 8 or i >= 56 and j >= 56), None)
        draw = (lambda g: render(g, *gfx[src])) if src is not None else schematic
        mode = r[4] & 15
        quads = {0: [(0, 0, 0)], 2: [(0, 0, 0), (1, 1, 0)], 3: [(0, 0, 0), (2, 0, 1)], 4: [(0, 0, 0), (1, 1, 0), (2, 0, 1), (3, 1, 1)]}.get(mode, [(0, 0, 0)])
        from PIL import Image
        W, H = max(q[1] for q in quads) + 1, max(q[2] for q in quads) + 1
        im = Image.new("RGB", (256 * W, 256 * H))
        for pg, qx, qy in quads:
            im.paste(draw(pages[pg][0]), (256 * qx, 256 * qy))
        im.crop((0, 0, 256 * W, 256 * (H - 1) + 13 * 16)).save(os.path.join(out, f"{ver}_{i:02d}.png"))
        print("    drawn with", f"tiles of record {src}" if src is not None else "hex cell values (no dump)")
    # chunks no record uses: drawn with the tiles of the record that uses the chunk just before it
    t = 0x0A * 0x2000 + (CHUNKS[ver] - 0x4000)
    n = 0
    while 0x4000 <= (rom[t + 2 * n] | rom[t + 2 * n + 1] << 8) < 0x8000:
        n += 1
    recs = records(rom)
    used = {c for r in recs for c in r[:4]}
    for c in range(n):
        if c in used:
            continue
        near = next((i for i, r in enumerate(recs) if c - 1 in r[:4]), None)
        src = near if near in gfx else next((j for j in sorted(gfx) if near is not None and (j // 8 == near // 8 or near >= 56 and j >= 56)), None)
        g, off, ln = chunk(rom, ver, c)
        if src is not None and sum(v not in gfx[src][0] for v in g[:13 * 16]) > 20:   # tile set does not fit
            src = None
        im = render(g, *gfx[src]) if src is not None else schematic(g)
        if len(set(im.crop((0, 0, 256, 208)).getdata())) < 8:   # drew (nearly) nothing: the tile set does not fit
            src, im = None, schematic(g)
        im.crop((0, 0, 256, 13 * 16)).save(os.path.join(out, f"{ver}_chunk{c:02X}_unused.png"))
        print(f"unused chunk ${c:02X} file ${off:05X} ({ln} bytes), drawn with tiles of record {src} (chunk ${c - 1:02X} is record {near})")

