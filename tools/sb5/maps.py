"""SB5 stage layouts (Normal rooms, bosses, battle stages, debug rooms) and their renders.
Format (found by watching the map build in Mesen):
  script op 0A <layout> <set> (handler $C2:0BED) stores $1B7E=layout, $1B7D=set; $C0:3550 builds the map.
  layout n: $D0:A000 + 3(n-1) -> 24-bit pointer to a 3-byte entry -> 24-bit pointer to a stream that the
    text/tile decompressor ($C0:1CB0, see textwin.py) expands to 256 bytes = a 16x16 grid of cell types
    (row-major; the field is columns 0-14, rows 0-12) at $7E:2500 -> $2400.
  set s: $D0:8000 + 2(s-1) -> 16-bit pointer (bank $D0) to a cell-type -> attribute table ([$9C]);
    attributes go to $7E:2700/$2800 and, masked with $B0, to the live collision map $7E:1052 (16 per row).
    Attribute bit 7 = solid (hard block or wall); $30 = soft block. Type 0 is always solid.
  $D0:0000 + 2(s-1) -> per-set metatile table (4 BG tile words per cell type), used to draw the BG.
Soft blocks are placed at run time (randomly in Battle), so a layout holds only walls, floor and fixed blocks.
Usage: maps.py rom [rooms.txt laysets.txt outdir]   rooms.txt = "ROOM rr cur cc set ss lay ll" lines from the Mesen sweep,
  laysets.txt = "rr ll/ss ..." layouts written to $1B7E while room rr ran;
  without it, prints every layout's pointer and type histogram."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textwin import Stream  # noqa: E402

NLAYOUT = 0x297 // 3  # the first entry's pointer is $D0:A297, right after the table: 221 layouts


def p24(rom, a):
    a &= 0x3FFFFF
    return rom[a] | rom[a + 1] << 8 | rom[a + 2] << 16


def layout(rom, n):
    src = p24(rom, p24(rom, 0xD0A000 + 3 * (n - 1)))
    return src, Stream(rom, src & 0x3FFFFF).take(256)


def attrs(rom, s):
    base = 0xD00000 | rom[0x108000 + 2 * (s - 1)] | rom[0x108001 + 2 * (s - 1)] << 8
    return [0x80] + [rom[(base & 0x3FFFFF) + t] for t in range(1, 256)]


def render(rom, n, s, scale=6):
    from PIL import Image
    _, cells = layout(rom, n)
    at = attrs(rom, s) if s else None
    im = Image.new("RGB", (15 * scale, 13 * scale))
    px = im.load()
    for y in range(13):
        for x in range(15):
            t = cells[16 * y + x]
            a = at[t] if at else (0x80 if t == 0 else 0)
            col = (70, 70, 80) if a & 0x80 else (170, 110, 50) if a & 0x30 else (60, 150, 70) if not a & 0x40 else (60, 110, 170)
            if not at:  # no set known: shade by type number
                col = (40 + (t * 37) % 200, 40 + (t * 91) % 200, 40 + (t * 53) % 200)
            for i in range(scale):
                for j in range(scale):
                    px[x * scale + i, y * scale + j] = col
    return im


def sheet(rom, items, path, cols=8, scale=6):
    """items: (layout, set, label) -> one labelled contact sheet."""
    from PIL import Image, ImageDraw
    w, h = 15 * scale + 8, 13 * scale + 22
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (cols * w, rows * h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for k, (n, s, label) in enumerate(items):
        x, y = (k % cols) * w + 4, (k // cols) * h + 4
        im.paste(render(rom, n, s, scale), (x, y + 14))
        d.text((x, y), label, fill=(0, 0, 0))
    im.save(path)


def montage(rom, rooms, lays, shots, outdir):
    """Mesen screenshots (s<room>.png, taken 360 frames after entering the room) on labelled sheets."""
    from PIL import Image, ImageDraw
    from scripts import name
    groups = [("zone1", range(0x0D, 0x1C)), ("zone2", range(0x1C, 0x2B)), ("zone3", range(0x2B, 0x3A)),
              ("zone4", range(0x3A, 0x49)), ("zone5a", range(0x49, 0x58)), ("zone5b", range(0x58, 0x67)),
              ("bosses_bonus", range(0x67, 0x74)), ("battle", range(0x74, 0xA8)), ("other", [0xA8, 0xAC, 0xAD, 0xAE])]
    for gname, rs in groups:
        rs = [r for r in rs if os.path.exists(os.path.join(shots, "s%02X.png" % r))]
        cols = min(len(rs), 4 if gname == "battle" else 5)
        W, H = 192, 168 + 24
        im = Image.new("RGB", (cols * W, ((len(rs) + cols - 1) // cols) * H), (255, 255, 255))
        d = ImageDraw.Draw(im)
        for k, r in enumerate(rs):
            x, y = (k % cols) * W, (k // cols) * H
            im.paste(Image.open(os.path.join(shots, "s%02X.png" % r)).convert("RGB").resize((192, 168)), (x, y + 24))
            ls = [n for n, _ in lays.get(r, [])]
            lab = name(r) if 0x0D <= r < 0x71 else ("stage %d/%d" % ((r - 0x74) // 4 + 1, (r - 0x74) % 4) if 0x74 <= r < 0xA8 else "")
            d.text((x + 2, y + 1), "$%02X %s  L%s" % (r, lab, "/".join("%02X" % n for n in ls)), fill=(0, 0, 0))
            d.text((x + 2, y + 12), " ".join("$%06X" % layout(rom, n)[0] for n in ls[:2]), fill=(0, 0, 0))
        im.save(os.path.join(outdir, "rooms_%s.png" % gname))


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    if len(sys.argv) < 3:
        for n in range(1, NLAYOUT + 1):
            src, cells = layout(rom, n)
            print("%02X %06X types %s" % (n, src, " ".join("%02X" % t for t in sorted(set(cells[16 * y + x] for y in range(13) for x in range(15))))))
        sys.exit()
    rooms, lays = {}, {}
    for line in open(sys.argv[2]):
        f = line.split()
        if f and f[0] == "ROOM":
            rooms[int(f[1], 16)] = (int(f[7], 16), int(f[5], 16))
    for line in open(sys.argv[3]):  # "room lay/set ..." : every layout written to $1B7E while the room ran
        f = line.split()
        lays[int(f[0], 16)] = [tuple(int(y, 16) for y in x.split("/")) for x in f[1:]]
    from scripts import name  # noqa: E402
    lab = lambda r: name(r) if 0x0D <= r < 0x71 else "%02X" % r
    used = {}
    items = []
    for r in sorted(lays):
        for n, s_ in lays[r]:
            s_ = s_ or rooms.get(r, (0, 0))[1]
            used.setdefault(n, []).append((r, s_))
            items.append((n, s_, "%s r%02X L%02X" % (lab(r), r, n)))
    os.makedirs(sys.argv[4], exist_ok=True)
    sheet(rom, items, os.path.join(sys.argv[4], "room_layouts.png"), cols=10)
    un = []
    for n in range(1, NLAYOUT + 1):
        if n not in used:
            near = min(used, key=lambda u: abs(u - n))
            un.append((n, used[near][0][1], "L%02X %06X" % (n, layout(rom, n)[0])))
    if len(sys.argv) > 5:  # screenshot directory
        montage(rom, rooms, lays, sys.argv[5], sys.argv[4])
    print("rooms", len(lays), "layouts used", len(used), "unused", " ".join("%02X" % u[0] for u in un))
