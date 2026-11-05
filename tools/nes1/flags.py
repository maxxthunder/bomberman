"""RAM that is read but never set, for the NES Bomberman carts (nes1, nes2).

Usage: python tools/nes1/flags.py <rom.nes> <cdlhex> [<cdlhex> ...] [--far C852]

Traces the PRG like deadcode.py (vectors + every executed code start) and collects, for every RAM byte ($0000-$07FF
and cart RAM $6000-$7FFF), the instructions that read it and those that write it. Writes: STA/STX/STY,
INC/DEC/ASL/LSR/ROL/ROR, and an indexed store (abs,X / abs,Y / zp,X / (zp),Y bases are taken to cover 32 bytes up).
Printed:
  never set  - read (by a non-indexed instruction), and no write of any kind: only the power-on RAM clear ever sets it;
  dead set   - read by code that ran, and every direct write is in code that never ran (no indexed write covers it).
'*' marks reads that never executed. Each line also lists store opcodes with that operand found in untraced bytes.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import m6502 as M

rom = M.prg(sys.argv[1])
N = len(rom)
cdl = M.read_cdl(sys.argv[2:], N)
d = M.run(rom, M.cdl_entries(cdl, N // M.BANK), M.FAR)
RD = {"LDA", "LDX", "LDY", "CMP", "CPX", "CPY", "BIT", "AND", "ORA", "EOR", "ADC", "SBC"}
WR = {"STA", "STX", "STY"}
RMW = {"INC", "DEC", "ASL", "LSR", "ROL", "ROR"}
ram = lambda a: a < 0x800 or 0x6000 <= a < 0x8000
reads, wsite, cover = {}, {}, set()
for o, (pc, n, t) in d.code.items():
    op, *rest = t.split(" ", 1)
    a = rest[0] if rest else ""
    m = re.match(r"^\(?\$([0-9A-F]{2,4})\)?(?:,([XY]))?\)?(?:,Y)?$", a)
    if not m or op.startswith("."):
        continue
    addr = int(m.group(1), 16)
    if not ram(addr):
        continue
    idx = m.group(2) or ("Y" if a.endswith(",Y") else None)
    if a.startswith("("):            # (zp),Y / (zp,X): the pointer is read; the target is unknown
        reads.setdefault(addr, []).append((o, pc, t)); reads.setdefault(addr + 1, []).append((o, pc, t))
        continue
    if op in WR or op in RMW:
        (cover.update(range(addr, addr + 32)) if idx else wsite.setdefault(addr, []).append(o))
    if (op in RD or op in RMW) and not idx:
        reads.setdefault(addr, []).append((o, pc, t))


def raw(addr):
    lo, hi = addr & 255, addr >> 8
    pat = [bytes([op, lo, hi]) for op in (0x8D, 0x8E, 0x8C, 0xEE, 0xCE, 0x0E, 0x4E, 0x2E, 0x6E, 0x9D, 0x99, 0xFE, 0xDE)]
    if hi == 0:
        pat += [bytes([op, lo]) for op in (0x85, 0x86, 0x84, 0xE6, 0xC6, 0x06, 0x46, 0x26, 0x66, 0x95, 0x96, 0x94)]
    h = []
    for p in pat:
        i = rom.find(p)
        while i >= 0:
            if i not in d.code and not cdl[i] & 1:
                h.append(i)
            i = rom.find(p, i + 1)
    return ("\tuntraced stores at " + ", ".join("%02X:%04X" % (i // M.BANK, d.base(i // M.BANK) | i % M.BANK) for i in h[:6])) if h else ""


for addr in sorted(reads):
    rs, ws = reads[addr], wsite.get(addr, [])
    where = ", ".join(f"{o // M.BANK:02X}:{pc:04X}{'' if cdl[o] & 1 else '*'} {t}" for o, pc, t in rs[:5])
    if not ws and addr not in cover:
        print(f"${addr:04X}\tnever set\treads {len(rs)}\t{where}{raw(addr)}")
    elif ws and addr not in cover and not any(cdl[o] & 1 for o in ws) and any(cdl[o] & 1 for o, _, _ in rs):
        sets = ", ".join(f"{o // M.BANK:02X}:{d.code[o][0]:04X} {d.code[o][2]}" for o in ws[:6])
        print(f"${addr:04X}\tdead set\treads {len(rs)}\t{where}\tset at {sets}{raw(addr)}")
