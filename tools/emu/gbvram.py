"""Render Game Boy VRAM dumps (mesen_gb.py vdump(): VRAM 8 KB, OAM 160, BGP, OBP0, OBP1, LCDC, SCY, SCX, WY, WX).
Shared by tools/gb1-gb3.
python tools/emu/gbvram.py bg <dump.vram> <out.png> [x y w h]     BG map (32 x 32 tiles, or a tile rect of it)
python tools/emu/gbvram.py logo <dump.vram> <out.png> x y w h     tile rect, colour 0 transparent, cropped to content
python tools/emu/gbvram.py tiles <dump.vram> <out.png>             all 384 tiles, 16 per row, BGP
bgw / logow: the same from the window's map (LCDC bit 6) instead of the BG's (LCDC bit 3).
Shades are the DMG greys Mesen shows (white, $B0, $68, black) through BGP."""
import sys
from PIL import Image

GREYS = [(255, 255, 255), (176, 176, 176), (104, 104, 104), (0, 0, 0)]


def load(path):
    d = open(path, "rb").read()
    v = dict(vram=d[:0x2000], oam=d[0x2000:0x20A0])
    v.update(zip(("bgp", "obp0", "obp1", "lcdc", "scy", "scx", "wy", "wx"), d[0x20A0:0x20A8]))
    return v


def tile(vram, n):
    """tile n of 384 ($8000 + 16 n) -> 8 rows of 8 colour numbers"""
    o = n * 16
    return [[((vram[o + 2 * y] >> (7 - x)) & 1) | (((vram[o + 2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]


def bg_tile(v, e):
    """BG map entry -> tile index (LCDC bit 4: $8000 unsigned, else $9000 signed)"""
    return e if v["lcdc"] & 0x10 else 256 + ((e ^ 0x80) - 0x80)


def shade(pal, c):
    return GREYS[(pal >> (2 * c)) & 3]


def render_map(v, x0=0, y0=0, w=32, h=32, transparent=False, window=False):
    base = 0x1C00 if v["lcdc"] & (0x40 if window else 0x08) else 0x1800
    im = Image.new("RGBA", (w * 8, h * 8), (0, 0, 0, 0))
    px = im.load()
    for ty in range(h):
        for tx in range(w):
            t = tile(v["vram"], bg_tile(v, v["vram"][base + ((y0 + ty) % 32) * 32 + (x0 + tx) % 32]))
            for y, row in enumerate(t):
                for x, c in enumerate(row):
                    if c or not transparent:
                        px[tx * 8 + x, ty * 8 + y] = shade(v["bgp"], c) + (255,)
    return im


def render_tiles(v, pal=None):
    im = Image.new("RGB", (128, 192))
    for n in range(384):
        for y, row in enumerate(tile(v["vram"], n)):
            for x, c in enumerate(row):
                im.putpixel(((n % 16) * 8 + x, (n // 16) * 8 + y), shade(v["bgp"] if pal is None else pal, c))
    return im


if __name__ == "__main__":
    cmd, src, out = sys.argv[1:4]
    v = load(src)
    r = list(map(int, sys.argv[4:8]))
    if cmd in ("bg", "bgw"):
        render_map(v, *r, window=cmd == "bgw").save(out)
    elif cmd in ("logo", "logow"):
        im = render_map(v, *r, transparent=True, window=cmd == "logow")
        im.crop(im.getbbox()).save(out)
    else:
        render_tiles(v).save(out)
