"""Small recursive-descent HuC6280 disassembler for PC Engine HuCards (unheadered, banks of 8 KB).

Usage: python tools/pce93/huc6280.py <rom.pce> <out.asm> [entries.txt]
Starts at the vectors at the end of bank 0 (mapped at $E000 on reset) and follows code, tracking the MPR
bank registers where they are set by LDA #n / TAM #m (or CLA / TAM). Calls keep the caller's mapping.
JSRs to routines that take inline argument bytes are recognised (see inline_len); a 3-byte task call
(address, bank) is followed with that bank at $8000 and the next at $A000 ($EAE7 in the US game). JMP (abs,X) tables are followed (see table).
Each line is  BB:LLLL  bytes  instruction, BB = ROM bank, LLLL = logical address it was traced at.
entries.txt lines: "logical mpr0 ... mpr7" in hex, e.g. "dcb0 ff f8 -- -- 06 07 01 00" (extra code starts with
the bank mapping there, "--" = unknown; cdl2entries.py makes them from Mesen code/data logs).
Bytes never reached are written as db. Zero page is logical $2000 (work RAM at MPR1 = $F8).
"""
import sys

OPS = """
BRK imp|ORA izx|SXY imp|ST0 imm|TSB zp|ORA zp|ASL zp|RMB0 zp|PHP imp|ORA imm|ASL acc|? imp|TSB abs|ORA abs|ASL abs|BBR0 zpr
BPL rel|ORA izy|ORA izp|ST1 imm|TRB zp|ORA zpx|ASL zpx|RMB1 zp|CLC imp|ORA aby|INC acc|? imp|TRB abs|ORA abx|ASL abx|BBR1 zpr
JSR abs|AND izx|SAX imp|ST2 imm|BIT zp|AND zp|ROL zp|RMB2 zp|PLP imp|AND imm|ROL acc|? imp|BIT abs|AND abs|ROL abs|BBR2 zpr
BMI rel|AND izy|AND izp|? imp|BIT zpx|AND zpx|ROL zpx|RMB3 zp|SEC imp|AND aby|DEC acc|? imp|BIT abx|AND abx|ROL abx|BBR3 zpr
RTI imp|EOR izx|SAY imp|TMA imm|BSR rel|EOR zp|LSR zp|RMB4 zp|PHA imp|EOR imm|LSR acc|? imp|JMP abs|EOR abs|LSR abs|BBR4 zpr
BVC rel|EOR izy|EOR izp|TAM imm|CSL imp|EOR zpx|LSR zpx|RMB5 zp|CLI imp|EOR aby|PHY imp|? imp|? imp|EOR abx|LSR abx|BBR5 zpr
RTS imp|ADC izx|CLA imp|? imp|STZ zp|ADC zp|ROR zp|RMB6 zp|PLA imp|ADC imm|ROR acc|? imp|JMP ind|ADC abs|ROR abs|BBR6 zpr
BVS rel|ADC izy|ADC izp|TII blk|STZ zpx|ADC zpx|ROR zpx|RMB7 zp|SEI imp|ADC aby|PLY imp|? imp|JMP iax|ADC abx|ROR abx|BBR7 zpr
BRA rel|STA izx|CLX imp|TST tzp|STY zp|STA zp|STX zp|SMB0 zp|DEY imp|BIT imm|TXA imp|? imp|STY abs|STA abs|STX abs|BBS0 zpr
BCC rel|STA izy|STA izp|TST tab|STY zpx|STA zpx|STX zpy|SMB1 zp|TYA imp|STA aby|TXS imp|? imp|STZ abs|STA abx|STZ abx|BBS1 zpr
LDY imm|LDA izx|LDX imm|TST tzx|LDY zp|LDA zp|LDX zp|SMB2 zp|TAY imp|LDA imm|TAX imp|? imp|LDY abs|LDA abs|LDX abs|BBS2 zpr
BCS rel|LDA izy|LDA izp|TST tax|LDY zpx|LDA zpx|LDX zpy|SMB3 zp|CLV imp|LDA aby|TSX imp|? imp|LDY abx|LDA abx|LDX aby|BBS3 zpr
CPY imm|CMP izx|CLY imp|TDD blk|CPY zp|CMP zp|DEC zp|SMB4 zp|INY imp|CMP imm|DEX imp|? imp|CPY abs|CMP abs|DEC abs|BBS4 zpr
BNE rel|CMP izy|CMP izp|TIN blk|CSH imp|CMP zpx|DEC zpx|SMB5 zp|CLD imp|CMP aby|PHX imp|? imp|? imp|CMP abx|DEC abx|BBS5 zpr
CPX imm|SBC izx|? imp|TIA blk|CPX zp|SBC zp|INC zp|SMB6 zp|INX imp|SBC imm|NOP imp|? imp|CPX abs|SBC abs|INC abs|BBS6 zpr
BEQ rel|SBC izy|SBC izp|TAI blk|SET imp|SBC zpx|INC zpx|SMB7 zp|SED imp|SBC aby|PLX imp|? imp|? imp|SBC abx|INC abx|BBS7 zpr
"""
OPS = [tuple(o.split()) for o in OPS.replace("\n", "|").strip("|").split("|")]
assert len(OPS) == 256
SIZE = {"imp": 1, "acc": 1, "imm": 2, "zp": 2, "zpx": 2, "zpy": 2, "izx": 2, "izy": 2, "izp": 2, "rel": 2,
        "abs": 3, "abx": 3, "aby": 3, "ind": 3, "iax": 3, "zpr": 3, "tzp": 3, "tzx": 3, "tab": 4, "tax": 4, "blk": 7}
FMT = {"imp": "", "acc": "A", "imm": "#${:02X}", "zp": "${:02X}", "zpx": "${:02X},X", "zpy": "${:02X},Y",
       "izx": "(${:02X},X)", "izy": "(${:02X}),Y", "izp": "(${:02X})", "abs": "${:04X}", "abx": "${:04X},X",
       "aby": "${:04X},Y", "ind": "(${:04X})", "iax": "(${:04X},X)"}
STOP = {"RTS", "RTI", "JMP", "BRA", "BRK", "?"}
KEEP_A = {"TAM", "STA", "PHA", "TAX", "TAY", "CMP", "BIT", "SEI", "CLI", "CLC", "SEC", "CSH", "CSL"}
TASK_FRAME = bytes.fromhex("860385026885066885076885")   # STX $03 / STA $02 / PLA / STA $06 / PLA / STA $07 / PLA / STA


def decode(rom, off, pc):
    """-> (size, text, branch target or None)."""
    op = rom[off]
    m, mode = OPS[op]
    n = SIZE[mode]
    b = rom[off + 1:off + n]
    if len(b) < n - 1:
        return 1, "?", None
    w = lambda i: b[i] | b[i + 1] << 8
    if mode == "rel":
        t = (pc + 2 + (b[0] ^ 0x80) - 0x80) & 0xFFFF
        return n, f"{m} ${t:04X}", t
    if mode == "zpr":
        t = (pc + 3 + (b[1] ^ 0x80) - 0x80) & 0xFFFF
        return n, f"{m} ${b[0]:02X},${t:04X}", t
    if mode in ("tzp", "tzx"):
        return n, f"{m} #${b[0]:02X},${b[1]:02X}" + (",X" if mode == "tzx" else ""), None
    if mode in ("tab", "tax"):
        return n, f"{m} #${b[0]:02X},${w(1):04X}" + (",X" if mode == "tax" else ""), None
    if mode == "blk":
        return n, f"{m} ${w(0):04X},${w(2):04X},${w(4):04X}", None
    if mode in ("abs", "abx", "aby", "ind", "iax"):
        return n, f"{m} {FMT[mode].format(w(0))}".rstrip(), None
    return n, f"{m} {FMT[mode].format(*b)}".rstrip(), None


class Dis:
    def __init__(self, rom):
        self.rom = rom
        self.nb = len(rom) // 0x2000
        self.code = {}      # rom offset -> (logical pc, size, text)
        self.labels = {}    # rom offset -> set of kinds
        self.default = [0xFF, 0xF8, None, None, None, None, 1, 0]  # reset sets MPR6 = MPR7 + 1 ($E04A)

    def off(self, mpr, pc):
        b = mpr[pc >> 13]
        if b is None or b >= self.nb:
            return None
        return b * 0x2000 + (pc & 0x1FFF)

    def word(self, mpr, pc):
        o = self.off(mpr, pc)
        o2 = self.off(mpr, (pc + 1) & 0xFFFF)
        return None if o is None or o2 is None else self.rom[o] | self.rom[o2] << 8

    def run(self, todo):
        while todo:
            pc, mpr = todo.pop()
            mpr = list(mpr)
            a = None  # known accumulator value, for TAM
            while True:
                o = self.off(mpr, pc)
                if o is None or o in self.code:
                    break
                n, text, tgt = decode(self.rom, o, pc)
                if pc & 0x1FFF > 0x2000 - n:   # instruction crosses a bank edge: stop
                    break
                m, mode = OPS[self.rom[o]]
                ops = self.rom[o + 1:o + n]
                if m == "TAM" and a is not None:
                    for i in range(8):
                        if ops[0] >> i & 1:
                            mpr[i] = a
                    text += f"    ; MPR{[i for i in range(8) if ops[0] >> i & 1]} = ${a:02X}"
                self.code[o] = (pc, n, text)
                a = ops[0] if (m == "LDA" and mode == "imm") else 0 if m == "CLA" else a if m in KEEP_A else None
                if tgt is not None:
                    todo.append((tgt, tuple(mpr)))
                    self.mark(mpr, tgt, "L")
                if m in ("JSR", "BSR") or (m == "JMP" and mode == "abs"):
                    t = tgt if m == "BSR" else ops[0] | ops[1] << 8
                    todo.append((t, tuple(mpr)))
                    self.mark(mpr, t, "S" if m != "JMP" else "L")
                    k = self.inline_len(mpr, t) if m == "JSR" else 0
                    if k:   # inline argument bytes after the JSR
                        o2 = o + n
                        arg = self.rom[o2:o2 + k]
                        if o2 in self.code or (pc + n) & 0x1FFF > 0x2000 - k:
                            break
                        self.code[o2] = ((pc + n) & 0xFFFF, k, "db " + ",".join(f"${x:02X}" for x in arg) + "    ; inline")
                        if k == 3 and arg[1] >= 0x40:   # task call: address, bank (mapped at $8000, bank+1 at $A000)
                            ft, m2 = arg[0] | arg[1] << 8, list(mpr)
                            m2[4], m2[5] = arg[2], arg[2] + 1
                            todo.append((ft, tuple(m2)))
                            self.mark(m2, ft, "S")
                        pc = (pc + n + k) & 0xFFFF
                        continue
                if m == "JMP" and mode == "iax":
                    self.table(ops[0] | ops[1] << 8, mpr, todo)
                if m in STOP:
                    break
                pc = (pc + n) & 0xFFFF

    def inline_len(self, mpr, t):
        """Bytes of inline arguments a JSR to t takes: 'LDA #n / JSR <task frame>' (the task library, n bytes;
        also through one 'LDA #n / BRA') or 'PLA / STA zp / CLC / ADC #1' (one byte: the sound call)."""
        o = self.off(mpr, t)
        if o is None:
            return 0
        b = self.rom[o:o + 8]
        if b[:2] == bytes([0x68, 0x85]) and b[3:6] == bytes([0x18, 0x69, 0x01]):
            return 1
        if b[0] == 0xA9 and b[2] == 0x80:       # LDA #n / BRA: look at the BRA target
            o2 = self.off(mpr, (t + 4 + (b[3] ^ 0x80) - 0x80) & 0xFFFF)
            if o2 is not None:
                b = bytes([0xA9, b[1]]) + self.rom[o2:o2 + 3]
        if b[0] == 0xA9 and b[2] == 0x20:
            f = self.off(mpr, b[3] | b[4] << 8)
            if f is not None and self.rom[f:f + 12] == TASK_FRAME:
                return b[1]
        return 0

    def table(self, base, mpr, todo):
        """JMP (abs,X) table: take entries while they point into ROM-mapped slots, at most 64."""
        for i in range(64):
            t = self.word(mpr, base + 2 * i)
            if t is None or (base + 2 * i) & 0x1FFF > 0x1FFE or self.off(mpr, t) is None or t < 0x4000:
                break
            if i and self.off(mpr, base + 2 * i) in self.code:
                break
            todo.append((t, tuple(mpr)))
            self.mark(mpr, t, "T")

    def mark(self, mpr, pc, kind):
        o = self.off(mpr, pc)
        if o is not None:
            self.labels.setdefault(o, set()).add(kind)

    def write(self, path):
        out = []
        o = 0
        while o < len(self.rom):
            if o % 0x2000 == 0:
                out.append(f"\n; ===== bank ${o >> 13:02X} (file ${o:05X}) =====")
            if o in self.code:
                pc, n, text = self.code[o]
                if o in self.labels:
                    out.append(f"L{o >> 13:02X}_{pc:04X}:")
                out.append(f"{o >> 13:02X}:{pc:04X}  {self.rom[o:o + n].hex(' '):<20} {text}")
                o += n
            else:
                e = o + 1
                while e < len(self.rom) and e not in self.code and e % 16 and e % 0x2000:
                    e += 1
                out.append(f"{o >> 13:02X}:{o & 0x1FFF:04X}x {self.rom[o:e].hex(' '):<48} db")
                o = e
        open(path, "w").write("\n".join(out) + "\n")


def main():
    rom = open(sys.argv[1], "rb").read()
    d = Dis(rom)
    vec = [rom[i] | rom[i + 1] << 8 for i in range(0x1FF6, 0x2000, 2)]
    d.run([(v, tuple(d.default)) for v in vec])
    if len(sys.argv) > 3:
        for line in open(sys.argv[3]):
            f = line.split("#", 1)[0].split()
            if not f:
                continue
            pc, mpr = int(f[0], 16), [None if x == "--" else int(x, 16) for x in f[1:9]]
            d.mark(mpr, pc, "E")
            d.run([(pc, tuple(mpr))])
    d.write(sys.argv[2])
    print(f"{sum(n for _, n, _ in d.code.values())} code bytes of {len(rom)}")


if __name__ == "__main__":
    main()
