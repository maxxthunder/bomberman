"""Dump ASCII-like text in a ROM and say whether the code/data logs ever saw it read (SB3 and SB4).
Usage: python tools/sb3/strings.py <rom> [merged cdl.bin] [min length, default 8]
A string is a run of printable bytes ($20-$7E) with at least min letters; '#'/'&'/'$' (SB4's debug text
format) count as printable. 'read' = some byte of it was read as data in the logs, '-' = never read."""
import re, sys


def strings(rom, n=8):
    for m in re.finditer(rb'[\x20-\x7e]{%d,}' % n, rom):
        s = m.group()
        if sum(c.isalpha() for c in s.decode()) >= n * 3 // 4 and len(set(s)) > 4:
            yield m.start(), s.decode()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        assert list(strings(b'\0\0HELLO WORLD!\0abc\0')) == [(2, 'HELLO WORLD!')]; print('self-check ok'); sys.exit()
    rom = open(sys.argv[1], 'rb').read()
    cdl = open(sys.argv[2], 'rb').read() if len(sys.argv) > 2 else None
    for o, s in strings(rom, int(sys.argv[3]) if len(sys.argv) > 3 else 8):
        r = '' if cdl is None else ('read' if any(cdl[o + i] & 2 for i in range(len(s))) else '-')
        print(f'${0xC00000 + o:06X} {r:4s} {s}')
