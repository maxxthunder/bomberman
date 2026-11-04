"""Find a picture's 8x8 tiles in the ROM as raw 4bpp (or 2bpp) data, under any palette (colour i <-> index j one-to-one).
Usage: python findtile.py <rom> <png> [bpp]   -> ROM addresses whose tile matches the picture's top-left 8x8 tile,
and for each, which of the other 8x8 tiles of the picture follow at +1 tile / +16 tiles."""
import sys
import numpy as np
from PIL import Image
r = np.frombuffer(open(sys.argv[1], 'rb').read(), np.uint8); bpp = int(sys.argv[3]) if len(sys.argv) > 3 else 4
im = Image.open(sys.argv[2]).convert('RGB'); W, H = im.size
cols = {}; lab = np.array([[cols.setdefault(im.getpixel((x, y)), len(cols)) for x in range(W)] for y in range(H)])
def decode(o):  # pixel indices (len(o),8,8) of tiles at offsets o
    o = o[:, None]; y = np.arange(8)[None, :]
    pl = [r[o + 2*y], r[o + 2*y + 1]] + ([r[o + 16 + 2*y], r[o + 17 + 2*y]] if bpp == 4 else [])
    px = np.zeros((len(o), 8, 8), np.uint8)
    for k, p in enumerate(pl):
        for x in range(8): px[:, :, x] |= ((p >> (7 - x)) & 1).astype(np.uint8) << k
    return px
def match(px, t):  # bijective colour match against picture tile t (8x8 labels)
    f = t.ravel(); px = px.reshape(len(px), 64); reps = {}
    ok = np.ones(len(px), bool)
    for i, l in enumerate(f):
        if l in reps: ok &= px[:, i] == px[:, reps[l]]
        else: reps[l] = i
    rv = list(reps.values())
    for a in range(len(rv)):
        for b in range(a + 1, len(rv)): ok &= px[:, rv[a]] != px[:, rv[b]]
    return ok
sz = 8 * bpp; N = len(r) - 32 * 17 * sz
t0 = lab[:8, :8]
hits = []
for s in range(0, N, 1 << 18):
    o = np.arange(s, min(s + (1 << 18), N)); hits += list(o[match(decode(o), t0)])
for h in hits:
    rest = []
    for ty in range(H // 8):
        for tx in range(W // 8):
            for step, name in ((tx + ty * (W // 8), 'seq'), (tx + 16 * ty, 'row16')):
                if match(decode(np.array([h + step * sz])), lab[ty*8:ty*8+8, tx*8:tx*8+8])[0]: rest.append(f'{tx},{ty}:{name}')
    print(f'${0xC00000 + h:06X}', ' '.join(rest))
