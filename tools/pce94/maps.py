"""Bomberman '94 stage maps: decode, list and render. python tools/pce94/maps.py <rom> <outdir> [gfx.json]

Map table: bank $1B $9DBE (file $37DBE), 5 bytes per map: bank, pointer (logical, bank at $4000), width, height in
16x16 cells. The stage code ($F022) looks the map up from $B7 (map id = $CBCD[$CBC6[area] + stage] + room $B6),
decodes it with the routine at $EA40/$EA60 into the cell grid at $2FB6 and draws each cell as 2x2 BAT words from
an 8-byte-per-cell table at ($95) with bank $341B at $4000.
Compression ($EA60): LZSS, bits read MSB first. Flag bit 1: a literal byte (8 bits). Flag 0: offset (8 bits) and
length (4 bits) + 2, copied from a 256-byte ring buffer that starts filled with $20, write position starting at $EF.
"""
import os, sys
TABLE = 0x1B * 0x2000 + 0x1DBE
NMAPS = 59


def entries(rom):
    for i in range(NMAPS):
        b, lo, hi, w, h = rom[TABLE + 5 * i:TABLE + 5 * i + 5]
        yield i, b * 0x2000 + ((hi << 8 | lo) - 0x4000), w, h


def decode(rom, off, n):
    """Returns (cells, bytes of input used)."""
    ring = bytearray([0x20]) * 256
    w = 0xEF
    pos, bitbuf, nbits = off, 0, 0
    out = bytearray()

    def bits(k):
        nonlocal pos, bitbuf, nbits
        v = 0
        for _ in range(k):
            if nbits == 0:
                bitbuf, nbits = rom[pos], 8
                pos += 1
            v = v << 1 | (bitbuf >> 7 & 1)
            bitbuf = bitbuf << 1 & 0xFF
            nbits -= 1
        return v
    while len(out) < n:
        if bits(1):
            c = bits(8)
            out.append(c)
            ring[w] = c
            w = (w + 1) & 0xFF
        else:
            src, ln = bits(8), bits(4) + 2
            for _ in range(ln):
                c = ring[src]
                src = (src + 1) & 0xFF
                out.append(c)
                ring[w] = c
                w = (w + 1) & 0xFF
    return bytes(out[:n]), pos - off


def area_of(rom):
    """map id -> (area 1-6, stage 1-4, room) from the stage tables $CBC6 / $CBCD (bank 1, file $2BC6 / $2BCD);
    a stage's rooms are the ids up to the next stage's first one."""
    first = rom[0x2BC6:0x2BCD]
    tab = rom[0x2BCD:0x2BCD + 21]
    out = {}
    for a in range(6):
        n = (first[a + 1] - first[a]) if a < 5 else 1
        for st in range(n):
            k = first[a] + st
            lo = tab[k]
            hi = tab[k + 1] if k + 1 < len(tab) else lo + 1
            for i in range(lo, hi):
                out[i] = (a + 1, st + 1, i - lo)
    return out


def render(rom, cells, w, h, gfx):
    """gfx = (vram words, palette rgba list, metatile table file offset) -> PIL image, 16 px per cell."""
    from PIL import Image
    import importlib.util
    spec = importlib.util.spec_from_file_location("vr", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pce93", "vram_render.py"))
    vr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vr)
    vram, pal, mt = gfx
    im = Image.new("RGB", (w * 16, h * 16), pal[0][:3])
    px = im.load()
    cache = {}
    for y in range(h):
        for x in range(w):
            c = cells[y * w + x]
            words = [rom[mt + c * 8 + 2 * k] | rom[mt + c * 8 + 2 * k + 1] << 8 for k in range(4)]
            for k, e in enumerate(words):
                key = e
                if key not in cache:
                    cache[key] = vr.tile(vram, (e & 0xFFF) * 16)
                t, pl = cache[key], e >> 12
                ox, oy = x * 16 + (k & 1) * 8, y * 16 + (k >> 1) * 8
                for yy in range(8):
                    for xx in range(8):
                        ci = t[yy][xx]
                        px[ox + xx, oy + yy] = pal[pl * 16 + ci][:3] if ci else pal[0][:3]
    return im


def schematic(cells, w, h):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w * 16, h * 16))
    d = ImageDraw.Draw(im)
    for y in range(h):
        for x in range(w):
            c = cells[y * w + x]
            col = ((c * 73) & 0xFF, (c * 151) & 0xFF, (c * 199) & 0xFF)
            d.rectangle([x * 16, y * 16, x * 16 + 15, y * 16 + 15], fill=col)
            d.text((x * 16 + 1, y * 16 + 3), "%02X" % c, fill=(255, 255, 255) if sum(col) < 380 else (0, 0, 0))
    return im


def load_gfx(d, rom):
    """Mesen dumps from cov.lua: vram_<id>.bin, pal_<id>.bin and a 'MAPGFX id ptr bank' line in log.txt.
    Returns {map id: (vram, pal, metatile file offset)}."""
    import glob, re
    g = {}
    for log in glob.glob(os.path.join(d, "*", "log.txt")):
        dd = os.path.dirname(log)
        for line in open(log):
            m = re.match(r"MAPGFX (\d+) ([0-9A-F]{4}) ([0-9A-F]{2})", line)
            if not m or not os.path.exists(os.path.join(dd, "vram_%s.bin" % m.group(1))):
                continue
            i, ptr, bank = int(m.group(1)), int(m.group(2), 16), int(m.group(3), 16)
            v = open(os.path.join(dd, "vram_%d.bin" % i), "rb").read()
            p = open(os.path.join(dd, "pal_%d.bin" % i), "rb").read()
            vram = [v[2 * k] | v[2 * k + 1] << 8 for k in range(len(v) // 2)]
            pal = []
            for k in range(256):
                c = p[2 * k] | p[2 * k + 1] << 8
                pal.append(((c >> 3 & 7) * 255 // 7, (c >> 6 & 7) * 255 // 7, (c & 7) * 255 // 7, 255))
            g.setdefault(i, (vram, pal, bank * 0x2000 + (ptr - 0x4000), ptr, bank))
    return g


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    gfx = load_gfx(sys.argv[3], rom) if len(sys.argv) > 3 else {}
    where = area_of(rom)
    seen = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else set()
    rows = []
    for i, off, w, h in entries(rom):
        cells, used = decode(rom, off, w * h)
        a = where.get(i)
        # graphics: this map's own dump, else a dump from a map of the same area (same tileset), else schematic
        src = i if i in gfx else next((j for j in sorted(gfx) if a and where.get(j, (0,))[0] == a[0]), None)
        guess = False
        if src is None and gfx and i < 50:   # not in the stage table (battle stages 50-58 each have their own tiles: schematic): the dumped map sharing the most cell values (same tile set)
            pool = [j for j in gfx if (j >= 50) == (i >= 50)] or list(gfx)   # battle stages (50-58) from battle dumps
            sets = {j: set(decode(rom, o2, w2 * h2)[0]) for j, o2, w2, h2 in entries(rom) if j in pool}
            src, guess = max(sets, key=lambda j: len(sets[j] & set(cells)) / len(set(cells))), True
        name = "map%02d" % i
        if src is not None:
            render(rom, cells, w, h, gfx[src][:3]).save(os.path.join(out, name + ".png"))
        else:
            schematic(cells, w, h).save(os.path.join(out, name + ".png"))
        rows.append((i, off, used, w, h, a, src, guess))
    for i, off, used, w, h, a, src, guess in rows:
        print(f"{i:2d} file ${off:05X} {used:4d} bytes {w}x{h} " + (f"area {a[0]} stage {a[1]} room {a[2]}" if a else "not in the stage table")
              + (f" gfx from map {src}" + (" (tile set guessed: most shared cell values)" if guess else "") if src is not None else " schematic"))
