"""Mega Bomberman (Genesis) password codec, mirroring the game's encoder ($1BA3C) and checker ($1BE32), USA build.

A password is the 4 digits as shown on screen, left to right. The game reads them as a decimal number with the
LEFTMOST digit as the ones: N = d0 + 10*d1 + 100*d2 + 1000*d3. Bit layout of N (14 bits):

  bit 13      ignored by the checker (the encoder always writes 0) -> "alias" codes N+8192
  bits 10-12  world 0-5 ($953B, highest world reached; 5 = final world)
  bits 6-9    stage bits: stages cleared, or (bit 5 set) the stages cleared BEFORE the last one
  bit 5       "all stages cleared" flag: boss open, low nibble of $953D forced to $F
  bits 0-4    check: bits 7-11 of N == bits 0-4 XOR $16

Usage: password.py                 list every valid password
       password.py 0515 7420 ...   decode codes
"""
import sys

STAGES = [3, 4, 4, 4, 4, 0]          # normal stages per world (world 1 has 3; the final world has none)


def _n(code):
    d = [int(c) for c in code]
    return d[0] + 10 * d[1] + 100 * d[2] + 1000 * d[3]


def _code(n):
    return ''.join(str(n // 10 ** i % 10) for i in range(4))


def decode(code):
    """Return the game state for a password, or None if the game rejects it. Mirrors $1BE32-$1BF62."""
    if len(code) != 4 or not code.isdigit():
        return None
    n = _n(code)
    lo, h, flag = n & 0xFF, (n >> 6) & 0xFF, (n >> 5) & 1
    if h & 0x3E != ((lo << 1) ^ 0xAC) & 0x3E:
        return None
    w = (h >> 4) & 7
    if w >= 6 or (w == 5 and h & 0xF) or (w == 0 and h & 8):
        return None
    full = 7 if w == 0 else 0xF
    if flag:
        x = ~h & full
        if x == 0 or x & (x - 1):            # exactly one stage left out of the "before" mask
            return None
        d = (h & 0xF) << 4 | 0xF
    else:
        if h & full == full:
            return None
        d = (h & 0xF) * 0x11
    cleared = [s + 1 for s in range(4) if d & (1 << s) and s < STAGES[w]]
    last = [s + 1 for s in range(4) if flag and not h & (1 << s) and s < STAGES[w]]
    return {'world': w + 1, 'cleared': cleared, 'last': last[0] if last else None, 'ram_953b': w, 'ram_953d': d,
            'alias': bool(n & 0x2000)}


def encode(world, cleared=(), last=None, alias=False):
    """Password for world 1-6 with the given cleared stages (1-based). If every stage is cleared (boss open), `last`
    names the stage cleared last (the game keeps it out of the high nibble). Mirrors $1BA3C."""
    w = world - 1
    m = sum(1 << (s - 1) for s in cleared)
    full = (1 << STAGES[w]) - 1 if w else 7
    if w and w < 5 and m == full or w == 0 and m == 7:
        m &= ~(1 << ((last or STAGES[w]) - 1))
        flag = 0x20
    else:
        flag = 0
    h = w << 4 | m
    n = (h << 6) + ((((h ^ 0xAC) & 0x3E) >> 1) + flag) + (0x2000 if alias else 0)
    return _code(n) if n <= 9999 else None


def valid_codes():
    return [c for c in map(_code, range(10000)) if decode(c)]


def label(st):
    if st['world'] == 6:
        return 'Final world'
    full = STAGES[st['world'] - 1]
    if len(st['cleared']) == full:
        return 'World %d boss (last cleared: stage %d)' % (st['world'], st['last'])
    if st['cleared'] == list(range(1, len(st['cleared']) + 1)):
        return 'World %d stage %d' % (st['world'], len(st['cleared']) + 1)
    return 'World %d, stages %s cleared' % (st['world'], ','.join(map(str, st['cleared'])) or 'none')


def demo():
    v = valid_codes()
    assert len(v) == 111
    for c in v:                       # every non-alias code round-trips through the encoder
        s = decode(c)
        assert encode(s['world'], s['cleared'], s['last'], s['alias']) == c, c
    assert decode('0515')['world'] == 6 and decode('2200')['cleared'] == [] and decode('7420')['last'] == 3
    assert decode('1234') is None
    return v


if __name__ == '__main__':
    v = demo()
    for c in sys.argv[1:] or v:
        s = decode(c)
        print(c, label(s) + (' [alias]' if s['alias'] else '') if s else 'invalid')
