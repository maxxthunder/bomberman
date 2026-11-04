"""Linear 65816 listing from one address, for code the recursive disassembler mis-decodes.
Usage: python tools/lin65.py <rom> <snes_addr hex> <count> [m x]   (m/x: 1 = 8-bit; default 0 0)
Tracks REP/SEP only; does not follow branches."""
import sys

import disasm

rom = open(sys.argv[1], "rb").read()
disasm.set_map(rom)
addr, count = int(sys.argv[2], 16), int(sys.argv[3])
m, x = (sys.argv[4] == "1", sys.argv[5] == "1") if len(sys.argv) > 5 else (False, False)
for _ in range(count):
    off = disasm.to_off(addr)
    name, mode = disasm.OPS[rom[off]]
    n = disasm.size_of(mode, m, x)
    ops = disasm.operand(rom, off, addr, name, mode, n, m, x, set())
    print(f"${addr:06X}  {rom[off:off + n].hex(' '):<12} {'m' if m else 'M'}{'x' if x else 'X'}  {name} {ops}")
    m, x, _ = disasm.widths(name, int.from_bytes(rom[off + 1:off + n], "little"), m, x, ())
    addr += n
