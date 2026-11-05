"""Render NES PPU dumps (vdump.lua output lines) to PNG, for the title logos and item icons of nes1 / nes2.

python tools/nes1/logo.py nt <dump.txt> <png> [nt]               whole nametable nt (0-3), attribute palettes
python tools/nes1/logo.py crop <dump.txt> <png> x y w h [nt] [sprites]
                                                                  tiles x..x+w-1, y..y+h-1 of a nametable; colour 0
                                                                  and the region's corner colour (a filled backdrop)
                                                                  transparent, cropped to the bounding box; sprites=1
                                                                  also draws the OAM sprites over it (8x8 or 8x16)
python tools/nes1/logo.py chr <dump.txt> <png> <pal 0-7>         both pattern tables, 16x16 tiles each, one palette
python tools/nes1/logo.py tiles <dump.txt> <png> <pal> <table 0/1> t0 t1 t2 t3 [...]
                                                                  2x2 metatiles (rows of 4 numbers: TL TR BL BR),
                                                                  placed side by side, colour 0 transparent
The dump line: 'VDUMP name PPU <$0000-$2FFF hex> PAL <32 bytes> OAM <256 bytes> CTRL <ppuctrl>'. Tiles are 2bpp
(16 bytes: plane 0 then plane 1); the colours are Mesen 2's default NES palette.
"""
import sys
from PIL import Image

NESPAL = bytes.fromhex(  # Mesen 2's default palette, read back from screenshots of each backdrop colour
    "666666002a881412a73b00a45c007e6e00406c0600561d003335000b4800005200004f0800404d000000000000000000"
    "adadad155fd94240ff7527fea01accb71e7bb53120994e006b6d003887000c9300008f32007c8d000000000000000000"
    "fffeff64b0ff9290ffc676fff36afffe6eccfe8170ea9e22bcbe0088d8005ce43045e08248cdde4f4f4f000000000000"
    "fffeffc0dfffd3d2ffe8c8fffbc2fffec4eafeccc5f7d8a5e4e594cfef96bdf4abb3f3ccb5ebf2b8b8b8000000000000")
RGB = [tuple(NESPAL[3 * i:3 * i + 3]) for i in range(64)]


def load(path):
    for line in open(path):
        if line.startswith("VDUMP "):
            f = line.split()
            d = dict(zip(f[2::2], f[3::2]))
            return {k: bytes.fromhex(v) for k, v in d.items()}
    raise SystemExit("no VDUMP line")


def tile(ppu, table, n):
    o = table * 0x1000 + n * 16
    return [[(ppu[o + y] >> (7 - x) & 1) | (ppu[o + 8 + y] >> (7 - x) & 1) << 1 for x in range(8)] for y in range(8)]


def colour(pal, p, c):
    return RGB[pal[0] & 0x3F if c == 0 else pal[4 * p + c] & 0x3F] + (255,)


def nametable(d, nt=0, x0=0, y0=0, w=32, h=30, transparent=False):
    ppu, pal = d["PPU"], d["PAL"]
    table = 1 if d["CTRL"][0] & 0x10 else 0
    im = Image.new("RGBA", (w * 8, h * 8), (0, 0, 0, 0))
    px = im.load()
    base = 0x2000 + 0x400 * nt
    for ty in range(h):
        for tx in range(w):
            X, Y = x0 + tx, y0 + ty
            n = ppu[base + Y * 32 + X]
            at = ppu[base + 0x3C0 + (Y // 4) * 8 + X // 4]
            p = at >> ((Y % 4 // 2) * 4 + (X % 4 // 2) * 2) & 3
            for y, row in enumerate(tile(ppu, table, n)):
                for x, c in enumerate(row):
                    if c or not transparent:
                        px[tx * 8 + x, ty * 8 + y] = colour(pal, p, c)
    return im


def sprites(d, im, x0, y0):
    """Draw the OAM sprites onto im (whose top left is pixel x0, y0 of the screen), back to front."""
    ppu, pal, oam, ctrl = d["PPU"], d["PAL"], d["OAM"], d["CTRL"][0]
    px = im.load()
    for k in range(63, -1, -1):
        y, t, at, x = oam[4 * k] + 1, oam[4 * k + 1], oam[4 * k + 2], oam[4 * k + 3]
        if y >= 240:
            continue
        parts = [(1 if t & 1 else 0, t & 0xFE, 0), (1 if t & 1 else 0, t | 1, 8)] if ctrl & 0x20 else [(1 if ctrl & 8 else 0, t, 0)]
        if ctrl & 0x20 and at & 0x80:
            parts = [(parts[0][0], parts[1][1], 0), (parts[0][0], parts[0][1], 8)]
        for table, n, dy in parts:
            for ty, row in enumerate(tile(ppu, table, n)):
                for tx, c in enumerate(row):
                    if not c:
                        continue
                    sx = x + (7 - tx if at & 0x40 else tx) - x0
                    sy = y + dy + (7 - ty if at & 0x80 else ty) - y0
                    if 0 <= sx < im.width and 0 <= sy < im.height:
                        px[sx, sy] = RGB[pal[16 + 4 * (at & 3) + c] & 0x3F] + (255,)


def metatiles(d, p, table, groups):
    ppu, pal = d["PPU"], d["PAL"]
    im = Image.new("RGBA", (16 * len(groups), 16), (0, 0, 0, 0))
    px = im.load()
    for g, ts in enumerate(groups):
        for k, n in enumerate(ts):
            for y, row in enumerate(tile(ppu, table, n)):
                for x, c in enumerate(row):
                    if c:
                        px[16 * g + 8 * (k % 2) + x, 8 * (k // 2) + y] = colour(pal, p, c)
    return im


if __name__ == "__main__":
    cmd, d, out = sys.argv[1], load(sys.argv[2]), sys.argv[3]
    a = [int(x, 0) for x in sys.argv[4:]]
    if cmd == "nt":
        nametable(d, a[0] if a else 0).save(out)
    elif cmd == "crop":
        im = nametable(d, a[4] if len(a) > 4 else 0, *a[:4], transparent=True)
        key = im.getpixel((0, 0))
        if key[3]:
            im.putdata([(0, 0, 0, 0) if p == key else p for p in im.getdata()])
        if len(a) > 5 and a[5]:
            sprites(d, im, a[0] * 8, a[1] * 8)
        im.crop(im.getbbox()).save(out)
    elif cmd == "chr":
        im = Image.new("RGBA", (256, 128))
        for t in range(2):
            for n in range(256):
                for y, row in enumerate(tile(d["PPU"], t, n)):
                    for x, c in enumerate(row):
                        im.putpixel((t * 128 + n % 16 * 8 + x, n // 16 * 8 + y), colour(d["PAL"][16:] if a[0] >= 4 else d["PAL"], a[0] % 4, c))
        im.save(out)
    elif cmd == "tiles":
        p, table, rest = a[0], a[1], a[2:]
        pal = d["PAL"] if p < 4 else d["PAL"][16:]
        d2 = dict(d, PAL=bytes([d["PAL"][0]]) + pal[1:])
        metatiles(d2, p % 4, table, [rest[i:i + 4] for i in range(0, len(rest), 4)]).save(out)
