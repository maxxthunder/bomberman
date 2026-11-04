"""Title logo from a title-screen dump made by logodump.lua: python logo.py <dir>/<name> card|demo out.png
Reads <name>_vram.bin (64 KB), <name>_pal.bin (VCE, 512 colours) and <name>_spr.bin (SAT). Both logos are sprites
(16x16 cells of 4 planes x 16 words; SAT entry = Y, X, pattern, attributes, see renderer below).
  card: every sprite with palette 2 (BOMBER MAN '94 and the comet behind it, which shares the same cells); the
        comet's colours 10, 12, 13 and 15 (blue to white) are dropped, keeping the letters.
  demo: palettes 0 (BOMBER MAN and the bomb) and 2 (the '94, which cycles its colours; this is the frame dumped),
        above screen y 130 (palette 1 is SPECIAL VERSION and the copyright line).
Colour 0 transparent, cropped tight, native resolution.
"""
import sys
from PIL import Image


def load(base):
    v = open(base + "_vram.bin", "rb").read()
    vram = [v[2 * i] | v[2 * i + 1] << 8 for i in range(len(v) // 2)]
    p = open(base + "_pal.bin", "rb").read()
    pal = []
    for i in range(512):
        c = p[2 * i] | p[2 * i + 1] << 8
        g, r, b = c >> 6 & 7, c >> 3 & 7, c & 7
        pal.append((r * 255 // 7, g * 255 // 7, b * 255 // 7, 255))
    return vram, pal, open(base + "_spr.bin", "rb").read()


def cell(vram, addr):
    out = []
    for y in range(16):
        p = [vram[(addr + 16 * k + y) & 0x7FFF] for k in range(4)]
        out.append([sum((p[k] >> (15 - x) & 1) << k for k in range(4)) for x in range(16)])
    return out


def render(vram, pal, sat, keep):
    """Sprites for which keep(palette, screen y) is true; keep colour index c only if keep(palette, y, c)."""
    im = Image.new("RGBA", (256, 240), (0, 0, 0, 0))
    px = im.load()
    for n in range(63, -1, -1):          # sprite 0 has priority: draw it last
        y0, x0, pat, at = [sat[8 * n + 2 * k] | sat[8 * n + 2 * k + 1] << 8 for k in range(4)]
        y0, x0, pl = (y0 & 0x3FF) - 64, (x0 & 0x3FF) - 32, at & 15
        if not (y0 or x0 or pat or at) or not keep(pl, y0):
            continue
        cw, ch = (2 if at & 0x100 else 1), (1, 2, 4, 4)[at >> 12 & 3]
        base = pat >> 1 & 0x3FF
        if cw == 2:
            base &= ~1
        if ch == 2:
            base &= ~2
        if ch == 4:
            base &= ~6
        for cy in range(ch):
            for cx in range(cw):
                c = cell(vram, (base + cy * 2 + cx) * 64)
                sx = (cw - 1 - cx) if at & 0x800 else cx
                sy = (ch - 1 - cy) if at & 0x8000 else cy
                for y in range(16):
                    for x in range(16):
                        v = c[15 - y if at & 0x8000 else y][15 - x if at & 0x800 else x]
                        X, Y = x0 + sx * 16 + x, y0 + sy * 16 + y
                        if v and keep(pl, y0, v) and 0 <= X < 256 and 0 <= Y < 240:
                            px[X, Y] = pal[256 + pl * 16 + v]
    return im


KEEP = {
    "card": lambda pl, y, c=1: pl == 2 and c not in (10, 12, 13, 15),
    "demo": lambda pl, y, c=1: pl in (0, 2) and y < 130,
}

if __name__ == "__main__":
    base, ver, out = sys.argv[1:4]
    im = render(*load(base), KEEP[ver])
    im.crop(im.getbbox()).save(out)
