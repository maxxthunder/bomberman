"""Render the BG tiles that differ between two VRAM dumps, with the palette their BAT entries use.
python vramdiff.py <dirA>/<name> <dirB>/<name> out.png   (reads <name>_vram.bin, _pal.bin; BAT entries searched in $0000-$0FFF)
Output: each differing tile A over B, 16x scale, side by side; prints the tile numbers and BAT positions."""
import sys
from PIL import Image

def load(base):
    v = open(base + '_vram.bin', 'rb').read(); p = open(base + '_pal.bin', 'rb').read()
    vram = [v[2 * i] | v[2 * i + 1] << 8 for i in range(len(v) // 2)]
    pal = []
    for i in range(512):
        c = p[2 * i] | p[2 * i + 1] << 8
        pal.append(((c >> 3 & 7) * 255 // 7, (c >> 6 & 7) * 255 // 7, (c & 7) * 255 // 7))
    return vram, pal

def tile(vram, pal, t, pn):
    im = Image.new('RGB', (8, 8)); px = im.load()
    for y in range(8):
        w0, w1 = vram[t * 16 + y], vram[t * 16 + 8 + y]
        for x in range(8):
            b = 7 - x
            c = (w0 >> b & 1) | (w0 >> (8 + b) & 1) << 1 | (w1 >> b & 1) << 2 | (w1 >> (8 + b) & 1) << 3
            px[x, y] = pal[pn * 16 + c] if c else pal[0]
    return im

A, B = load(sys.argv[1]), load(sys.argv[2])
diff = sorted({i // 16 for i in range(0x8000) if A[0][i] != B[0][i]})
use = {}
for i in range(0x1000):
    e = A[0][i]
    if (e & 0xFFF) in diff: use.setdefault(e & 0xFFF, []).append((hex(i), e >> 12))
print('differing tiles:', [hex(t) for t in diff]); print('BAT use (VRAM word, palette):', use)
S = 16
out = Image.new('RGB', (len(diff) * (8 * S + 8), 16 * S + 8), 'white')
for k, t in enumerate(diff):
    pn = use.get(t, [(0, 0)])[0][1]
    for r, (vr, pl) in enumerate((A, B)):
        out.paste(tile(vr, pl, t, pn).resize((8 * S, 8 * S), Image.NEAREST), (k * (8 * S + 8), r * (8 * S + 8)))
out.save(sys.argv[3])
