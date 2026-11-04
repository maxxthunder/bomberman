"""Bomberman '94 (PC Engine) password codec, mirroring the game's encoder ($1AF48) and checker ($1B27C), both in bank
$0D (ROM offsets; the bank runs at $A000-$BFFF). Mega Bomberman (Genesis) uses the same algorithm: tools/mega/password.py.

A password is the 4 digits as shown on screen, left to right. The game reads them as a decimal number with the
LEFTMOST digit as the ones: N = d0 + 10*d1 + 100*d2 + 1000*d3. Bit layout of N (14 bits):

  bit 13      ignored by the checker (the encoder always writes 0) -> "alias" codes N+8192
  bits 10-12  area 0-5 (both $20B2 and $20B3 get it; 5 = the final area)
  bits 6-9    stage bits: stages cleared, or (bit 5 set) the stages cleared BEFORE the last one
  bit 5       "all stages cleared" flag: boss open, low nibble of $20B5 forced to $F
  bits 0-4    check: bits 7-11 of N == bits 0-4 XOR $16

Usage: password.py                 list every valid password
       password.py 0515 7420 ...   decode codes
       password.py --fuzz log.txt  check a fuzz.lua log (all 10,000 codes through the game's checker) against decode()
"""
import sys

STAGES = [3, 4, 4, 4, 4, 0]          # normal stages per area (area 1 has 3; the final area has none)


def _n(code):
    d = [int(c) for c in code]
    return d[0] + 10 * d[1] + 100 * d[2] + 1000 * d[3]


def _code(n):
    return ''.join(str(n // 10 ** i % 10) for i in range(4))


def decode(code):
    """Return the game state for a password, or None if the game rejects it. Mirrors $1B27C-$1B366."""
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
    return {'area': w + 1, 'cleared': cleared, 'last': last[0] if last else None, 'ram_b3': w, 'ram_b5': d,
            'alias': bool(n & 0x2000)}


def encode(area, cleared=(), last=None, alias=False):
    """Password for area 1-6 with the given cleared stages (1-based). If every stage is cleared (boss open), `last`
    names the stage cleared last (the game keeps it out of the high nibble). Mirrors $1AF48."""
    w = area - 1
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
    if st['area'] == 6:
        return 'Final area'
    full = STAGES[st['area'] - 1]
    if len(st['cleared']) == full:
        return 'Area %d boss (last cleared: stage %d)' % (st['area'], st['last'])
    if st['cleared'] == list(range(1, len(st['cleared']) + 1)):
        return 'Area %d stage %d' % (st['area'], len(st['cleared']) + 1)
    return 'Area %d, stages %s cleared' % (st['area'], ','.join(map(str, st['cleared'])) or 'none')


def demo():
    v = valid_codes()
    assert len(v) == 111
    for c in v:                       # every non-alias code round-trips through the encoder
        s = decode(c)
        assert encode(s['area'], s['cleared'], s['last'], s['alias']) == c, c
    assert decode('0515')['area'] == 6 and decode('2200')['cleared'] == [] and decode('7420')['last'] == 3
    assert decode('1234') is None
    return v


def check_fuzz(path):
    """Compare fuzz.lua's "F code ok b2 b3 b5" / "F code bad" lines with decode(); returns (ok, bad, mismatches)."""
    ok = bad = 0
    miss = []
    for line in open(path):
        t = line.split()
        if len(t) < 3 or t[0] != 'F':
            continue
        s = decode(t[1])
        if t[2] == 'ok':
            ok += 1
            if not s or [int(x, 16) for x in t[3:6]] != [s['ram_b3'], s['ram_b3'], s['ram_b5']]:
                miss.append(t[1])
        else:
            bad += 1
            if s:
                miss.append(t[1])
    return ok, bad, miss


if __name__ == '__main__':
    v = demo()
    if sys.argv[1:2] == ['--fuzz']:
        ok, bad, miss = check_fuzz(sys.argv[2])
        print('accepted %d, rejected %d, total %d, disagreeing with decode(): %s' % (ok, bad, ok + bad, miss or 'none'))
        sys.exit(1 if miss or ok + bad != 10000 else 0)
    for c in sys.argv[1:] or v:
        s = decode(c)
        print(c, label(s) + (' [alias]' if s['alias'] else '') if s else 'invalid')
