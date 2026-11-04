"""Mesen code/data logs -> huc6280.py entries: python tools/pce93/cdl2entries.py rom out.txt a.cdl [b.cdl ...]

A CDL marks ROM bytes run as code (bit 0) and jump/call targets (bits 2-3) but not the logical address. Each
bank's slot is voted from the JSR/JMP abs operands inside its own logged code that land on its own code;
the neighbour bank is assumed mapped in the next slot (the game maps code banks in pairs, $F08A/$F093).
Fixed slots: MPR0 $FF, MPR1 $F8, MPR6 bank 1, MPR7 bank 0. One entry per start of a run of code bytes and
per logged target.
"""
import sys, collections

rom = open(sys.argv[1], "rb").read()
cdl = bytearray(len(rom))
for f in sys.argv[3:]:
    for i, b in enumerate(open(f, "rb").read()):
        cdl[i] |= b
nb = len(rom) // 0x2000
slot = {0: 7, 1: 6}
for b in range(2, nb):
    c = collections.Counter()
    base = b * 0x2000
    for i in range(base, base + 0x1FFD):
        if cdl[i] & 1 and rom[i] in (0x20, 0x4C) and cdl[i + 1] & 1 and cdl[i + 2] & 1:
            t = rom[i + 1] | rom[i + 2] << 8
            if 0x4000 <= t < 0xC000 and cdl[base + (t & 0x1FFF)] & 1:
                c[t >> 13] += 1
    if c:
        slot[b] = c.most_common(1)[0][0]
for b in range(2, nb):   # a pair partner with a known slot gives the other one
    p = b ^ 1
    if b not in slot and slot.get(p) in (2, 3, 4, 5) and (slot[p] ^ 1) == slot[p] + (b - p):
        slot[b] = slot[p] + (b - p)
out = []
for o in range(len(rom)):
    if not cdl[o] & 1 or (o and cdl[o - 1] & 1 and not cdl[o] & 0x0C):
        continue
    b = o >> 13
    if b not in slot:
        continue
    s = slot[b]
    mpr = [0xFF, 0xF8, None, None, None, None, 1, 0]
    mpr[s] = b
    for nbk, ns in ((b - 1, s - 1), (b + 1, s + 1)):
        if 2 <= ns <= 5 and slot.get(nbk) == ns:
            mpr[ns] = nbk
    out.append(f"{s << 13 | o & 0x1FFF:04x} " + " ".join("--" if m is None else f"{m:02x}" for m in mpr))
open(sys.argv[2], "w").write("\n".join(out) + "\n")
print(len(out), "entries;", "slots", " ".join(f"{b:02x}:{s}" for b, s in sorted(slot.items())))
