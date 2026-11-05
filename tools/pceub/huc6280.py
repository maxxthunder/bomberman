"""Small recursive-descent HuC6280 disassembler for PC Engine HuCard images (no header).

Usage: python tools/pceub/huc6280.py <rom.pce> <out.asm> [entries.txt]
       python tools/pceub/huc6280.py <rom.pce> - <bank:addr> <count>     (linear listing to stdout)

Traces from the reset/IRQ vectors at the end of bank 0 (mapped at $E000 on power-up). MPR mapping is tracked
per code path: `LDA #n / TAM #m` (and CLA) sets the pages in m to bank n; a TAM with an unknown A marks
those pages unknown, and code is not followed into an unknown page. JSR assumes the callee keeps the mapping.
JMP (abs,X) tables are followed while their entries land in a mapped ROM page.
entries.txt lines: `bank:addr` (hex, e.g. `03:6A20`) = extra code entry, that bank mapped at addr's page.
Listing lines: `bb:aaaa  bytes  op` with bb = ROM bank (8 KB), aaaa = logical address; unreached bytes are `db`.
"""
import sys

T = """BRK imp|ORA izx|SXY imp|ST0 imm|TSB zp|ORA zp|ASL zp|RMB0 zp|PHP imp|ORA imm|ASL acc|? imp|TSB abs|ORA abs|ASL abs|BBR0 zrel
BPL rel|ORA izy|ORA izp|ST1 imm|TRB zp|ORA zpx|ASL zpx|RMB1 zp|CLC imp|ORA aby|INC acc|? imp|TRB abs|ORA abx|ASL abx|BBR1 zrel
JSR abs|AND izx|SAX imp|ST2 imm|BIT zp|AND zp|ROL zp|RMB2 zp|PLP imp|AND imm|ROL acc|? imp|BIT abs|AND abs|ROL abs|BBR2 zrel
BMI rel|AND izy|AND izp|? imp|BIT zpx|AND zpx|ROL zpx|RMB3 zp|SEC imp|AND aby|DEC acc|? imp|BIT abx|AND abx|ROL abx|BBR3 zrel
RTI imp|EOR izx|SAY imp|TMA imm|BSR rel|EOR zp|LSR zp|RMB4 zp|PHA imp|EOR imm|LSR acc|? imp|JMP abs|EOR abs|LSR abs|BBR4 zrel
BVC rel|EOR izy|EOR izp|TAM imm|CSL imp|EOR zpx|LSR zpx|RMB5 zp|CLI imp|EOR aby|PHY imp|? imp|? imp|EOR abx|LSR abx|BBR5 zrel
RTS imp|ADC izx|CLA imp|? imp|STZ zp|ADC zp|ROR zp|RMB6 zp|PLA imp|ADC imm|ROR acc|? imp|JMP ind|ADC abs|ROR abs|BBR6 zrel
BVS rel|ADC izy|ADC izp|TII blk|STZ zpx|ADC zpx|ROR zpx|RMB7 zp|SEI imp|ADC aby|PLY imp|? imp|JMP iax|ADC abx|ROR abx|BBR7 zrel
BRA rel|STA izx|CLX imp|TST imzp|STY zp|STA zp|STX zp|SMB0 zp|DEY imp|BIT imm|TXA imp|? imp|STY abs|STA abs|STX abs|BBS0 zrel
BCC rel|STA izy|STA izp|TST imab|STY zpx|STA zpx|STX zpy|SMB1 zp|TYA imp|STA aby|TXS imp|? imp|STZ abs|STA abx|STZ abx|BBS1 zrel
LDY imm|LDA izx|LDX imm|TST imzx|LDY zp|LDA zp|LDX zp|SMB2 zp|TAY imp|LDA imm|TAX imp|? imp|LDY abs|LDA abs|LDX abs|BBS2 zrel
BCS rel|LDA izy|LDA izp|TST imax|LDY zpx|LDA zpx|LDX zpy|SMB3 zp|CLV imp|LDA aby|TSX imp|? imp|LDY abx|LDA abx|LDX aby|BBS3 zrel
CPY imm|CMP izx|CLY imp|TDD blk|CPY zp|CMP zp|DEC zp|SMB4 zp|INY imp|CMP imm|DEX imp|? imp|CPY abs|CMP abs|DEC abs|BBS4 zrel
BNE rel|CMP izy|CMP izp|TIN blk|CSH imp|CMP zpx|DEC zpx|SMB5 zp|CLD imp|CMP aby|PHX imp|? imp|? imp|CMP abx|DEC abx|BBS5 zrel
CPX imm|SBC izx|? imp|TIA blk|CPX zp|SBC zp|INC zp|SMB6 zp|INX imp|SBC imm|NOP imp|? imp|CPX abs|SBC abs|INC abs|BBS6 zrel
BEQ rel|SBC izy|SBC izp|TAI blk|SET imp|SBC zpx|INC zpx|SMB7 zp|SED imp|SBC aby|PLX imp|? imp|? imp|SBC abx|INC abx|BBS7 zrel"""
OPS = [tuple(o.split()) for o in T.replace("\n", "|").split("|")]
assert len(OPS) == 256
SIZE = {"imp": 1, "acc": 1, "imm": 2, "zp": 2, "zpx": 2, "zpy": 2, "izx": 2, "izy": 2, "izp": 2, "rel": 2,
        "abs": 3, "abx": 3, "aby": 3, "ind": 3, "iax": 3, "zrel": 3, "imzp": 3, "imzx": 3, "imab": 4, "imax": 4, "blk": 7}
FMT = {"imp": "", "acc": "A", "imm": "#${:02X}", "zp": "${:02X}", "zpx": "${:02X},X", "zpy": "${:02X},Y",
       "izx": "(${:02X},X)", "izy": "(${:02X}),Y", "izp": "(${:02X})", "abs": "${:04X}", "abx": "${:04X},X",
       "aby": "${:04X},Y", "ind": "(${:04X})", "iax": "(${:04X},X)"}
WRITES_A = {"PLA", "TXA", "TYA", "ADC", "SBC", "AND", "ORA", "EOR", "SAX", "SAY", "TMA", "JSR", "BSR"}
STOP = {"RTS", "RTI", "BRA", "?", "BRK"}


def operand(rom, off, pc, mode):
    b = rom[off + 1:off + SIZE[mode]]
    w = lambda i: b[i] | b[i + 1] << 8
    if mode == "rel":
        return "${:04X}".format(pc + 2 + (b[0] ^ 0x80) - 0x80 & 0xFFFF)
    if mode == "zrel":
        return "${:02X},${:04X}".format(b[0], pc + 3 + (b[1] ^ 0x80) - 0x80 & 0xFFFF)
    if mode in ("imzp", "imzx"):
        return "#${:02X},${:02X}{}".format(b[0], b[1], ",X" if mode == "imzx" else "")
    if mode in ("imab", "imax"):
        return "#${:02X},${:04X}{}".format(b[0], w(1), ",X" if mode == "imax" else "")
    if mode == "blk":
        return "${:04X},${:04X},${:04X}".format(w(0), w(2), w(4))
    return FMT[mode].format(*([w(0)] if mode in ("abs", "abx", "aby", "ind", "iax") else list(b)))


class Dis:
    def __init__(self, rom):
        self.rom, self.nb = rom, len(rom) // 0x2000
        self.code = {}   # rom offset -> (logical pc, size, text)
        self.pc_of = {}  # rom bank -> logical page (first seen)

    def off(self, pc, mpr):
        bank = mpr[pc >> 13]
        if bank is None or bank >= 0xF7:
            return None
        bank %= self.nb
        return bank * 0x2000 + (pc & 0x1FFF)

    def trace(self, pc, mpr):
        work = [(pc, tuple(mpr))]
        while work:
            pc, mpr = work.pop()
            a = None  # known A value
            while True:
                o = self.off(pc, mpr)
                if o is None or o in self.code or o >= len(self.rom):
                    break
                name, mode = OPS[self.rom[o]]
                n = SIZE[mode]
                self.code[o] = (pc, n, f"{name} {operand(self.rom, o, pc, mode)}".strip())
                self.pc_of.setdefault(o >> 13, pc >> 13)
                arg = int.from_bytes(self.rom[o + 1:o + n], "little")
                if name == "LDA" and mode == "imm":
                    a = arg
                elif name == "CLA":
                    a = 0
                elif name == "TAM":
                    m = list(mpr)
                    for i in range(8):
                        if arg >> i & 1:
                            m[i] = a
                    mpr = tuple(m)
                elif name in WRITES_A or mode == "acc" or name in ("LDA",):
                    a = None
                if mode == "rel":
                    work.append((pc + 2 + (arg ^ 0x80) - 0x80 & 0xFFFF, mpr))
                elif mode == "zrel":
                    work.append((pc + 3 + ((arg >> 8) ^ 0x80) - 0x80 & 0xFFFF, mpr))
                if name in ("JSR", "JMP") and mode == "abs":
                    work.append((arg, mpr))
                if name == "JMP" and mode == "iax":
                    self.table(arg, mpr, work)
                if name == "JMP" or name in STOP:
                    break
                pc = pc + n & 0xFFFF

    def table(self, t, mpr, work):
        for i in range(0, 128, 2):
            o = self.off(t + i, mpr)
            if o is None or o in self.code:
                return
            dest = self.rom[o] | self.rom[o + 1] << 8
            if self.off(dest, mpr) is None or dest < 0x4000:
                return
            work.append((dest, mpr))

    def listing(self):
        out, o = [], 0
        while o < len(self.rom):
            bank = o >> 13
            if o % 0x2000 == 0:
                out.append(f"\n; ---- ROM bank ${bank:02X} (seen at page {self.pc_of.get(bank, '?')}) ----")
            if o in self.code:
                pc, n, txt = self.code[o]
                out.append(f"{bank:02X}:{pc:04X}  {self.rom[o:o + n].hex(' '):<20} {txt}")
                o += n
            else:
                base = (self.pc_of.get(bank, 0) << 13) | (o & 0x1FFF)
                j = o
                while j < len(self.rom) and j not in self.code and j - o < 16 and (j == o or j % 0x2000):
                    j += 1
                out.append(f"{bank:02X}:{base:04X}  db {self.rom[o:j].hex(' ')}")
                o = j
        return "\n".join(out) + "\n"


BOOT = (0xFF, 0xF8, None, None, None, None, None, 0)  # MPR0 = I/O, MPR1 = RAM, MPR7 = bank 0 at power-up


def run(rom, entries=()):
    d = Dis(rom)
    for v in (0x1FF6, 0x1FF8, 0x1FFA, 0x1FFC, 0x1FFE):
        d.trace(rom[v] | rom[v + 1] << 8, BOOT)
    for bank, pc in entries:
        m = list(BOOT)
        m[pc >> 13] = bank
        d.trace(pc, m)
    return d


def read_entries(path):
    out = []
    for line in open(path):
        f = line.split("#", 1)[0].split()
        if f:
            b, a = f[0].split(":")
            out.append((int(b, 16), int(a, 16)))
    return out


def linear(rom, bank, pc, count):
    o = bank * 0x2000 + (pc & 0x1FFF)
    for _ in range(count):
        name, mode = OPS[rom[o]]
        n = SIZE[mode]
        print(f"{bank:02X}:{pc:04X}  {rom[o:o + n].hex(' '):<20} {name} {operand(rom, o, pc, mode)}")
        o, pc = o + n, pc + n


def cdl_entries(cdl_hex_files, maps, out):
    """Merge Mesen CDL dumps (hex text) into entries.txt: each run of code bytes starts an instruction, mapped at
    the page(s) the bank was seen at (maps: 'bb:p' tokens from lib.lua's maps_dump)."""
    pages = {}
    for t in maps.split():
        b, p = t.split(":")
        pages.setdefault(int(b, 16), []).append(int(p))
    have = set(read_entries(out)) if __import__("os").path.exists(out) else set()
    for path in cdl_hex_files:
        c = bytes.fromhex(open(path).read().strip())
        for i, b in enumerate(c):
            if b & 1 and not (i and c[i - 1] & 1 and i % 0x2000):
                for p in pages.get(i >> 13, []):
                    have.add((i >> 13, p << 13 | i & 0x1FFF))
    open(out, "w").write("".join(f"{b:02X}:{a:04X}\n" for b, a in sorted(have)))
    print(len(have), "entries")


if __name__ == "__main__" and sys.argv[1] == "cdl":  # huc6280.py cdl <entries.txt> "<MAPS line>" cdl.hex...
    cdl_entries(sys.argv[4:], sys.argv[3], sys.argv[2])
elif __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    if sys.argv[2] == "-":
        b, a = sys.argv[3].split(":")
        linear(rom, int(b, 16), int(a, 16), int(sys.argv[4]))
    else:
        d = run(rom, read_entries(sys.argv[3]) if len(sys.argv) > 3 else ())
        open(sys.argv[2], "w").write(d.listing())
        print(f"{len(d.code)} instructions, {sum(n for _, n, _ in d.code.values())} code bytes")

