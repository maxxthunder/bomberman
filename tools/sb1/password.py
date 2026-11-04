"""Super Bomberman (SNES) password codec. Mirrors the game's decoder at $C5:72B0 and encoder at $C5:7FB9.

A password is 4 digits 0-7. Each digit maps through DEC = $C3:0D40 to a 3-bit value t0 t1 t2 t3:
  t1 = world-1, t2 = stage-1, t3 = salt (even, random when the game makes a code), t0 = (t1+t2+t3) & 7.
Valid iff t3 is even, t0 matches, and t1*8+t2 < 48. 48 stages x 4 salts = 192 valid codes.
Usage: python password.py            -> table of all valid codes
       python password.py 7503 5656  -> decode each
"""
import sys

DEC = [1, 3, 4, 6, 2, 0, 5, 7]          # $C3:0D40, digit -> value
ENC = [DEC.index(v) for v in range(8)]  # $C3:0D30 = 5 0 4 1 2 6 3 7, value -> digit
SPECIAL = {"5656": "sets $0C90=1 (small Bomberman in Normal Game), back to title"}  # $C5:7287


def decode(code):
    """Return (world, stage, salt) or None if the game rejects it."""
    if len(code) != 4 or any(c not in "01234567" for c in code):
        return None
    t = [DEC[int(c)] for c in code]
    if t[3] & 1 or (t[1] + t[2] + t[3]) & 7 != t[0] or t[1] * 8 + t[2] >= 48:
        return None
    return t[1] + 1, t[2] + 1, t[3]


def encode(world, stage, salt=0):
    """world 1-6, stage 1-8, salt 0/2/4/6 (the game picks it at random)."""
    assert 1 <= world <= 6 and 1 <= stage <= 8 and salt in (0, 2, 4, 6)
    t1, t2 = world - 1, stage - 1
    return "".join(str(ENC[v]) for v in ((t1 + t2 + salt) & 7, t1, t2, salt))


def all_codes():
    return [c for c in (f"{i:04o}" for i in range(4096)) if decode(c)]


if __name__ == "__main__":
    codes = all_codes()
    assert len(codes) == 192 and all(decode(encode(*decode(c))) == decode(c) for c in codes)
    assert decode("5555") == (1, 1, 0) and decode("5656") is None
    if len(sys.argv) > 1:
        for c in sys.argv[1:]:
            d = decode(c)
            print(c, SPECIAL.get(c) or (f"{d[0]}-{d[1]} (salt {d[2]})" if d else "invalid"))
    else:
        for w in range(1, 7):
            for s in range(1, 9):
                print(f"{w}-{s}", " ".join(encode(w, s, k) for k in (0, 2, 4, 6)))
