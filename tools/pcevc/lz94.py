"""Bomberman '94 graphics decompressors, in Python. The loader script ($EB16) picks one by bit 7 of the source
address high byte:
  unlz (bank 0 $EA40 init / $EA60 next byte): LZSS, bits MSB first: flag 1 = literal (8 bits); flag 0 = ring
    offset (8 bits) + length-2 (4 bits); 256-byte ring filled with $20, write position starting at $EF.
  unmask ($EAB7 init / $EAC2 next byte): 16-byte groups; a mask byte for the 8 even bytes, then one for the 8 odd
    bytes, MSB first: bit 0 = read a new byte, bit 1 = repeat the previous even (odd) byte.
The caller decides how many bytes to take.
  python lz94.py lz|mask <rom> <file offset> <out bytes> <out.bin>   -> also prints the input bytes consumed
Self-check: python lz94.py --test"""
import sys


def unlz(rom, start, n):
    ring = [0x20] * 256
    pos = 0xEF
    src = start
    bits = 0
    cur = 0

    def get(k):
        nonlocal src, bits, cur
        v = 0
        for _ in range(k):
            if bits == 0:
                cur, src, bits = rom[src], src + 1, 8
            v = (v << 1) | (cur >> 7)
            cur = (cur << 1) & 0xFF
            bits -= 1
        return v

    out = bytearray()
    while len(out) < n:
        if get(1):
            b = get(8)
            ring[pos] = b; pos = (pos + 1) & 0xFF; out.append(b)
        else:
            o = get(8); ln = get(4) + 2
            for _ in range(ln):
                b = ring[o]; o = (o + 1) & 0xFF
                ring[pos] = b; pos = (pos + 1) & 0xFF; out.append(b)
    return bytes(out[:n]), src


def unmask(rom, start, n):
    src, out, prev = start, bytearray(), [0, 0]
    while len(out) < n:
        g = [0] * 16
        for par in (0, 1):
            m = rom[src]; src += 1
            for k in range(8):
                if not (m << k) & 0x80:
                    prev[par] = rom[src]; src += 1
                g[2 * k + par] = prev[par]
        out += bytes(g)
    return bytes(out[:n]), src


if __name__ == '__main__':
    if sys.argv[1:] == ['--test']:
        # literal 'A' then a match of 3 at the 'A' just written ($EF): bits 1 01000001 0 11101111 0001
        data = bytes([0b10100000, 0b10111011, 0b11000100])
        assert unlz(data, 0, 4)[0] == b'AAAA', unlz(data, 0, 4)
        # even mask $7F: one new byte then 7 repeats; odd mask $00: 8 new bytes
        data = bytes([0x7F, 9, 0x00, 1, 2, 3, 4, 5, 6, 7, 8])
        assert unmask(data, 0, 16) == (bytes([9, 1, 9, 2, 9, 3, 9, 4, 9, 5, 9, 6, 9, 7, 9, 8]), 11)
        print('ok')
    else:
        f = unlz if sys.argv[1] == 'lz' else unmask
        rom = open(sys.argv[2], 'rb').read()
        out, end = f(rom, int(sys.argv[3], 0), int(sys.argv[4], 0))
        open(sys.argv[5], 'wb').write(out)
        print('consumed %d bytes, input ends at %#x' % (end - int(sys.argv[3], 0), end))
