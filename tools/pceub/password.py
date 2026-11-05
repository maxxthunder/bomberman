"""Bomberman: Users Battle (PC Engine, 1990) password codec. The 1990 Bomberman's password system is still in this card,
byte for byte apart from RAM and ROM addresses, but nothing calls its screen (see docs/pceub.md):
decoder $C8AB, encoder $C73D, BOMSOUND check $C656 (bank 2 at $C000); letters $3410-$3417, result $342F.

8 letters. Letter pair k (letters 2k, 2k+1) is byte k, low nibble first; each nibble is the letter's index in that
pair's 16-letter row ($CA88). Byte 0: bits 0-2 shift n, bit 3 = 0, bit 4 = 1, bits 5-7 invert bytes 1-3.
Bytes 1-3 (big-endian 24-bit) shifted right by n hold scattered fields ($CA5C masks, $CA72 byte indices).

    python password.py <CODE>...      decode
    python password.py --test         self-check
    python password.py --count        number of valid codes (exact, from the bit layout)
"""
import sys

ROWS = ["MUROYAGCQXSKIWHB", "WRECKFVBYHOZNAGL", "NEWSLOGIMPHJTVBQ", "NUCLEARHPSTVZYGK"]  # $CA88
# (byte index 1-3, mask), most significant bit first ($CA5C / $CA72)
FIELDS = {
    "round": [(1, 0x08), (3, 0x04), (2, 0x10), (2, 0x04)],   # stored +1, 1-8 -> $2849 0-7
    "stage": [(3, 0x40), (2, 0x40), (1, 0x01), (3, 0x08)],   # stored +1, 1-8 -> $284A 0-7
    "bombs": [(2, 0x80), (1, 0x10), (2, 0x01), (3, 0x20)],   # 1-10 -> $284B
    "fire": [(3, 0x10), (2, 0x08), (3, 0x02), (1, 0x02)],    # 1-15 -> $284C
    "speed": [(1, 0x20)],                                 # 0-1 -> $284D (roller skate)
}
CHECK = [(2, 0x02), (3, 0x01), (1, 0x04), (3, 0x80), (2, 0x20)]  # = number of 1 bits in the five fields
BOMSOUND = "BOMSOUND"  # $C66C: not a password; arms the sound test ($341B = $FF) for the next valid code


def _gather(b, spec):
    v = 0
    for i, m in spec:
        v = v << 1 | (1 if b[i] & m else 0)
    return v


def decode(code):
    """Return {'round','stage','bombs','fire','speed'} (round/stage 1-based; the game stores round-1, stage-1), or None."""
    code = code.upper()
    if len(code) != 8:
        return None
    try:
        v = [ROWS[i // 2].index(c) for i, c in enumerate(code)]
    except ValueError:
        return None
    b = [v[2 * k] | v[2 * k + 1] << 4 for k in range(4)]
    for k in (1, 2, 3):
        if b[0] >> (4 + k) & 1:
            b[k] ^= 0xFF
    if b[0] & 0x18 != 0x10:
        return None
    x = (b[1] << 16 | b[2] << 8 | b[3]) >> (b[0] & 7)
    b = [b[0], x >> 16 & 0xFF, x >> 8 & 0xFF, x & 0xFF]
    f = {k: _gather(b, s) for k, s in FIELDS.items()}
    if not (1 <= f["round"] <= 8 and 1 <= f["stage"] <= 8 and 1 <= f["bombs"] <= 10 and f["fire"] >= 1):
        return None
    ones = sum(bin(_gather(b, s)).count("1") for s in FIELDS.values())
    if _gather(b, CHECK) != ones:
        return None
    return f


def encode(round, stage, bombs=1, fire=1, speed=0, flip=0, shift=0):
    """flip 0-7 (bits = invert bytes 1-3), shift 0-7 (the game picks flip 0-7 and shift 0-2 at random)."""
    b = [0, 0, 0, 0]
    f = {"round": round, "stage": stage, "bombs": bombs, "fire": fire, "speed": speed}
    for k, spec in list(FIELDS.items()) + [("check", CHECK)]:
        val = sum(bin(f[j]).count("1") for j in FIELDS) if k == "check" else f[k]
        for j, (i, m) in enumerate(spec):
            if val >> (len(spec) - 1 - j) & 1:
                b[i] |= m
    x = (b[1] << 16 | b[2] << 8 | b[3]) << shift
    if x >> 24:
        return None  # bits pushed out: shift too large for this state
    b = [flip << 5 | 0x10 | shift, x >> 16 & 0xFF, x >> 8 & 0xFF, x & 0xFF]
    for k in (1, 2, 3):
        if flip >> (k - 1) & 1:
            b[k] ^= 0xFF
    return "".join(ROWS[k][b[k] & 15] + ROWS[k][b[k] >> 4] for k in range(4))


def all_codes(state):
    """Every code for a state (all flips and shifts the decoder accepts)."""
    return sorted({c for fl in range(8) for s in range(8) for c in [encode(**state, flip=fl, shift=s)] if c})


def count_valid():
    """Exact number of accepted 8-letter codes. y = bytes 1-3 after the flip; bits 22-23 of the shifted value are
    unused, and a shift of n needs the top n bits of y zero (they are shifted in as 0) and frees the n bits shifted out."""
    used = 0
    for spec in list(FIELDS.values()) + [CHECK]:
        for i, m in spec:
            used |= m << 8 * (3 - i)
    free = [b for b in range(24) if not used >> b & 1]
    ys = []
    for st in _states():
        c = encode(**st)
        v = [ROWS[i // 2].index(ch) for i, ch in enumerate(c)]
        y = sum((v[2 * k] | v[2 * k + 1] << 4) << 8 * (3 - k) for k in (1, 2, 3))
        for fb in range(1 << len(free)):
            ys.append(y | sum((fb >> j & 1) << b for j, b in enumerate(free)))
    per_shift = [sum(1 for y in ys if y < 1 << 24 - n) << n for n in range(8)]
    return 8 * sum(per_shift), per_shift


def _states():
    for r in range(1, 9):
        for s in range(1, 9):
            for bo in range(1, 11):
                for fi in range(1, 16):
                    for d in (0, 1):
                        yield dict(round=r, stage=s, bombs=bo, fire=fi, speed=d)


def _test():
    import random
    rnd = random.Random(1)
    n = 0
    for r in range(1, 9):
        for s in range(1, 9):
            for bo in range(1, 11):
                for fi in range(1, 16):
                    for d in (0, 1):
                        st = dict(round=r, stage=s, bombs=bo, fire=fi, speed=d)
                        c = encode(**st, flip=rnd.randrange(8), shift=rnd.randrange(3))
                        assert decode(c) == st, (st, c)
                        n += 1
    assert n == 19200
    assert decode(BOMSOUND) is None
    # shift > 2 loses the top bits: count how many states still fit
    print("ok", n, "states")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    if sys.argv[1:] == ["--count"]:
        print(*count_valid())
    for c in sys.argv[1:]:
        if not c.startswith("--"):
            print(c, decode(c))
