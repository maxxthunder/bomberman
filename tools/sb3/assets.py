"""SB3 graphics assets: the compressed-stream codec ($C0:25B1) and the asset tables at $C1:8000.

Asset loader $C0:193F: A = asset id (1-based), $0D78 = table set. Set pointers are words at $C0:1AA3 (bank $81);
sets 0, 3, 4, 6 and 8 exist. Each entry is 8 bytes: VRAM word address, decompressed length, 24-bit source, type
(low nibble: 2 = BG tiles to VRAM, 3/4 = tilemaps, 5 = sprite tiles stored as 16x16 cells TL, BL, TR, BR).
Codec: a control byte gives count = (c & $1F) + 1 and mode = c >> 5; mode 0 copies literal bytes, 1 = previous + 1,
2 = previous again, 3-7 = the byte 2, 4, 16, 32 or 64 back in a 256-byte ring that starts zeroed.

Usage: python tools/sb3/assets.py list [eu|jp|beta]          table with source ranges
       python tools/sb3/assets.py diff                        assets that differ between EU, JP and the beta
       python tools/sb3/assets.py png ID OUT.png [eu|jp|beta] render one asset in grey (e.g. 3.54)
With no arguments it runs the self-check (every stream ends where the next one starts)."""
import os, struct, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "roms")
NAMES = {"eu": "Super Bomberman 3 (Europe).sfc", "jp": "Super Bomberman 3 (Japan).sfc", "beta": "Super Bomberman 3 (Europe) (Beta).sfc"}
SETS = {0: (0x18000, 31), 8: (0x180F8, 65), 6: (0x18300, 2), 3: (0x18310, 94), 4: (0x18600, 48)}  # file offset, entries
BACK = {3: 2, 4: 4, 5: 16, 6: 32, 7: 64}


def rom(ver="eu"):
    return open(os.path.join(ROOT, NAMES[ver]), "rb").read()


def decomp(r, p, n):
    """Decompress n bytes from file offset p. Returns (data, offset just past the last byte used)."""
    ring, i, out = [0] * 256, 0, bytearray()
    c = r[p]; p += 1; mode, cnt = c >> 5, (c & 0x1F) + 1
    while len(out) < n:
        if mode == 0: v = r[p]; p += 1
        elif mode == 1: v = (ring[(i - 1) & 255] + 1) & 255
        elif mode == 2: v = ring[(i - 1) & 255]
        else: v = ring[(i - BACK[mode]) & 255]
        ring[i] = v; i = (i + 1) & 255; out.append(v); cnt -= 1
        if cnt == 0:
            c = r[p]; p += 1; mode, cnt = c >> 5, (c & 0x1F) + 1
    return bytes(out), p - 1  # the game reads one control byte ahead


def assets(r):
    """{'set.id': (vram, length, file offset, type, data, end)}"""
    out = {}
    for s, (t, n) in SETS.items():
        for k in range(n):
            d, l, a, b, ty = struct.unpack("<HHHBB", r[t + 8 * k:t + 8 * k + 8])
            o = ((b & 0x3F) << 16) | a
            data, end = decomp(r, o, l)
            out["%d.%02d" % (s, k + 1)] = (d, l, o, ty & 15, data, end)
    return out


def render(data, kind, w=16, scale=2):
    """Grey tile sheet; kind 5 = 16x16 sprite cells."""
    from PIL import Image
    n = len(data) // 32
    cells = [(t, (t % w) * 8, (t // w) * 8) for t in range(n)] if kind != 5 else \
        [(c * 4 + q, (c % (w // 2)) * 16 + (q >> 1) * 8, (c // (w // 2)) * 16 + (q & 1) * 8) for c in range(n // 4) for q in range(4)]
    h = max(y for _, _, y in cells) + 8 if cells else 8
    im = Image.new("L", (w * 8, h)); px = im.load()
    for t, ox, oy in cells:
        b = t * 32
        for y in range(8):
            for x in range(8):
                v = sum(((data[b + p * 16 + 2 * y + q] >> (7 - x)) & 1) << (2 * p + q) for p in (0, 1) for q in (0, 1))
                px[ox + x, oy + y] = v * 17
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        for ver in NAMES:
            A = sorted(assets(rom(ver)).values(), key=lambda e: e[2])
            joined = sum(1 for x, y in zip(A, A[1:]) if x[5] == y[2])  # a wrong codec would break the chain
            assert len(A) == 240 and joined >= 230, (ver, joined)
        print("ok: 240 assets per ROM, streams chain end to start")
    elif a[0] == "list":
        for k, (d, l, o, t, data, end) in assets(rom(a[1] if len(a) > 1 else "eu")).items():
            print("%s vram=%04x len=%04x src=$%02X:%04X-%04X type=%d" % (k, d, l, 0xC0 + (o >> 16), o & 0xFFFF, end & 0xFFFF, t))
    elif a[0] == "diff":
        A = {v: assets(rom(v)) for v in NAMES}
        for k, e in A["eu"].items():
            d = [v for v in ("jp", "beta") if A[v][k][4] != e[4]]
            if d: print(k, "differs in", ", ".join(d))
    elif a[0] == "png":
        e = assets(rom(a[3] if len(a) > 3 else "eu"))[a[1]]
        render(e[4], e[3]).save(a[2])
