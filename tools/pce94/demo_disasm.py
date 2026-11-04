"""Disassemble the Bomberman '94 demo CD's boot program with huc6280.py.

Usage: python demo_disasm.py "<Track 2>.bin" <syscard.pce> <outdir>
Extracts the data track (2352-byte raw sectors, 2048 bytes of user data at +16; data starts at file sector 225,
after the 3-second pregap) to <outdir>/data.bin, then builds a memory image for the disassembler: banks $00-$1F =
the System Card, banks $80-$83 = data sectors 2-17 (the IPL record in sector 1 loads them to $4000 with MPR2-6 =
$80-$84). Traces from $4000 and writes <outdir>/bankNN.asm like huc6280.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import huc6280  # noqa: E402

raw = open(sys.argv[1], "rb").read()
data = b"".join(raw[i * 2352 + 16:i * 2352 + 16 + 2048] for i in range(225, len(raw) // 2352))
out = sys.argv[3]
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "data.bin"), "wb").write(data)
ipl = data[2048:2048 + 0x20]
blk, bln, sta = int.from_bytes(ipl[0:3], "big"), ipl[3], ipl[4] | ipl[5] << 8
print("IPL: sectors %d-%d -> $%04X, jump $%04X, MPR2-6 %s" % (blk, blk + bln - 1, sta, ipl[6] | ipl[7] << 8,
                                                              " ".join("$%02X" % (0x80 + b) for b in ipl[8:13])))
img = bytearray(0x88 * 0x2000)
card = open(sys.argv[2], "rb").read()
img[:len(card)] = card
prog = data[blk * 2048:(blk + bln) * 2048]
img[0x80 * 0x2000:0x80 * 0x2000 + len(prog)] = prog
d = huc6280.Dis(bytes(img), inline=False)
d.run(ipl[6] | ipl[7] << 8, [0xFF, 0xF8, 0x80, 0x81, 0x82, 0x83, 0x84, 0x00], "boot")
d.write(out)
for f in os.listdir(out):            # keep only the loaded program's banks
    if f.startswith("bank") and int(f[4:6], 16) < 0x80:
        os.remove(os.path.join(out, f))
print("instructions", sum(1 for v in d.code.values() if v))
