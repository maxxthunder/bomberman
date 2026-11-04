"""Merge Mesen CDL dumps into <outdir>/entries.txt (HiROM, banks C0-FF). Each run of code bytes, jump target and subroutine entry starts an instruction.
Usage: python tools/cdl2entries.py <outdir> cdl.hex [...]   (hex text of the CDL, one byte per ROM byte)"""
import binascii, os, sys

OUT = os.path.join(sys.argv[1], "entries.txt")
have = {}
if os.path.exists(OUT):
    for line in open(OUT):
        f = line.split("#", 1)[0].split()
        if f:
            have[int(f[0], 16)] = (f[1], f[2])
for path in sys.argv[2:]:
    c = binascii.unhexlify(open(path).read().strip())
    for i, b in enumerate(c):
        if b & 1 and (b & 0x0C or not (i and c[i - 1] & 1)):  # run start, jump target or sub entry
            have.setdefault(0xC00000 + i,
                            ("1" if b & 0x20 else "0", "1" if b & 0x10 else "0"))
with open(OUT, "w") as f:
    for a in sorted(have):
        f.write(f"{a:06X} {have[a][0]} {have[a][1]}\n")
print(len(have), "entries")
