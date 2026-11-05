"""Genesis Game Genie encode/decode (8 letters, ABCD-EFGH; 24-bit ROM address, 16-bit value).
Usage: gg.py ADDR VALUE  -> code     gg.py CODE -> address, value
Bit layout as in Genesis Plus GX's decoder; the codes made with it were checked in BizHawk (client.addcheat)."""
import sys
CH = "ABCDEFGHJKLMNPRSTVWXYZ0123456789"


def decode(code):
    n = [CH.index(c) for c in code.replace('-', '').upper()]
    a = d = 0
    d |= n[0] << 3
    d |= n[1] >> 2; a |= (n[1] & 3) << 14
    a |= n[2] << 9
    a |= (n[3] & 0xF) << 20 | (n[3] >> 4) << 8
    d |= (n[4] & 1) << 12; a |= (n[4] >> 1) << 16
    d |= (n[5] & 1) << 15 | (n[5] >> 1) << 8
    d |= (n[6] >> 3) << 13; a |= (n[6] & 7) << 5
    a |= n[7]
    return a, d


def encode(a, d):
    n = [0] * 8
    n[0] = (d >> 3) & 31
    n[1] = (d & 7) << 2 | (a >> 14) & 3
    n[2] = (a >> 9) & 31
    n[3] = (a >> 20) & 0xF | ((a >> 8) & 1) << 4
    n[4] = (d >> 12) & 1 | ((a >> 16) & 15) << 1
    n[5] = (d >> 15) & 1 | ((d >> 8) & 15) << 1
    n[6] = ((d >> 13) & 3) << 3 | (a >> 5) & 7
    n[7] = a & 31
    s = ''.join(CH[x] for x in n)
    return s[:4] + '-' + s[4:]


if __name__ == '__main__':
    for a in range(0, 0x1000000, 0x12345):          # self-check: every bit round-trips
        for d in (0, 0xFFFF, 0x4A38, 0x1234):
            assert decode(encode(a, d)) == (a, d)
    if len(sys.argv) == 3: print(encode(int(sys.argv[1], 16), int(sys.argv[2], 16)))
    elif len(sys.argv) == 2: a, d = decode(sys.argv[1]); print('%06X:%04X' % (a, d))
