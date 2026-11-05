"""NES Game Genie codes: python tools/nes1/gg.py ADDR VAL [CMP]   (hex; ADDR $8000-$FFFF) -> 6 or 8 letters
                        python tools/nes1/gg.py CODE                -> address, value, compare
"""
import sys

L = "APZLGITYEOXUKSVN"


def encode(a, v, c=None):
    n = [(v & 7) | (v >> 4 & 8), (v >> 4 & 7) | (a >> 4 & 8), (a >> 4 & 7) | (8 if c is not None else 0),
         (a >> 12 & 7) | (a & 8), (a & 7) | (a >> 8 & 8), (a >> 8 & 7) | ((c if c is not None else v) & 8)]
    if c is not None:
        n += [(c & 7) | (c >> 4 & 8), (c >> 4 & 7) | (v & 8)]
    return "".join(L[x] for x in n)


def decode(code):
    n = [L.index(ch) for ch in code.upper()]
    a = 0x8000 | (n[3] & 7) << 12 | (n[5] & 7) << 8 | (n[4] & 8) << 8 | (n[2] & 7) << 4 | (n[1] & 8) << 4 | (n[4] & 7) | (n[3] & 8)
    if len(n) == 6:
        return a, (n[1] & 7) << 4 | (n[0] & 8) << 4 | (n[0] & 7) | (n[5] & 8), None
    return a, (n[1] & 7) << 4 | (n[0] & 8) << 4 | (n[0] & 7) | (n[7] & 8), (n[7] & 7) << 4 | (n[6] & 8) << 4 | (n[6] & 7) | (n[5] & 8)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(*("$%X" % x if x is not None else "-" for x in decode(sys.argv[1])))
    else:
        print(encode(*(int(x, 16) for x in sys.argv[1:])))
    for a, v, c in [(0xC6E9, 0xA9, None), (0x9562, 0x60, 0x20), (0xFFFF, 0x12, 0x34)]:
        assert decode(encode(a, v, c)) == (a, v, c)
