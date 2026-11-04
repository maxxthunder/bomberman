"""Find raw references to an address in the ROM (long and, with bank $7F/$00 dropped, absolute).
Usage: python tools/sb4/xref.py <rom> <addr hex, e.g. 7F70BD or 00024A> [...]"""
import sys
rom = open(sys.argv[1], 'rb').read()
for a in sys.argv[2:]:
    v = int(a, 16); lo = bytes([v & 255, v >> 8 & 255]); lng = lo + bytes([v >> 16])
    hits = []
    i = rom.find(lng)
    while i >= 0:
        hits.append(f"L {0xC00000 + i - 1:06X} op={rom[i-1]:02X}"); i = rom.find(lng, i + 1)
    for op in (0xAD, 0x8D, 0x9C, 0xEE, 0xCE, 0x2C, 0xCD, 0xBD, 0x9D, 0x0D, 0x2D):  # abs ops
        i = rom.find(bytes([op]) + lo)
        while i >= 0:
            hits.append(f"A {0xC00000 + i:06X} op={op:02X}"); i = rom.find(bytes([op]) + lo, i + 1)
    print(a, len(hits)); [print('  ', h) for h in hits if not h.startswith('L') or rom[int(h.split()[1],16)-0xC00000] in (0xAF,0x8F,0xCF,0x0F,0x2F,0xBF,0x9F,0xDF)]
