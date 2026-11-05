"""List the JSL/JML sites that differ between an English ROM and its Japanese original and point into
the added code: banks $E0+ or a free-space block in bank $C0 (default from $C0:FC00).
Usage: python tools/sb4en/hooks.py <english.sfc> <japan.sfc> [lowest $C0 target, hex]   (works for SB4 and SB5)"""
import sys

e = open(sys.argv[1], 'rb').read()
j = open(sys.argv[2], 'rb').read()
lo = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xC0FC00
for i in range(len(j) - 3):
    if e[i] in (0x22, 0x5C) and e[i:i + 4] != j[i:i + 4]:
        t = int.from_bytes(e[i + 1:i + 4], 'little')
        if t >= 0xE00000 or lo <= t < 0xC10000:
            print("%06X %s $%06X  (JP: %s)" % (0xC00000 + i, 'JSL' if e[i] == 0x22 else 'JML', t, j[i:i + 4].hex()))
