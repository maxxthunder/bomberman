"""Render Genesis VDP planes/sprites from raw VRAM/CRAM dumps (from vdpdump.lua). Helpers for logo.py."""
from PIL import Image

def palette(cram):
    out = []
    for i in range(64):
        w = cram[2 * i] << 8 | cram[2 * i + 1]
        out.append(tuple(((w >> s) & 0xE) * 255 // 14 for s in (0, 4, 8)))   # 0000BBB0GGG0RRR0
    return out

def tile(vram, n, hf=False, vf=False):
    b = vram[n * 32:n * 32 + 32]
    px = [[(b[y * 4 + x // 2] >> (4 * (1 - x % 2))) & 15 for x in range(8)] for y in range(8)]
    if hf: px = [r[::-1] for r in px]
    if vf: px = px[::-1]
    return px

def plane(vram, base, w, h):
    """Indexed image (palette index 0-63, 0 = transparent) of a w x h-cell plane at VRAM base, plus a priority mask."""
    im = Image.new('P', (w * 8, h * 8)); pr = Image.new('1', (w * 8, h * 8))
    for cy in range(h):
        for cx in range(w):
            e = vram[base + 2 * (cy * w + cx)] << 8 | vram[base + 2 * (cy * w + cx) + 1]
            t = tile(vram, e & 0x7FF, e & 0x800, e & 0x1000); pal = (e >> 13) & 3
            for y in range(8):
                for x in range(8):
                    if t[y][x]:
                        im.putpixel((cx * 8 + x, cy * 8 + y), pal * 16 + t[y][x])
                        if e & 0x8000: pr.putpixel((cx * 8 + x, cy * 8 + y), 1)
    return im, pr

def sprites(vram, sat, size=(512, 512)):
    """Draw the sprite list at VRAM sat (linked list from entry 0) into an indexed canvas in sprite coordinates."""
    im = Image.new('P', size); i = 0; seen = set()
    order = []
    while i not in seen and len(seen) < 80:
        seen.add(i); e = vram[sat + 8 * i: sat + 8 * i + 8]; order.append(e)
        i = e[3] & 0x7F
        if i == 0: break
    for e in reversed(order):                         # lower list index has priority, draw it last
        y = (e[0] << 8 | e[1]) & 0x3FF; sw = ((e[2] >> 2) & 3) + 1; sh = (e[2] & 3) + 1
        a = e[4] << 8 | e[5]; x = (e[6] << 8 | e[7]) & 0x1FF; pal = (a >> 13) & 3; hf = a & 0x800; vf = a & 0x1000
        for tx in range(sw):
            for ty in range(sh):
                n = (a & 0x7FF) + tx * sh + ty
                t = tile(vram, n, hf, vf)
                ox = (sw - 1 - tx) if hf else tx; oy = (sh - 1 - ty) if vf else ty
                for yy in range(8):
                    for xx in range(8):
                        if t[yy][xx] and x + ox * 8 + xx < size[0] and y + oy * 8 + yy < size[1]:
                            im.putpixel((x + ox * 8 + xx, y + oy * 8 + yy), pal * 16 + t[yy][xx])
    return im
