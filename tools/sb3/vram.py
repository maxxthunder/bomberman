"""Render SNES BG layers / sprites from a Mesen dump (the VRAM/CGRAM/OAM/PPU lines printed by logo.lua).
Usage: python tools/sb3/vram.py dump.out outprefix  -> outprefix_bg1.png ... _obj.png (transparent where colour 0)."""
import re
import sys
from PIL import Image

txt = open(sys.argv[1]).read()
VRAM = bytes.fromhex(re.search(r"^VRAM (\w+)", txt, re.M).group(1))
CG = bytes.fromhex(re.search(r"^CGRAM (\w+)", txt, re.M).group(1))
OAM = bytes.fromhex(re.search(r"^OAM (\w+)", txt, re.M).group(1))
PPU = dict(kv.split("=", 1) for kv in re.search(r"^PPU (.*)", txt, re.M).group(1).split())


def color(i):
    c = CG[2 * i] | CG[2 * i + 1] << 8
    return ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31, 255)


def tile(base, n, bpp):
    """8x8 tile -> rows of colour indices. base/n in bytes / tile number."""
    a = (base + n * 8 * bpp) & 0xFFFF
    rows = []
    for y in range(8):
        row = []
        for x in range(8):
            b = 7 - x
            v = 0
            for p in range(bpp // 2):
                v |= (VRAM[(a + p * 16 + 2 * y) & 0xFFFF] >> b & 1) << 2 * p
                v |= (VRAM[(a + p * 16 + 2 * y + 1) & 0xFFFF] >> b & 1) << 2 * p + 1
            row.append(v)
        rows.append(row)
    return rows


def bg(i, bpp, crop=True):
    L = lambda k: PPU[f"ppu.layers[{i}].{k}"]
    tm, chr_ = int(L("tilemapAddress")) * 2, int(L("chrAddress")) * 2
    w, h = (64 if L("doubleWidth") == "true" else 32), (64 if L("doubleHeight") == "true" else 32)
    img = Image.new("RGBA", (w * 8, h * 8))
    px = img.load()
    for ty in range(h):
        for tx in range(w):
            scr = (tx >= 32) + (ty >= 32) * (2 if w == 64 else 1)
            e = tm + scr * 0x800 + ((ty % 32) * 32 + tx % 32) * 2
            v = VRAM[e & 0xFFFF] | VRAM[(e + 1) & 0xFFFF] << 8
            t = tile(chr_, v & 0x3FF, bpp)
            pal = (v >> 10 & 7) * (1 << bpp)
            for y in range(8):
                for x in range(8):
                    c = t[7 - y if v & 0x8000 else y][7 - x if v & 0x4000 else x]
                    if c:
                        px[tx * 8 + x, ty * 8 + y] = color(pal + c)
    if not crop:
        return img
    hs, vs = int(L("hscroll")), int(L("vscroll"))
    out = Image.new("RGBA", (256, 224))
    for y in range(224):
        for x in range(256):
            out.putpixel((x, y), img.getpixel(((x + hs) % img.width, (y + vs + 1) % img.height)))
    return out


def obj():
    sizes = {0: (8, 16), 1: (8, 32), 2: (8, 64), 3: (16, 32), 4: (16, 64), 5: (32, 64)}
    small, large = sizes.get(int(PPU.get("ppu.oamMode", 0)), (8, 16))
    base = int(PPU.get("ppu.oamBaseAddress", 0)) * 2
    gap = int(PPU.get("ppu.oamAddressOffset", 0x1000)) * 2
    out = Image.new("RGBA", (256, 224))
    for n in range(127, -1, -1):
        x, y, t, at = OAM[4 * n:4 * n + 4]
        hi = OAM[0x200 + n // 4] >> (n % 4 * 2) & 3
        x |= (hi & 1) << 8
        x = x - 512 if x >= 256 else x
        sz = large if hi & 2 else small
        num = t | (at & 1) << 8
        pal = 128 + (at >> 1 & 7) * 16
        for ty in range(sz // 8):
            for tx in range(sz // 8):
                ttx = sz // 8 - 1 - tx if at & 0x40 else tx
                tty = sz // 8 - 1 - ty if at & 0x80 else ty
                tn = (num & 0xF0) + ((num + ttx) & 0x0F) + tty * 16
                b = base + (gap if tn & 0x100 else 0)
                rows = tile(b, tn & 0xFF, 4)
                for yy in range(8):
                    for xx in range(8):
                        c = rows[7 - yy if at & 0x80 else yy][7 - xx if at & 0x40 else xx]
                        X, Y = x + tx * 8 + xx, (y + ty * 8 + yy + 1) % 256
                        if c and 0 <= X < 256 and Y < 224:
                            out.putpixel((X, Y), color(pal + c))
    return out


if __name__ == "__main__":
    p = sys.argv[2]
    for i, bpp in ((0, 4), (1, 4), (2, 2)):
        bg(i, bpp).save(f"{p}_bg{i + 1}.png")
    obj().save(f"{p}_obj.png")
