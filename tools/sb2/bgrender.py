"""Render one SNES mode-1 4bpp background layer from a Mesen VRAM/CGRAM dump, colour 0 transparent.
Usage: python tools/sb2/bgrender.py dump.txt layer out.png [x0 y0 x1 y1]
dump.txt holds lines 'ST <ppu.* state>', 'VRAM <hex>', 'CGRAM <hex>' (see logo.lua). The crop box is in
screen pixels after scrolling; without it the whole 256x224 screen is written."""
import sys
from PIL import Image


def load(path):
    d = {}
    for line in open(path):
        k, _, v = line.rstrip("\n").partition(" ")
        if k == "ST":
            d["st"] = dict(x.split("=", 1) for x in v.split())
        elif k in ("VRAM", "CGRAM"):
            d[k] = bytes.fromhex(v)
    return d


def render(d, layer):
    st, vram, cg = d["st"], d["VRAM"], d["CGRAM"]
    g = lambda k: st[f"ppu.layers[{layer}].{k}"]
    chr_ = int(g("chrAddress")) * 2 if int(g("chrAddress")) < 0x8000 else int(g("chrAddress"))
    tm = int(g("tilemapAddress")) * 2 if int(g("tilemapAddress")) < 0x8000 else int(g("tilemapAddress"))
    big, dw, dh = g("largeTiles") == "true", g("doubleWidth") == "true", g("doubleHeight") == "true"
    hs, vs = int(g("hscroll")), int(g("vscroll"))
    ts = 16 if big else 8
    W, H = (64 if dw else 32) * ts, (64 if dh else 32) * ts
    pal = [(((c & 31) << 3), ((c >> 5 & 31) << 3), ((c >> 10 & 31) << 3), 255)
           for c in (cg[i] | cg[i + 1] << 8 for i in range(0, 512, 2))]
    img = Image.new("RGBA", (256, 224), (0, 0, 0, 0))
    px = img.load()
    for sy in range(224):
        for sx in range(256):
            x, y = (sx + hs) % W, (sy + vs + 1) % H  # BG lines are fetched one line down
            tx, ty = x // ts, y // ts
            scr = (tx // 32) + ((ty // 32) * 2 if dw else ty // 32)
            e = tm + scr * 0x800 + ((ty % 32) * 32 + tx % 32) * 2
            e = vram[e % 0x10000] | vram[(e + 1) % 0x10000] << 8
            t, p, hf, vf = e & 0x3FF, e >> 10 & 7, e >> 14 & 1, e >> 15 & 1
            ix, iy = x % ts, y % ts
            if hf: ix = ts - 1 - ix
            if vf: iy = ts - 1 - iy
            t = (t + (ix >> 3) + (iy >> 3) * 16) & 0x3FF
            a = (chr_ + t * 32 + (iy & 7) * 2) % 0x10000
            b = 7 - (ix & 7)
            c = (vram[a] >> b & 1) | (vram[a + 1] >> b & 1) << 1 | (vram[a + 16] >> b & 1) << 2 | (vram[a + 17] >> b & 1) << 3
            if c:
                px[sx, sy] = pal[p * 16 + c]
    return img


if __name__ == "__main__":
    img = render(load(sys.argv[1]), int(sys.argv[2]))
    if len(sys.argv) > 4:
        img = img.crop(tuple(int(v) for v in sys.argv[4:8]))
    img.save(sys.argv[3])
