"""Find instructions that touch a WRAM address (long $7E:xxxx form only; abs and direct-page accesses need a Mesen read watch). Usage: xref.py rom addr..."""
import sys, re
d = open(sys.argv[1], "rb").read()
for a in sys.argv[2:]:
    v = int(a, 16) & 0xFFFF
    lo, hi = v & 255, v >> 8
    for m in re.finditer(re.escape(bytes([lo, hi, 0x7E])), d):
        op = d[m.start() - 1]
        if op in (0xAF, 0x8F, 0xCF, 0x0F, 0x2F, 0x4F, 0x6F, 0xEF, 0xBF, 0x9F, 0xDF, 0x1F, 0x3F, 0x5F, 0x7F, 0xFF):
            print(a, "long %06X op %02X" % (0xC00000 + m.start() - 1, op))
