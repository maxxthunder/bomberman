"""Render SNES BG layers / sprites from a Mesen dump (lines VRAM/CGRAM/OAM/REGS, see logo.lua).
python vram_render.py out.txt outprefix -> outprefix_bg0.png .. bg2.png, _obj.png (256x224 RGBA, colour 0 transparent)"""
import sys, binascii
from PIL import Image
L = {l.split(' ', 1)[0]: l.split(' ', 1)[1].strip() for l in open(sys.argv[1]) if l[:4] in ('VRAM', 'CGRA', 'OAM ', 'REGS')}
vram, cg, oam = (binascii.unhexlify(L[k]) for k in ('VRAM', 'CGRAM', 'OAM'))
R = dict(kv.split('=') for kv in L['REGS'].split())
pal = [((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31) for c in (cg[i] | cg[i + 1] << 8 for i in range(0, 512, 2))]

def tile(base, n, bpp):  # 8x8 tile -> rows of indices; base is a word address
    a = (base * 2 + n * 8 * bpp) & 0xFFFF; out = []
    for y in range(8):
        row = []
        for x in range(8):
            b = 7 - x; v = 0
            for p in range(bpp):
                v |= (vram[(a + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF] >> b & 1) << p
            row.append(v)
        out.append(row)
    return out

def bg(i, bpp):
    chr_, tm = int(R[f'{i}chrAddress']), int(R[f'{i}tilemapAddress'])
    big = R[f'{i}largeTiles'] == 'true'; ts = 16 if big else 8
    dw, dh = R[f'{i}doubleWidth'] == 'true', R[f'{i}doubleHeight'] == 'true'
    W, H = 32 * ts * (2 if dw else 1), 32 * ts * (2 if dh else 1)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
    for ty in range(H // ts):
        for tx in range(W // ts):
            scr = (tx >= 32) + (ty >= 32) * (2 if dw else 1)
            e = (tm + scr * 0x400 + (ty % 32) * 32 + tx % 32) * 2
            w = vram[e & 0xFFFF] | vram[(e + 1) & 0xFFFF] << 8
            n, p, hf, vf = w & 0x3FF, w >> 10 & 7, w >> 14 & 1, w >> 15
            for sy in range(ts // 8):
                for sx in range(ts // 8):
                    t = tile(chr_, (n + sx + sy * 16) & 0x3FF, bpp)
                    for y in range(8):
                        for x in range(8):
                            v = t[y][x]
                            if v:
                                X = (ts - 8 - sx * 8 if hf else sx * 8) + (7 - x if hf else x)
                                Y = (ts - 8 - sy * 8 if vf else sy * 8) + (7 - y if vf else y)
                                px[tx * ts + X, ty * ts + Y] = pal[p * (1 << bpp) + v] + (255,)
    hs, vs = int(R[f'{i}hscroll']), int(R[f'{i}vscroll'])
    out = Image.new('RGBA', (256, 224))
    for y in range(224):
        for x in range(256):
            out.putpixel((x, y), img.getpixel(((x + hs) % W, (y + vs + 1) % H)))
    return out

def obj():
    base, off = int(R['oamBase']), int(R['oamOff']); mode = int(R['oamMode'])
    sizes = [(8, 16), (8, 32), (8, 64), (16, 32), (16, 64), (32, 64), (16, 32), (16, 32)][mode]
    out = Image.new('RGBA', (256, 224), (0, 0, 0, 0)); px = out.load()
    for i in range(127, -1, -1):
        x, y, n, at = oam[i * 4:i * 4 + 4]
        hi = oam[512 + i // 4] >> (i % 4 * 2)
        x |= (hi & 1) << 8; sz = sizes[hi >> 1 & 1]
        if x >= 256: x -= 512
        n |= (at & 1) << 8; p = at >> 1 & 7; hf, vf = at >> 6 & 1, at >> 7
        for sy in range(sz // 8):
            for sx in range(sz // 8):
                tn = (n & 0xF0 | (n + sx) & 0x0F) + sy * 16
                b = base + (off if tn & 0x100 else 0)
                t = tile(b, tn & 0xFF, 4)
                for yy in range(8):
                    for xx in range(8):
                        v = t[yy][xx]
                        if not v: continue
                        X = x + (sz - 8 - sx * 8 if hf else sx * 8) + (7 - xx if hf else xx)
                        Y = y + 1 + (sz - 8 - sy * 8 if vf else sy * 8) + (7 - yy if vf else yy)
                        if 0 <= X < 256 and 0 <= Y % 256 < 224: px[X, Y % 256] = pal[128 + p * 16 + v] + (255,)
    return out

if __name__ == '__main__':
    for i, bpp in ((0, 4), (1, 4), (2, 2)):
        bg(i, bpp).save(f'{sys.argv[2]}_bg{i}.png')
    obj().save(f'{sys.argv[2]}_obj.png')
