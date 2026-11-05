"""Render SNES mode-1 BG layers from a Mesen dump (lines VRAM/CGRAM hex, from logo.lua; addresses are word addresses from ppu.layers).
Usage: bgrender.py dump.out outprefix  -> outprefix_bg1.png ... (64x32-tile maps, palette index 0 transparent)"""
import sys, binascii
from PIL import Image
L = {l.split()[0]: binascii.unhexlify(l.split()[1]) for l in open(sys.argv[1]) if l.startswith(("VRAM ", "CGRAM "))}
vram, cg = L["VRAM"], L["CGRAM"]
pal = [(lambda c: ((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))(cg[2 * i] | cg[2 * i + 1] << 8) for i in range(256)]


def tile(chr_base, n, bpp, y):
    base = chr_base + n * 8 * bpp
    row = []
    for x in range(8):
        v = 0
        for p in range(bpp):
            b = vram[(base + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF]
            v |= (b >> (7 - x) & 1) << p
        row.append(v)
    return row


def render(map_word, chr_word, bpp, out, wide=True):
    W = 64 if wide else 32
    im = Image.new("RGBA", (W * 8, 256), (0, 0, 0, 0))
    px = im.load()
    for ty in range(32):
        for tx in range(W):
            scr = tx // 32
            e = map_word * 2 + scr * 0x800 + (ty * 32 + tx % 32) * 2
            v = vram[e] | vram[e + 1] << 8
            n, p, hf, vf = v & 0x3FF, v >> 10 & 7, v >> 14 & 1, v >> 15
            for y in range(8):
                r = tile(chr_word * 2, n, bpp, 7 - y if vf else y)
                if hf: r = r[::-1]
                for x in range(8):
                    if r[x]:
                        px[tx * 8 + x, ty * 8 + y] = pal[(p * (1 << bpp) + r[x]) if bpp == 4 else (p * 4 + r[x])] + (255,)
    im.save(out)


if __name__ == "__main__":
    pre = sys.argv[2]
    # (tilemap word address, chr word address, bpp) from emu.getState() ppu.layers[n]
    for i, (m, c, b) in enumerate(eval(sys.argv[3]) if len(sys.argv) > 3 else [(0x3000, 0, 4), (0x3800, 0, 4), (0x4000, 0x5000, 2)]):
        render(m, c, b, f"{pre}_bg{i + 1}.png")
