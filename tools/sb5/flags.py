"""Find WRAM bytes that SB5 code tests but never sets (the model: $6253 invincibility).
Reads the disassembly listings (banks $C0-$C7) and, optionally, a Mesen CDL (to tell which writers ever ran).
A "test" is LDA/LDX/LDY/BIT/CMP/CPX/CPY of a fixed address followed within 3 instructions by a branch.
A "write" (a set) is STA/STX/STY/STZ/INC/DEC/ASL/LSR/ROL/ROR/TSB/TRB of the address (16-bit stores cover 2 bytes);
STZ and STA right after LDA #0 are clears and do not count.
Indexed stores (base,X / base,Y) are counted as covering base..base+$7F. Script ops that take a WRAM
address (handlers that reach $C2:1ECF directly or via one JSR, e.g. 5D-7A, 7B INC) are counted as writes wherever their operand appears in the script banks.
Abs addresses $2000-$7FFF are taken as WRAM (the game runs with DB=$7E there); $21xx/$40xx/$42xx/$43xx are I/O.
Usage: flags.py <asm dir> <rom> [cdl] [--direct]   -> address, testers, writers (* = writer never executed per CDL)"""
import os, re, sys

DIRECT = "--direct" in sys.argv  # ignore indexed stores (more candidates, more noise)

LINE = re.compile(r"^\s+(\w{3})\s*(.*?)\s*; \$([0-9A-F]{6})\s+(?:[0-9A-F]{2} ?)+\s+([mM][xX])")
RD = {"LDA", "LDX", "LDY", "BIT", "CMP", "CPX", "CPY"}
WR = {"STA", "STX", "STY", "STZ", "INC", "DEC", "ASL", "LSR", "ROL", "ROR", "TSB", "TRB"}
BR = {"BEQ", "BNE", "BMI", "BPL", "BCC", "BCS", "BVC", "BVS"}
XW = {"LDX", "LDY", "STX", "STY", "CPX", "CPY"}


def wram(arg):
    """-> (address, indexed) for a fixed WRAM operand, else None."""
    m = re.match(r"^\$([0-9A-F]{4}|[0-9A-F]{6})(,[XY])?$", arg)
    if not m:
        return None
    v = int(m.group(1), 16)
    if len(m.group(1)) == 6:
        if v >> 16 not in (0x7E, 0x7F, 0x00, 0x80):
            return None
        if v >> 16 in (0x00, 0x80):
            v &= 0xFFFF
            if v >= 0x2000:
                return None
        else:
            v &= 0x1FFFF if v >> 16 == 0x7F else 0xFFFF
            v |= 0x10000 if m.group(1).startswith("7F") else 0
    elif v >= 0x8000 or (v >> 8) in (0x21, 0x40, 0x41, 0x42, 0x43):
        return None
    return v, bool(m.group(2))


def load(path):
    ins = []
    for name in sorted(os.listdir(path)):
        if re.match(r"bank_C[0-7]\.asm$", name):
            for line in open(os.path.join(path, name)):
                m = LINE.match(line)
                if m:
                    ins.append((int(m.group(3), 16), m.group(1), m.group(2), m.group(4)))
    return ins


def script_writes(rom):
    w16 = lambda a: rom[a] | rom[a + 1] << 8
    def uses_addr(h, depth=2):  # handler JSRs $C2:1ECF, directly or through one JSR
        if rom[h] != 0x20:
            return False
        t = w16(h + 1)
        return t == 0x1ECF or (depth > 1 and uses_addr(0x020000 | t, depth - 1))
    ops = [op for op in range(1, 0xFC) if uses_addr(0x020000 | w16(0x0204FA + 2 * (op - 1)))]
    s = set()
    for i in range(0x060000, 0x080000 - 2):
        if rom[i] in ops:
            s.add(w16(i + 1))
    return s


def analyse(ins, rom, cdl=None):
    tests, writes = {}, {}
    for i, (a, op, arg, mx) in enumerate(ins):
        r = wram(arg)
        if not r:
            continue
        v, idx = r
        wide = (mx[1] == "X") if op in XW else (mx[0] == "M")
        if op in WR:
            if op == "STZ" or (op == "STA" and i and ins[i - 1][1] == "LDA" and ins[i - 1][2] in ("#$00", "#$0000")):
                continue  # clearing is not setting
            span = range(v, v + ((0x80 if not DIRECT else 0) if idx else 2 if wide else 1))
            for b in span:
                writes.setdefault(b, []).append(a)
        elif op in RD and not idx and any(x[1] in BR for x in ins[i + 1:i + 4]):
            for b in range(v, v + (2 if wide else 1)):
                tests.setdefault(b, []).append(a)
    sw = script_writes(rom)
    out = []
    for b in sorted(tests):
        ws = writes.get(b, [])
        if b in sw or (b - 1) in sw:
            continue
        ran = [w for w in ws if cdl is None or cdl[w & 0x3FFFFF] & 1]
        if not ran:
            out.append((b, tests[b], ws))
    return out


if __name__ == "__main__":
    rom = open(sys.argv[2], "rb").read()
    cdl = None
    if len(sys.argv) > 3 and not sys.argv[3].startswith("--"):
        cdl = open(sys.argv[3], "rb").read()
        cdl = cdl[9:] if cdl[:5] == b"CDLv2" else cdl
    for b, t, w in analyse(load(sys.argv[1]), rom, cdl):
        print("$%05X  tested %-40s written %s" % (b, " ".join("%06X" % x for x in t[:5]) + (" +%d" % (len(t) - 5) if len(t) > 5 else ""),
                                            " ".join("%06X*" % x for x in w[:4]) or "never"))
