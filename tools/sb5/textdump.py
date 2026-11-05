"""Every SB5 text-table message (tables 4 and 6, the only two the drawer $C0:0000 has; see textwin.py),
for any of the three ROMs, plus renders through a real VRAM/CGRAM snapshot from Mesen.
The drawer argument is message+1 ($C0:0024 DECs it); this tool numbers messages by pointer index, as textwin.py does.
  textdump.py rom list                      -> table, index, file offset, windows (x,y,w,h,attr)
  textdump.py rom render dump.txt name table idx out.png
      dump.txt holds Mesen lines "PPU name mode=m chr,map,.. x4", "VRAM name <hex>", "CGRAM name <hex>";
      the message is drawn with every BG layer's character base of that snapshot (one row per layer).
  textdump.py rom sheet dump.txt name table first last out.png   -> many messages on one image"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textwin  # noqa: E402


def count(rom, t):
    e = 0x8000 + 3 * t
    b = rom[e] | rom[e + 1] << 8 | rom[e + 2] << 16
    return ((rom[b & 0x3FFFFF] | rom[(b & 0x3FFFFF) + 1] << 8) - (b & 0xFFFF)) // 2


def messages(rom):
    for t in (4, 6):
        for m in range(count(rom, t)):
            off = textwin.msg_offset(rom, t, m)
            yield t, m, off, list(textwin.windows(rom, off))


def load_dump(path, name):
    d = {}
    for line in open(path):
        f = line.split(" ", 2)
        if len(f) == 3 and f[1] == name:
            d[f[0]] = f[2].strip()
    vram = bytes.fromhex(d["VRAM"])
    cg = bytes.fromhex(d["CGRAM"])
    ppu = d["PPU"].split()
    mode = int(ppu[0].split("=")[1])
    chrs = [int(x.split(",")[0]) for x in ppu[1:]]
    return vram, cg, mode, chrs


BPP = {0: (2, 2, 2, 2), 1: (4, 4, 2, 0), 2: (4, 4, 0, 0), 3: (8, 4, 0, 0), 4: (8, 2, 0, 0), 5: (4, 2, 0, 0), 6: (4, 0, 0, 0), 7: (8, 0, 0, 0)}


def tile(vram, base, n, bpp):
    """8x8 list of colour indices for tile n (base = VRAM word address)."""
    a = (base * 2 + n * 8 * bpp) & 0xFFFF
    out = []
    for y in range(8):
        row = []
        for x in range(8):
            c = 0
            for p in range(bpp):
                byte = vram[(a + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF]
                c |= ((byte >> (7 - x)) & 1) << p
            row.append(c)
        out.append(row)
    return out


def draw(rom, table, idx, vram, cg, base, bpp):
    from PIL import Image
    ws = list(textwin.windows(rom, textwin.msg_offset(rom, table, idx)))
    W = max(w for _, _, w, _, _, _, _ in ws)
    H = sum(h for _, _, _, h, _, _, _ in ws)
    im = Image.new("RGB", (W * 8, H * 8))
    px = im.load()
    pal = [((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3) for c in (cg[2 * i] | cg[2 * i + 1] << 8 for i in range(256))]
    oy = 0
    for _, _, w, h, attr, tl, hi in ws:
        for k in range(w * h):
            hb = hi[k] if hi else 0x20
            n = tl[k] | (hb & 3) << 8
            p = (hb >> 2) & 7
            t = tile(vram, base, n, bpp)
            for y in range(8):
                for x in range(8):
                    c = t[7 - y if hb & 0x80 else y][7 - x if hb & 0x40 else x]
                    col = pal[(p * (1 << bpp) + c) & 255] if c and bpp < 8 else pal[c] if c else (0, 0, 0)
                    px[(k % w) * 8 + x, oy + (k // w) * 8 + y] = col
        oy += h * 8
    return im


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    if sys.argv[2] == "list":
        for t, m, off, ws in messages(rom):
            print("%d %02X %06X %s" % (t, m, off, " ".join("%sx%s@%s,%s/%02X" % (w, h, x, y, a) for x, y, w, h, a, _, _ in ws)))
    else:
        from PIL import Image
        vram, cg, mode, chrs = load_dump(sys.argv[3], sys.argv[4])
        t = int(sys.argv[5])
        ids = [int(sys.argv[6], 16)] if sys.argv[2] == "render" else range(int(sys.argv[6], 16), int(sys.argv[7], 16) + 1)
        rows = []
        for i in ids:
            ims = [draw(rom, t, i, vram, cg, chrs[L], BPP[mode][L]) for L in range(4) if BPP[mode][L]]
            rows.append(ims)
        Wt = sum(max(im.width for im in r) + 8 for r in zip(*rows)) if rows else 0
        Ht = sum(max(im.height for im in r) + 8 for r in rows)
        out = Image.new("RGB", (Wt, Ht), (90, 0, 90))
        y = 0
        for r in rows:
            x = 0
            for L, im in enumerate(r):
                out.paste(im, (x, y))
                x += max(im2.width for im2 in [rr[L] for rr in rows]) + 8
            y += max(im.height for im in r) + 8
        out.save(sys.argv[-1])
