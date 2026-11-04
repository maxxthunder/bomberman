"""Super Bomberman 3 (SNES) password codec: a Python copy of the game's own decoder ($C2:67DB) and encoder ($C2:67FD).

Usage: python tools/sb3/password.py               list every valid password
       python tools/sb3/password.py 5358 0803     decode codes
       python tools/sb3/password.py --stage 1-1   encode (all four spellings)
The same code is in all three ROMs (EU, JP, EU beta); only the addresses move by 8 bytes in the beta.
"""
import sys

# $C2:6984: stage id ($0346) -> area ($0349). Ids missing here are rejected.
STAGES = [(0x0B, 1), (0x0C, 1), (0x0D, 1), (0x0F, 1), (0x11, 1), (0x12, 2), (0x13, 2), (0x15, 2), (0x18, 2), (0x1A, 2),
          (0x1B, 3), (0x1D, 3), (0x1F, 3), (0x22, 3), (0x24, 3), (0x25, 4), (0x27, 4), (0x2A, 4), (0x2D, 4), (0x30, 4),
          (0x31, 5), (0x34, 5), (0x37, 5), (0x3A, 5), (0x3E, 5), (0x3F, 6)]
AREA_OF = dict(STAGES)
NAME = {}
for _area in range(1, 6):
    _ids = [s for s, a in STAGES if a == _area]
    for _i, _s in enumerate(_ids):
        NAME[_s] = f"{_area}-{_i + 1}" if _i < 4 else f"{_area}-boss"
NAME[0x3F] = "6-1"

# $C2:6A08: special codes, checked before the normal decode. (digits, effect)
SPECIAL = {
    "4622": "battle mode, arena variant 1 ($542E=1)",
    "1616": "battle mode, arena variant 2 ($542E=2)",
    "3194": "battle mode, arena variant 3 ($542E=3)",
    "1511": "battle mode, COM level 4 ($542F=$6C6F=4)",
    "5656": "battle mode, $4C0C=$7F (unused)",
    "0704": "1-1 with full equipment ($2901=1)",
    "3200": "2-1 with full equipment",
    "2711": "3-1 with full equipment",
    "3870": "4-1 with full equipment",
    "4501": "5-1 with full equipment",
    "0606": "6-1 with full equipment",
    "3104": "6-boss (stage $46) with full equipment",
    "6514": "new game, hard mode: every enemy takes one more hit ($2902=1)",
    "0803": "ending",
}


def swap(v):
    """$C2:68B6: XOR $0DDE, then swap bits 0<->5 and 9<->12. Its own inverse."""
    v ^= 0x0DDE
    for a, b in ((0, 5), (9, 12)):
        if (v >> a & 1) != (v >> b & 1):
            v ^= 1 << a | 1 << b
    return v


def check(lo):
    """$C2:693B: 4-bit checksum of the low byte."""
    return ((lo & 0x7F) >> 4) + lo & 0x0F


def decode(code):
    """4 digits -> ('special', effect) | ('stage', id, name) | None (rejected)."""
    code = str(code)
    if len(code) != 4 or not code.isdigit():
        return None
    if code in SPECIAL:
        return ("special", SPECIAL[code])
    v = (int(code) - 0x0710) & 0xFFFF   # $C2:680A
    v = swap(v)
    if v >= 0x2000 or check(v & 0xFF) != (v >> 9) & 0x0F:  # $C2:691D
        return None
    stage = (v & 0x7F) + 0x0B          # $C2:6949
    if stage not in AREA_OF:
        return None
    return ("stage", stage, NAME[stage])


def encode(stage, spare=0):
    """Stage id -> code. spare (0-3) fills bits 7 and 8, which the decoder ignores; the game itself always writes 0."""
    stage = min(stage, 0x3F)            # $C2:68FA clamps ids >= $40 (the final boss) to $3F
    s = (stage - 0x0B) & 0x7F
    v = s | (spare & 1) << 7 | (spare >> 1 & 1) << 8
    v |= check(v & 0xFF) << 9           # $C2:67FF
    return f"{swap(v) + 0x0710:04d}"    # $C2:6867


def stage_id(name):
    return next(s for s, n in NAME.items() if n == name)


def all_codes():
    return {c: decode(c) for c in (f"{n:04d}" for n in range(10000)) if decode(c)}


def _demo():
    assert decode("5358") == ("stage", 0x0B, "1-1")
    assert encode(0x0B) == "5358"
    assert all(decode(encode(s, k))[1] == s for s, _ in STAGES for k in range(4))
    codes = all_codes()
    assert sum(1 for v in codes.values() if v[0] == "stage") == 104 and len(codes) == 118
    assert decode("1234") is None


if __name__ == "__main__":
    _demo()
    a = sys.argv[1:]
    if a[:1] == ["--stage"]:
        s = stage_id(a[1])
        print(" ".join(encode(s, k) for k in range(4)))
    elif a:
        for c in a:
            print(c, decode(c))
    else:
        for c, v in sorted(all_codes().items(), key=lambda kv: (kv[1][0], kv[1][1] if kv[1][0] == "stage" else 0, kv[0])):
            print(c, *v[1:])
