"""Unused-graphics sweep: ROM bytes in the graphics banks that no coverage run read (Mesen code/data log),
rendered as 4bpp tiles so they can be looked at.
Usage: python tools/sb2/unused_gfx.py rom out_dir cdl [cdl ...]
Each cdl is a Mesen .cdl file or a text file with a 'CDL <hex>' line (tools/sb2/coverage.lua). A byte counts as
used if any log flags it. Unread 32-byte tiles in BANKS are grouped into runs (gaps of up to GAP tiles are
bridged); runs of MIN tiles or more that are not blank are drawn 16 tiles wide, 2x, in a grey ramp (or with
--pal FILE: 32 bytes of CGRAM, e.g. from a palette the game uses), one PNG per run, named by HiROM address,
plus index.txt. The page shows where to look; whether a run is truly unused is decided by hand (docs/sb2.md)."""
import os, sys
from PIL import Image

BANKS = range(0x02, 0x10)  # $C2-$CF; $C0/$C1/$CC are mostly code but are cheap to include
MIN, GAP = 4, 1


def load_cdl(path, size):
    raw = open(path, "rb").read()
    if raw[:5] == b"CDLv2":
        return raw[9:9 + size]
    for line in raw.decode("latin-1").splitlines():
        if line.startswith("CDL "):
            return bytes.fromhex(line[4:].strip())[:size]
    raise SystemExit(f"{path}: no CDL data")


def tile4(b):
    px = []
    for y in range(8):
        p0, p1, p2, p3 = b[2 * y], b[2 * y + 1], b[16 + 2 * y], b[17 + 2 * y]
        px.append([(p0 >> (7 - x) & 1) | (p1 >> (7 - x) & 1) << 1 | (p2 >> (7 - x) & 1) << 2 | (p3 >> (7 - x) & 1) << 3
                   for x in range(8)])
    return px


def runs(rom, used):
    out, cur, gap = [], None, 0
    for bank in BANKS:
        for off in range(bank << 16, (bank + 1) << 16, 32):
            t = rom[off:off + 32]
            free = not any(used[off:off + 32]) and len(set(t)) > 2
            if free:
                if cur is None:
                    cur = [off, off + 32]
                else:
                    cur[1] = off + 32
                gap = 0
            elif cur is not None:
                gap += 1
                if gap > GAP or (off + 32) >> 16 != cur[0] >> 16:
                    out.append(cur)
                    cur, gap = None, 0
        if cur is not None:
            out.append(cur)
            cur, gap = None, 0
    return [r for r in out if (r[1] - r[0]) // 32 >= MIN]


def render(rom, a, b, pal):
    n = (b - a) // 32
    w, h = 16, (n + 15) // 16
    img = Image.new("RGB", (w * 8, h * 8), (255, 0, 255))
    px = img.load()
    for i in range(n):
        t = tile4(rom[a + 32 * i:a + 32 * i + 32])
        for y in range(8):
            for x in range(8):
                px[(i % 16) * 8 + x, (i // 16) * 8 + y] = pal[t[y][x]]
    return img.resize((img.width * 2, img.height * 2), Image.NEAREST)


def palette(path):
    if not path:
        return [(c * 17,) * 3 for c in range(16)]
    cg = open(path, "rb").read()[:32]
    return [((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3) for c in (cg[i] | cg[i + 1] << 8 for i in range(0, 32, 2))]


if __name__ == "__main__":
    args = sys.argv[1:]
    pal = None
    if "--pal" in args:
        i = args.index("--pal"); pal = args[i + 1]; del args[i:i + 2]
    rom = open(args[0], "rb").read()
    used = bytearray(len(rom))
    for p in args[2:]:
        for i, v in enumerate(load_cdl(p, len(rom))):
            used[i] |= v
    os.makedirs(args[1], exist_ok=True)
    P = palette(pal)
    idx = []
    for a, b in runs(rom, used):
        name = f"{0xC00000 + a:06X}-{0xC00000 + b - 1:06X}"
        render(rom, a, b, P).save(os.path.join(args[1], name + ".png"))
        idx.append(f"{name} file ${a:05X} {(b - a) // 32} tiles")
    open(os.path.join(args[1], "index.txt"), "w").write("\n".join(idx) + "\n")
    print(len(idx), "runs,", sum(int(s.split()[3]) for s in idx), "tiles")
