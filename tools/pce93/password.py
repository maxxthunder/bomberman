"""Bomberman '93 (PC Engine) password codec, both directions. See docs/pce93.md.

A password is 8 letters, each an index 0-19 into the entry grid (US: BCDFGHJKLMNPQRSTVWXZ, JP: A-T).
Values d0-d5 = world-1 (0-6), stage-1 (0-7), bombs (1-10), fire (1-5), cleared-world mask bits 0-3,
and (mask bits 4-5) << 2 | speed (0-3). Letters 6 and 7 are the checksum S = d0+...+d5: L6 = S & 15, L7 = S >> 4.
Letters 0-5 are d + k, with k taken from the 16-bit key L6 | L7 << 8 rotated right x+1 times (low 3 bits).
US/JP: encoder bank 1 $DC34, decoder $DCAC (US) / bank 6 $99C4, $9A3C (JP). Special Version: same, but
d4 and d5 must be < 15 ($9723 / $979B).
"""
LETTERS = {"us": "BCDFGHJKLMNPQRSTVWXZ", "jp": "ABCDEFGHIJKLMNOPQRST", "sp": "ABCDEFGHIJKLMNOPQRST"}
LIMIT = [(0, 6), (0, 7), (1, 10), (1, 5), (0, 15), (0, 15)]   # inclusive ranges checked by the decoder


def keys(l6, l7):
    v, k = l6 | l7 << 8, []
    for _ in range(6):
        v = (v >> 1) | (v & 1) << 15
        k.append(v & 7)
    return k


def limits(ver):
    return LIMIT[:4] + [(0, 14)] * 2 if ver == "sp" else LIMIT


def decode_vals(p, ver="us"):
    """8 letter indices -> [d0..d5] or None, exactly as the game's decoder."""
    k = keys(p[6], p[7])
    d = []
    for x in range(6):
        if p[x] < k[x]:
            return None
        d.append(p[x] - k[x])
    s = sum(d) & 0xFF
    if p[6] != s & 15 or p[7] != s >> 4:
        return None
    if any(not lo <= v <= hi for v, (lo, hi) in zip(d, limits(ver))):
        return None
    return d


def encode_vals(d):
    s = sum(d) & 0xFF
    l6, l7 = s & 15, s >> 4
    return [v + k for v, k in zip(d, keys(l6, l7))] + [l6, l7]


def to_state(d):
    return {"world": d[0] + 1, "stage": d[1] + 1, "bombs": d[2], "fire": d[3],
            "cleared": d[4] | (d[5] >> 2) << 4, "speed": d[5] & 3}


def from_state(world, stage, bombs=1, fire=1, cleared=0, speed=0):
    return [world - 1, stage - 1, bombs, fire, cleared & 15, (cleared >> 4 & 3) << 2 | speed]


def decode(code, ver="us"):
    a = LETTERS[ver]
    code = code.strip().upper()
    if len(code) != 8 or any(c not in a for c in code):
        return None
    d = decode_vals([a.index(c) for c in code], ver)
    return d and to_state(d)


def encode(ver="us", **state):
    d = from_state(**state)
    if any(not lo <= v <= hi for v, (lo, hi) in zip(d, limits(ver))):
        raise ValueError("state out of range")
    return "".join(LETTERS[ver][i] for i in encode_vals(d))


if __name__ == "__main__":
    import itertools, sys
    n = 0
    for d in itertools.product(*[range(lo, hi + 1) for lo, hi in LIMIT]):
        p = encode_vals(list(d))
        assert max(p) <= 19 and decode_vals(p) == list(d)
        n += 1
    assert n == 716800
    print("ok", n, encode(world=1, stage=1), encode("jp", world=1, stage=1))
    for c in sys.argv[1:]:
        print(c, decode(c), decode(c, "jp"))
