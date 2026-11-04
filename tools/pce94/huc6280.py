"""Recursive-descent HuC6280 disassembler for a PC Engine HuCard image (no header).

Usage: python huc6280.py <rom.pce> <outdir> [entries.txt]
Traces from the vectors at the end of bank 0 (always mapped at $E000), following JSR/JMP/branches and tracking
the MPR bank registers: TAM #mask with a constant in A (LDA #n / CLA just before) remaps the pages in the mask.
Code reached through a page whose bank is unknown is not followed (the target is noted as `; ?bank`).
entries.txt lines: `<phys hex> <page 0-7>` (an entry point: ROM offset and the 8 KB page it runs in), e.g. taken
from an emulator trace (trace.lua). Pages 2 and 6 are taken to hold banks $61 and $01 and pages 4/5 an even/odd
pair, as every trace of the game showed.
Writes <outdir>/bankNN.asm (one per 8 KB bank, unreached bytes as db) and <outdir>/labels.txt.
"""
import os
import sys

R = """
BRK imp|ORA izx|SXY imp|ST0 imm|TSB zp|ORA zp|ASL zp|RMB0 zp|PHP imp|ORA imm|ASL imp|- -|TSB abs|ORA abs|ASL abs|BBR0 zpr
BPL rel|ORA izy|ORA izp|ST1 imm|TRB zp|ORA zpx|ASL zpx|RMB1 zp|CLC imp|ORA aby|INC imp|- -|TRB abs|ORA abx|ASL abx|BBR1 zpr
JSR abs|AND izx|SAX imp|ST2 imm|BIT zp|AND zp|ROL zp|RMB2 zp|PLP imp|AND imm|ROL imp|- -|BIT abs|AND abs|ROL abs|BBR2 zpr
BMI rel|AND izy|AND izp|- -|BIT zpx|AND zpx|ROL zpx|RMB3 zp|SEC imp|AND aby|DEC imp|- -|BIT abx|AND abx|ROL abx|BBR3 zpr
RTI imp|EOR izx|SAY imp|TMA imm|BSR rel|EOR zp|LSR zp|RMB4 zp|PHA imp|EOR imm|LSR imp|- -|JMP abs|EOR abs|LSR abs|BBR4 zpr
BVC rel|EOR izy|EOR izp|TAM imm|CSL imp|EOR zpx|LSR zpx|RMB5 zp|CLI imp|EOR aby|PHY imp|- -|- -|EOR abx|LSR abx|BBR5 zpr
RTS imp|ADC izx|CLA imp|- -|STZ zp|ADC zp|ROR zp|RMB6 zp|PLA imp|ADC imm|ROR imp|- -|JMP ind|ADC abs|ROR abs|BBR6 zpr
BVS rel|ADC izy|ADC izp|TII blk|STZ zpx|ADC zpx|ROR zpx|RMB7 zp|SEI imp|ADC aby|PLY imp|- -|JMP iax|ADC abx|ROR abx|BBR7 zpr
BRA rel|STA izx|CLX imp|TST tzp|STY zp|STA zp|STX zp|SMB0 zp|DEY imp|BIT imm|TXA imp|- -|STY abs|STA abs|STX abs|BBS0 zpr
BCC rel|STA izy|STA izp|TST tab|STY zpx|STA zpx|STX zpy|SMB1 zp|TYA imp|STA aby|TXS imp|- -|STZ abs|STA abx|STZ abx|BBS1 zpr
LDY imm|LDA izx|LDX imm|TST tzx|LDY zp|LDA zp|LDX zp|SMB2 zp|TAY imp|LDA imm|TAX imp|- -|LDY abs|LDA abs|LDX abs|BBS2 zpr
BCS rel|LDA izy|LDA izp|TST tax|LDY zpx|LDA zpx|LDX zpy|SMB3 zp|CLV imp|LDA aby|TSX imp|- -|LDY abx|LDA abx|LDX aby|BBS3 zpr
CPY imm|CMP izx|CLY imp|TDD blk|CPY zp|CMP zp|DEC zp|SMB4 zp|INY imp|CMP imm|DEX imp|- -|CPY abs|CMP abs|DEC abs|BBS4 zpr
BNE rel|CMP izy|CMP izp|TIN blk|CSH imp|CMP zpx|DEC zpx|SMB5 zp|CLD imp|CMP aby|PHX imp|- -|- -|CMP abx|DEC abx|BBS5 zpr
CPX imm|SBC izx|- -|TIA blk|CPX zp|SBC zp|INC zp|SMB6 zp|INX imp|SBC imm|NOP imp|- -|CPX abs|SBC abs|INC abs|BBS6 zpr
BEQ rel|SBC izy|SBC izp|TAI blk|SET imp|SBC zpx|INC zpx|SMB7 zp|SED imp|SBC aby|PLX imp|- -|- -|SBC abx|INC abx|BBS7 zpr
"""
OPS = [tuple(o.split()) for o in R.strip().replace("\n", "|").split("|")]
assert len(OPS) == 256
SIZE = {"imp": 1, "imm": 2, "zp": 2, "zpx": 2, "zpy": 2, "izx": 2, "izy": 2, "izp": 2, "rel": 2, "abs": 3, "abx": 3,
        "aby": 3, "ind": 3, "iax": 3, "zpr": 3, "tzp": 3, "tzx": 3, "tab": 4, "tax": 4, "blk": 7, "-": 1}
AW = {"LDA", "ADC", "SBC", "AND", "ORA", "EOR", "PLA", "TXA", "TYA", "SAX", "SAY", "TMA", "JSR", "BSR", "TMA"}
# JSRs followed by inline data (bank 0, always at $E000): $E501 sets the current task's next handler to
# (return address + signed byte), $E528 to the inline word; both return past the data. $E405/$E409 take 3/4
# bytes of inline data (a pointer, a bank for $E409, a mode).
INLINE = {0xE501: 1, 0xE528: 2}
STOP = {"RTS", "RTI", "JMP", "BRA", "BRK", "-"}


def fmt(op, mode, b, pc):
    a8 = b[1] if len(b) > 1 else 0
    a16 = b[1] | b[2] << 8 if len(b) > 2 else 0
    f = {"imp": "", "imm": "#$%02X" % a8, "zp": "$%02X" % a8, "zpx": "$%02X,X" % a8, "zpy": "$%02X,Y" % a8,
         "izx": "($%02X,X)" % a8, "izy": "($%02X),Y" % a8, "izp": "($%02X)" % a8,
         "rel": "$%04X" % ((pc + 2 + (a8 - 256 if a8 > 127 else a8)) & 0xFFFF),
         "abs": "$%04X" % a16, "abx": "$%04X,X" % a16, "aby": "$%04X,Y" % a16, "ind": "($%04X)" % a16,
         "iax": "($%04X,X)" % a16, "-": ""}
    if mode == "zpr":
        r = b[2] - 256 if b[2] > 127 else b[2]
        return "%s $%02X,$%04X" % (op, a8, (pc + 3 + r) & 0xFFFF)
    if mode in ("tzp", "tzx", "tab", "tax"):
        x = b[2] if mode in ("tzp", "tzx") else b[2] | b[3] << 8
        return "%s #$%02X,$%0*X%s" % (op, a8, 2 if mode[1] == "z" else 4, x, ",X" if mode[-1] == "x" else "")
    if mode == "blk":
        w = [b[1] | b[2] << 8, b[3] | b[4] << 8, b[5] | b[6] << 8]
        return "%s $%04X,$%04X,$%04X" % (op, *w)
    if op == "-":
        return "db $%02X" % b[0]
    return (op + " " + f[mode]).strip()


class Dis:
    def __init__(self, rom, inline=True):
        self.rom = rom
        self.inline = inline  # the HuCard's inline-argument JSRs (off for other images)
        self.nb = len(rom) // 0x2000
        self.code = {}      # phys -> (text, size, logical pc)
        self.labels = {}    # phys -> name
        self.notes = {}     # phys -> comment
        self.seen = set()   # (logical pc, mpr tuple)

    def phys(self, pc, mpr):
        b = mpr[pc >> 13]
        if b is None or b >= self.nb:
            return None
        return b * 0x2000 + (pc & 0x1FFF)

    def run(self, pc, mpr, label=None):
        work = [(pc, tuple(mpr))]
        if label:
            p = self.phys(pc, mpr)
            if p is not None:
                self.labels.setdefault(p, label)
        while work:
            pc, mpr = work.pop()
            mpr = list(mpr)
            a = None  # constant in A, if known
            while True:
                key = (pc, tuple(mpr))
                if key in self.seen:
                    break
                self.seen.add(key)
                p = self.phys(pc, mpr)
                if p is None or pc < 0x4000 and mpr[pc >> 13] in (0xF8, 0xFF):
                    break
                op, mode = OPS[self.rom[p]]
                n = SIZE[mode]
                b = self.rom[p:p + n]
                if (p & 0x1FFF) + n > 0x2000 or p in self.code and (self.code[p] is None or self.code[p][1] != n):
                    break
                self.code[p] = (fmt(op, mode, b, pc), n, pc)
                for q in range(p + 1, p + n):
                    self.code.setdefault(q, None)
                nxt = (pc + n) & 0xFFFF
                tgt = None
                if mode == "rel":
                    tgt = (pc + 2 + (b[1] - 256 if b[1] > 127 else b[1])) & 0xFFFF
                elif mode == "zpr":
                    tgt = (pc + 3 + (b[2] - 256 if b[2] > 127 else b[2])) & 0xFFFF
                elif op in ("JSR", "JMP") and mode == "abs":
                    tgt = b[1] | b[2] << 8
                if tgt is not None:
                    tp = self.phys(tgt, mpr)
                    if tp is None:
                        self.notes[p] = "?bank"
                    else:
                        self.labels.setdefault(tp, ("sub_" if op in ("JSR", "BSR") else "L_") + "%05X" % tp)
                        work.append((tgt, tuple(mpr)))
                if self.inline and op == "JSR" and tgt in (0xE405, 0xE409) and mpr[7] == 0:   # inline data: pointer[, bank], mode
                    k = 3 if tgt == 0xE405 else 4
                    self.code[p + 3] = ("db " + ",".join("$%02X" % x for x in self.rom[p + 3:p + 3 + k]), k, nxt)
                    for q in range(p + 4, p + 3 + k):
                        self.code[q] = None
                    nxt = (nxt + k) & 0xFFFF
                elif self.inline and op == "JSR" and tgt in INLINE and mpr[7] == 0:
                    k = INLINE[tgt]
                    if k == 1:
                        t2 = (pc + 2 + (self.rom[p + 3] ^ 0x80) - 0x80) & 0xFFFF
                    else:
                        t2 = self.rom[p + 3] | self.rom[p + 4] << 8
                    self.code[p + 3] = ("dw $%04X" % t2 if k == 2 else "db $%02X  ; -> $%04X" % (self.rom[p + 3], t2), k, nxt)
                    for q in range(p + 4, p + 3 + k):
                        self.code[q] = None
                    tp = self.phys(t2, mpr)
                    if tp is not None:
                        self.labels.setdefault(tp, "task_%05X" % tp)
                        work.append((t2, tuple(mpr)))
                    nxt = (nxt + k) & 0xFFFF
                if op == "TAM":
                    for i in range(8):
                        if b[1] >> i & 1:
                            mpr[i] = a
                # A tracking: only LDA #, CLA keep a known constant
                if op == "LDA" and mode == "imm":
                    a = b[1]
                elif op == "CLA":
                    a = 0
                elif op in AW or op in ("ASL", "LSR", "ROL", "ROR", "INC", "DEC") and mode == "imp":
                    a = None
                if op in STOP or (op == "JMP"):
                    if op == "JMP" and mode in ("ind", "iax"):
                        self.notes[p] = "indirect"
                    break
                pc = nxt

    def write(self, out):
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "labels.txt"), "w") as f:
            for p in sorted(self.labels):
                f.write("%05X %s\n" % (p, self.labels[p]))
        for bank in range(self.nb):
            lines = []
            p, end = bank * 0x2000, (bank + 1) * 0x2000
            while p < end:
                if p in self.labels:
                    lines.append("%s:" % self.labels[p])
                c = self.code.get(p)
                if c:
                    t, n, pc = c
                    hx = " ".join("%02X" % x for x in self.rom[p:p + n])
                    note = "  ; " + self.notes[p] if p in self.notes else ""
                    lines.append("%05X %04X  %-20s %s%s" % (p, pc, hx, t, note))
                    p += n
                else:
                    q = p
                    while q < end and q - p < 16 and q not in self.code and (q == p or q not in self.labels):
                        q += 1
                    if q == p:
                        q += 1
                    lines.append("%05X       db %s" % (p, ",".join("$%02X" % x for x in self.rom[p:q])))
                    p = q
            open(os.path.join(out, "bank%02X.asm" % bank), "w").write("\n".join(lines) + "\n")


def main():
    rom = open(sys.argv[1], "rb").read()
    d = Dis(rom)
    mpr = [0xFF, 0xF8, None, None, None, None, None, 0]
    for name, v in (("reset", 0x1FFE), ("nmi", 0x1FFC), ("timer", 0x1FFA), ("irq1", 0x1FF8), ("irq2", 0x1FF6)):
        d.run(rom[v] | rom[v + 1] << 8, mpr, name)
    ent = sys.argv[3] if len(sys.argv) > 3 else os.path.join(sys.argv[2], "entries.txt")
    if os.path.exists(ent):
        for line in open(ent):
            f = line.split("#", 1)[0].split()
            if not f:
                continue
            ph, page = int(f[0], 16), int(f[1])
            m = list(mpr)
            m[2], m[6] = 0x61, 0x01        # pages 2 and 6 never change in a trace of the game
            m[page] = ph >> 13
            if page in (4, 5):             # pages 4/5 always hold an even/odd bank pair
                m[page ^ 1] = m[page] ^ 1
            for extra in f[2:]:          # optional page=bank pins, e.g. 4=12
                pg, bk = extra.split("=")
                m[int(pg)] = int(bk, 16)
            d.run(page << 13 | ph & 0x1FFF, m)
    d.write(sys.argv[2])
    n = sum(1 for v in d.code.values() if v)
    print("instructions", n, "bytes", len(d.code))


if __name__ == "__main__":
    main()
