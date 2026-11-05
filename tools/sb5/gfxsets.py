"""SB5 graphics-set sweep. The loader $C0:1B04 takes a set number and a group ($0AE7); group g's table is
the 16-bit pointer at $C0:1C96+2g (bank $85), 8 bytes per set: VRAM word address, byte size, 24-bit
source, flags (bit 7 = raw copy, else the text/tile decompressor $C0:1CB0; low bits look like the
format). A set counts as unused when its source bytes are unmarked in a Mesen code/data log.
Usage: gfxsets.py rom cdl outdir   -> outdir/<group>_<set>_<source>.png (4bpp, greyscale) + a list on stdout"""
import os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textwin import DIST  # noqa: E402  (same decompressor as the text windows)

GROUPS = {0: (0xE22D, 0xE34D), 8: (0xE34D, 0xE50D), 6: (0xE50D, 0xE525), 3: (0xE525, 0xE91D), 4: (0xE91D, 0xEB45)}


def sets(rom):
    for g, (a, b) in GROUPS.items():
        for i in range((b - a) // 8):
            e = rom[0x50000 + a + 8 * i:0x50000 + a + 8 * i + 8]
            src = e[4] | e[5] << 8 | e[6] << 16
            if not 0xC0 <= src >> 16 <= 0xDF:
                break
            yield g, i + 1, e[0] | e[1] << 8, e[2] | e[3] << 8, src, e[7]


def data(rom, src, size, fl):
    if fl & 0x80:
        return rom[src & 0x3FFFFF:(src & 0x3FFFFF) + size]
    p, out = src & 0x3FFFFF, []
    while len(out) < size:
        c = rom[p]
        p += 1
        for _ in range((c & 31) + 1):
            if c >> 5 == 0:
                out.append(rom[p])
                p += 1
            else:
                k = 1 if c >> 5 == 1 else DIST[c >> 5]
                v = out[-k] if len(out) >= k else 0  # the $0200 ring starts zeroed
                out.append((v + 1) & 255 if c >> 5 == 1 else v)
    return bytes(out[:size])


def render(buf, bpp=4, width=16):
    n = len(buf) // (8 * bpp)
    im = Image.new("L", (width * 8, max(1, (n + width - 1) // width) * 8))
    px = im.load()
    for t in range(n):
        for y in range(8):
            for x in range(8):
                v = 0
                for p in range(bpp):
                    v |= (buf[t * 8 * bpp + (p // 2) * 16 + y * 2 + (p & 1)] >> (7 - x) & 1) << p
                px[(t % width) * 8 + x, (t // width) * 8 + y] = v * 255 // ((1 << bpp) - 1)
    return im


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    cdl = open(sys.argv[2], "rb").read()[9:]
    out = sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for g, i, vram, size, src, fl in sets(rom):
        o = src & 0x3FFFFF
        if any(cdl[o + k] for k in range(min(size, 64) if fl & 0x80 else 4)):
            continue
        buf = data(rom, src, size, fl)
        name = "g%d_set%02d_%06X.png" % (g, i, src)
        render(buf).resize((256, max(8, render(buf).height * 2)), Image.NEAREST).save(os.path.join(out, name))
        print("group %d set %3d  src $%06X (file 0x%06X)  vram $%04X  %5d bytes  flags $%02X  %s" % (g, i, src, o, vram, size, fl, name))
