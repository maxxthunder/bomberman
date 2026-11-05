"""RAM that is read but never set, for the PC Engine Bomberman cards.

Usage: python tools/pce90/flags.py <rom.pce> "<MAPS line>" <cdl> [<cdl> ...]

Traces the ROM like deadcode.py (vectors + every executed code run) and collects, for every work-RAM byte
($2000-$3FFF, zero page = $20xx), the instructions that read it and those that write it. Writes count as: STA/STX/
STY/STZ, INC/DEC/ASL/LSR/ROL/ROR/TSB/TRB/SMB/RMB, an indexed store whose base is within 32 bytes below, and the
destination range of TII/TIN/TIA/TAI/TDD block moves. Printed:
  never set  - read (by a non-indexed instruction), and no write of any kind: only the power-on RAM clear (a
               block move over all of RAM, excluded here) ever sets it;
  dead set   - read by code that ran, and every direct write is in code that never ran (no indexed or block
               write covers it).
'*' marks reads that never executed in the runs.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import huc6280 as H

rom = open(sys.argv[1], "rb").read()
N = len(rom)
pages = {}
for t in sys.argv[2].split():
    b, p = t.split(":"); pages.setdefault(int(b, 16), []).append(int(p))
cdl = bytearray(N)
for p in sys.argv[3:]:
    raw = open(p, "rb").read()[-N:]
    for i, b in enumerate(raw):
        cdl[i] |= b
for i in range(N - 8):           # fuzz/patch runs leave code bits on $FF fill: drop them
    if rom[i:i + 8] == b"\xff" * 8:
        for k in range(i, i + 8):
            cdl[k] &= 0xFE
ent = []
for i in range(N):
    if cdl[i] & 1 and (cdl[i] & 0x0C or not (i % 0x2000 and cdl[i - 1] & 1)):  # run start, jump target or sub entry
        ent += [(i >> 13, p << 13 | i & 0x1FFF) for p in pages.get(i >> 13, [])]
d = H.run(rom, ent)
RD = {"LDA", "LDX", "LDY", "CMP", "CPX", "CPY", "BIT", "AND", "ORA", "EOR", "ADC", "SBC", "TST"}
WR = {"STA", "STX", "STY", "STZ"}
RMW = {"INC", "DEC", "ASL", "LSR", "ROL", "ROR", "TSB", "TRB"}
reads, wsite, cover = {}, {}, set()      # cover: bytes reached by indexed or block writes
for o, (pc, n, t) in d.code.items():
    op, *rest = t.split(" ", 1)
    a = rest[0] if rest else ""
    if op in ("TII", "TIN", "TIA", "TAI", "TDD"):
        s, dst, ln = (int(x[1:], 16) for x in a.split(","))
        if ln < 0x1000:
            cover.update(range(dst, dst + ln))
        continue
    if op.startswith(("SMB", "RMB", "BBR", "BBS")):
        addr = 0x2000 + int(a[1:3], 16)
        (wsite.setdefault(addr, []).append(o) if op[1] == "M" else reads.setdefault(addr, []).append((o, pc, t)))
        continue
    m = re.match(r"^(#\$[0-9A-F]+,)?\$([0-9A-F]{2,4})(,[XY])?$", a)
    if not m:
        continue
    v = int(m.group(2), 16)
    addr = v + 0x2000 if len(m.group(2)) == 2 else v
    if not 0x2000 <= addr < 0x4000:
        continue
    idx = m.group(3)
    if op in WR or op in RMW:
        if idx:
            cover.update(range(addr, addr + 32))
        else:
            wsite.setdefault(addr, []).append(o)
    if (op in RD or op in RMW) and not idx:
        reads.setdefault(addr, []).append((o, pc, t))
# second check: store opcodes with that operand anywhere in the ROM outside the traced code (code the trace missed)
codebanks = {i >> 13 for i in range(N) if cdl[i] & 1}


def raw_stores(addr):
    hits = []
    lo, hi = addr & 255, addr >> 8
    pat = [bytes([op, lo, hi]) for op in (0x8D, 0x8E, 0x8C, 0x9C, 0xEE, 0xCE, 0x0E, 0x4E, 0x2E, 0x6E, 0x0C, 0x1C, 0x9D, 0x99, 0x9E, 0xFE, 0xDE)]
    if hi == 0x20:
        pat += [bytes([op, lo]) for op in (0x85, 0x86, 0x84, 0x64, 0xE6, 0xC6, 0x06, 0x46, 0x26, 0x66, 0x04, 0x14)]
        pat += [bytes([0x87 + 16 * n, lo]) for n in range(8)]
    for p in pat:
        i = rom.find(p)
        while i >= 0:
            if i not in d.code and i >> 13 in codebanks:
                hits.append(i)
            i = rom.find(p, i + 1)
    return hits


def raw(addr):
    h = raw_stores(addr)
    return ("\tuntraced stores at " + ", ".join("%02X:%04X" % (i >> 13, i & 0x1FFF) for i in h[:6])) if h else ""


for addr in sorted(reads):
    rs = reads[addr]
    ws = wsite.get(addr, [])
    where = ", ".join(f"{o >> 13:02X}:{pc:04X}{'' if cdl[o] & 1 else '*'} {t}" for o, pc, t in rs[:5])
    if not ws and addr not in cover:
        print(f"${addr:04X}\tnever set\treads {len(rs)}\t{where}{raw(addr)}")
    elif ws and addr not in cover and not any(cdl[o] & 1 for o in ws) and any(cdl[o] & 1 for o, _, _ in rs):
        sets = ", ".join(f"{o >> 13:02X}:{d.code[o][0]:04X} {d.code[o][2]}" for o in ws[:6])
        print(f"${addr:04X}\tdead set\treads {len(rs)}\t{where}\tset at {sets}{raw(addr)}")

