"""Unused-graphics sweep: OR together Mesen CDL dumps (CDLHEX hex text, see lib.lua cdl_dump / scene_cdl.lua), list the
non-empty runs of ROM never read as code, data or DMA, and render a run as 4bpp tiles (grey, plus a CGRAM dump's palette).
python unused_tiles.py list cdl.hex [...]                       -> runs >= 32 bytes in banks $C0-$C2
python unused_tiles.py render rom out.png start end cgram.hex pal cdl.hex [...]   (start/end = SNES hex addresses)
Old dumps made before lib.lua started at index 0 (524,287 bytes long) are shifted by one; they are realigned here."""
import binascii, sys
from PIL import Image, ImageDraw


def cdl(paths):
    c = bytearray(0x80000)
    for p in paths:
        h = open(p).read().split()[-1]
        b = binascii.unhexlify(h[:len(h) // 2 * 2])
        o = 0x80000 - len(b)  # 1 for the old off-by-one dumps
        for i, v in enumerate(b): c[i + o] |= v
    return c


def tile(rom, off):
    return [[sum((rom[off + (p // 2) * 16 + y * 2 + (p & 1)] >> (7 - x) & 1) << p for p in range(4)) for x in range(8)] for y in range(8)]


def runs(rom, c, lo=0, hi=0x30000, minlen=32):
    out, s = [], None
    for i in range(lo, hi + 1):
        u = i < hi and c[i] == 0
        if u and s is None: s = i
        if not u and s is not None:
            if i - s >= minlen and len(set(rom[s:i])) > 2: out.append((s, i))
            s = None
    return out


def render(rom, c, start, end, cg, p, out, cols=16, scale=3):
    pal = [((w & 31) * 255 // 31, (w >> 5 & 31) * 255 // 31, (w >> 10 & 31) * 255 // 31) for w in (cg[i] | cg[i + 1] << 8 for i in range(0, 512, 2))]
    n = (end - start) // 32; rows = (n + cols - 1) // cols
    im = Image.new('RGB', (cols * 16 + 8, rows * 8), (40, 40, 40))
    for t in range(n):
        tl = tile(rom, start + t * 32)
        for y in range(8):
            for x in range(8):
                v = tl[y][x]; X, Y = t % cols * 8 + x, t // cols * 8 + y
                im.putpixel((X, Y), (v * 17,) * 3)
                im.putpixel((X + cols * 8 + 8, Y), pal[128 + 16 * p + v] if v else (0, 0, 0))
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST); d = ImageDraw.Draw(im)
    for t in range(n):
        if not any(c[start + t * 32:start + t * 32 + 32]):
            for ox in (0, (cols * 8 + 8) * scale):
                x, y = ox + t % cols * 8 * scale, t // cols * 8 * scale
                d.rectangle([x, y, x + 8 * scale - 1, y + 8 * scale - 1], outline=(255, 0, 0))
    im.save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        rom = open(sys.argv[2], 'rb').read(); c = cdl(sys.argv[3:])
        for s, e in runs(rom, c): print(f'${0xC00000 + s:06X}-${0xC00000 + e - 1:06X} {e - s:5d}')
    else:
        rom = open(sys.argv[2], 'rb').read()
        start, end = (int(a, 16) - 0xC00000 for a in sys.argv[4:6])
        cg = binascii.unhexlify(open(sys.argv[6]).read().split()[-1])
        render(rom, cdl(sys.argv[8:]), start, end, cg, int(sys.argv[7]), sys.argv[3])
