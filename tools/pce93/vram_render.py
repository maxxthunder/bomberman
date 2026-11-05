"""Render PC Engine VDC layers from a Mesen dump (vdump in lib.lua): python vram_render.py <base> [bg|spr] [out.png]
<base>.vram (64 KB), <base>.pal (512 VCE colours), <base>.spr (SAT). Colour 0 of every palette is transparent.
BG: 32x32 BAT at VRAM word 0, entry = tile (bits 0-11, 16 words each) | palette << 12. Tiles are 4 planes:
words 0-7 hold planes 0/1 (low/high byte) of rows 0-7, words 8-15 planes 2/3.
Sprites: SAT entries Y, X, pattern, attributes; 16x16 cells of 64 words (pattern word >> 1 = cell, 32 words-aligned),
attribute bits 0-3 palette (+16), bit 8 width 32, bits 12-13 height 16/32/64, bit 11 X flip, bit 15 Y flip.
"""
import sys
from PIL import Image


def load(base):
    v = open(base + ".vram", "rb").read()
    vram = [v[2 * i] | v[2 * i + 1] << 8 for i in range(len(v) // 2)]
    p = open(base + ".pal", "rb").read()
    pal = []
    for i in range(512):
        c = p[2 * i] | p[2 * i + 1] << 8
        g, r, b = c >> 6 & 7, c >> 3 & 7, c & 7
        pal.append((r * 255 // 7, g * 255 // 7, b * 255 // 7, 255))
    return vram, pal, open(base + ".spr", "rb").read()


def tile(vram, addr):
    """8x8 colour indices of the 4bpp tile at VRAM word addr."""
    rows = []
    for y in range(8):
        a, b = vram[(addr + y) & 0x7FFF], vram[(addr + 8 + y) & 0x7FFF]
        rows.append([(a >> (7 - x) & 1) | (a >> (15 - x) & 1) << 1 | (b >> (7 - x) & 1) << 2 | (b >> (15 - x) & 1) << 3 for x in range(8)])
    return rows


def bg(vram, pal, w=32, h=32):
    im = Image.new("RGBA", (w * 8, h * 8), (0, 0, 0, 0))
    px = im.load()
    for ty in range(h):
        for tx in range(w):
            e = vram[ty * w + tx]
            t, pl = tile(vram, (e & 0xFFF) * 16), e >> 12
            for y in range(8):
                for x in range(8):
                    c = t[y][x]
                    if c:
                        px[tx * 8 + x, ty * 8 + y] = pal[pl * 16 + c]
    return im


def cell(vram, addr):
    """16x16 sprite cell at VRAM word addr: 4 planes of 16 words each."""
    out = []
    for y in range(16):
        p = [vram[(addr + 16 * k + y) & 0x7FFF] for k in range(4)]
        out.append([sum((p[k] >> (15 - x) & 1) << k for k in range(4)) for x in range(16)])
    return out


def sprites(vram, pal, sat, w=512, h=512):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for n in range(63, -1, -1):          # sprite 0 has priority: draw it last
        y0, x0, pat, at = [sat[8 * n + 2 * k] | sat[8 * n + 2 * k + 1] << 8 for k in range(4)]
        if not (y0 or x0 or pat or at):  # empty entry
            continue
        y0, x0 = (y0 & 0x3FF) - 64, (x0 & 0x3FF) - 32
        cw, ch = (2 if at & 0x100 else 1), (1, 2, 4, 4)[at >> 12 & 3]
        base = (pat >> 1 & 0x3FF)
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
                        X, Y = x0 + sx * 16 + x + 64, y0 + sy * 16 + y + 64
                        if v and 0 <= X < w and 0 <= Y < h:
                            px[X, Y] = pal[256 + (at & 15) * 16 + v]
    return im   # offset (64, 64) = screen (0, 0)


if __name__ == "__main__":
    vram, pal, sat = load(sys.argv[1])
    im = bg(vram, pal) if sys.argv[2] == "bg" else sprites(vram, pal, sat)
    im.save(sys.argv[3])
