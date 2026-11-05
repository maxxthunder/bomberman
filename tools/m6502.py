"""Small recursive-descent 6502 disassembler for NES iNES images (NROM and MMC1-style 16 KB PRG banking).

Usage: python tools/m6502.py <rom.nes> <out.asm> [entries.txt]
       python tools/m6502.py <rom.nes> - <bank:addr> <count>     (linear listing to stdout)
       python tools/m6502.py cdl <rom.nes> <entries.txt> <cdl> [...] (merge Mesen CDL code starts into entries.txt)

PRG is split into 16 KB banks; the last one is fixed at $C000, the others are seen at $8000 (a 16 KB NROM image is
bank 0 at both). Traces from the NMI/RESET/IRQ vectors. A JSR/JMP/branch into $8000-$BFFF from the fixed bank goes
to an unknown bank and is not followed (add it with entries.txt or a CDL); from a switchable bank it stays in that bank.
JMP (ind) is not followed. --far ADDR (hex, repeatable) names a far-call routine used as `JSR ADDR / .db bank / .dw target-1`
(Bomberman II: $C852): the 3 inline bytes are listed as `.far bb:target` and the target is traced in that bank.
entries.txt lines: `bank:addr` (hex, e.g. `03:8A20`).
Listing lines: `bb:aaaa  bytes  op`, bb = 16 KB PRG bank; unreached bytes are `db`.
Undocumented opcodes decode as `?` and stop the trace.
CDL: Mesen .cdl (CDLv2 header, then 1 byte per PRG byte; bit 0 code, bit 1 data) or a CDLHEX text dump.
"""
import os, sys

T = """BRK imp|ORA izx|? imp|? imp|? imp|ORA zp|ASL zp|? imp|PHP imp|ORA imm|ASL acc|? imp|? imp|ORA abs|ASL abs|? imp
BPL rel|ORA izy|? imp|? imp|? imp|ORA zpx|ASL zpx|? imp|CLC imp|ORA aby|? imp|? imp|? imp|ORA abx|ASL abx|? imp
JSR abs|AND izx|? imp|? imp|BIT zp|AND zp|ROL zp|? imp|PLP imp|AND imm|ROL acc|? imp|BIT abs|AND abs|ROL abs|? imp
BMI rel|AND izy|? imp|? imp|? imp|AND zpx|ROL zpx|? imp|SEC imp|AND aby|? imp|? imp|? imp|AND abx|ROL abx|? imp
RTI imp|EOR izx|? imp|? imp|? imp|EOR zp|LSR zp|? imp|PHA imp|EOR imm|LSR acc|? imp|JMP abs|EOR abs|LSR abs|? imp
BVC rel|EOR izy|? imp|? imp|? imp|EOR zpx|LSR zpx|? imp|CLI imp|EOR aby|? imp|? imp|? imp|EOR abx|LSR abx|? imp
RTS imp|ADC izx|? imp|? imp|? imp|ADC zp|ROR zp|? imp|PLA imp|ADC imm|ROR acc|? imp|JMP ind|ADC abs|ROR abs|? imp
BVS rel|ADC izy|? imp|? imp|? imp|ADC zpx|ROR zpx|? imp|SEI imp|ADC aby|? imp|? imp|? imp|ADC abx|ROR abx|? imp
? imp|STA izx|? imp|? imp|STY zp|STA zp|STX zp|? imp|DEY imp|? imp|TXA imp|? imp|STY abs|STA abs|STX abs|? imp
BCC rel|STA izy|? imp|? imp|STY zpx|STA zpx|STX zpy|? imp|TYA imp|STA aby|TXS imp|? imp|? imp|STA abx|? imp|? imp
LDY imm|LDA izx|LDX imm|? imp|LDY zp|LDA zp|LDX zp|? imp|TAY imp|LDA imm|TAX imp|? imp|LDY abs|LDA abs|LDX abs|? imp
BCS rel|LDA izy|? imp|? imp|LDY zpx|LDA zpx|LDX zpy|? imp|CLV imp|LDA aby|TSX imp|? imp|LDY abx|LDA abx|LDX aby|? imp
CPY imm|CMP izx|? imp|? imp|CPY zp|CMP zp|DEC zp|? imp|INY imp|CMP imm|DEX imp|? imp|CPY abs|CMP abs|DEC abs|? imp
BNE rel|CMP izy|? imp|? imp|? imp|CMP zpx|DEC zpx|? imp|CLD imp|CMP aby|? imp|? imp|? imp|CMP abx|DEC abx|? imp
CPX imm|SBC izx|? imp|? imp|CPX zp|SBC zp|INC zp|? imp|INX imp|SBC imm|NOP imp|? imp|CPX abs|SBC abs|INC abs|? imp
BEQ rel|SBC izy|? imp|? imp|? imp|SBC zpx|INC zpx|? imp|SED imp|SBC aby|? imp|? imp|? imp|SBC abx|INC abx|? imp"""
OPS = [tuple(o.split()) for o in T.replace("\n", "|").split("|")]
assert len(OPS) == 256
SIZE = {"imp": 1, "acc": 1, "imm": 2, "zp": 2, "zpx": 2, "zpy": 2, "izx": 2, "izy": 2, "rel": 2,
        "abs": 3, "abx": 3, "aby": 3, "ind": 3}
FMT = {"imp": "", "acc": "A", "imm": "#${:02X}", "zp": "${:02X}", "zpx": "${:02X},X", "zpy": "${:02X},Y",
       "izx": "(${:02X},X)", "izy": "(${:02X}),Y", "abs": "${:04X}", "abx": "${:04X},X", "aby": "${:04X},Y",
       "ind": "(${:04X})"}
STOP = {"RTS", "RTI", "?", "BRK", "JMP"}
BANK = 0x4000


def prg(path):
    """PRG bytes of an iNES file (16-byte header, no trainer handling needed for these carts)."""
    d = open(path, "rb").read()
    return d[16:16 + d[4] * BANK]


def operand(rom, off, pc, mode):
    b = rom[off + 1:off + SIZE[mode]]
    if mode == "rel":
        return "${:04X}".format(pc + 2 + (b[0] ^ 0x80) - 0x80 & 0xFFFF)
    return FMT[mode].format(*([b[0] | b[1] << 8] if SIZE[mode] == 3 else list(b)))


class Dis:
    def __init__(self, rom, far=()):
        self.rom, self.nb, self.far = rom, len(rom) // BANK, set(far)
        self.code = {}  # rom offset -> (pc, size, text)

    def base(self, bank):
        return 0xC000 if bank == self.nb - 1 else 0x8000

    def off(self, pc, bank):
        """rom offset of pc when the code at `bank` is running, or None (RAM, I/O or an unknown switchable bank)."""
        if pc >= 0xC000:
            return (self.nb - 1) * BANK + (pc & 0x3FFF)
        if pc >= 0x8000 and (self.nb == 1 or bank != self.nb - 1):
            return (0 if self.nb == 1 else bank) * BANK + (pc & 0x3FFF)
        return None

    def trace(self, bank, pc):
        work = [(bank, pc)]
        while work:
            bank, pc = work.pop()
            while True:
                o = self.off(pc, bank)
                if o is None or o in self.code or o >= len(self.rom):
                    break
                name, mode = OPS[self.rom[o]]
                n = SIZE[mode]
                if o + n > len(self.rom):
                    break
                self.code[o] = (pc, n, f"{name} {operand(self.rom, o, pc, mode)}".strip())
                arg = int.from_bytes(self.rom[o + 1:o + n], "little")
                if mode == "rel":
                    work.append((bank, pc + 2 + (arg ^ 0x80) - 0x80 & 0xFFFF))
                if name == "JSR" and arg in self.far and o + 6 <= len(self.rom):
                    fb, fa = self.rom[o + 3], self.rom[o + 4] | self.rom[o + 5] << 8
                    self.code[o + 3] = (pc + 3, 3, f".far ${fb:02X}:${fa + 1 & 0xFFFF:04X}")
                    if fb < self.nb:
                        work.append((fb, fa + 1 & 0xFFFF))
                    pc = pc + 6 & 0xFFFF
                    continue
                if name in ("JSR", "JMP") and mode == "abs":
                    work.append((bank, arg))
                if name in STOP:
                    break
                pc = pc + n & 0xFFFF

    def listing(self):
        out, o = [], 0
        while o < len(self.rom):
            bank = o // BANK
            if o % BANK == 0:
                out.append(f"\n; ---- PRG bank ${bank:02X} at ${self.base(bank):04X} ----")
            if o in self.code:
                pc, n, txt = self.code[o]
                out.append(f"{bank:02X}:{pc:04X}  {self.rom[o:o + n].hex(' '):<9} {txt}")
                o += n
            else:
                j = o
                while j < len(self.rom) and j not in self.code and j - o < 16 and (j == o or j % BANK):
                    j += 1
                out.append(f"{bank:02X}:{self.base(bank) | o % BANK:04X}  db {self.rom[o:j].hex(' ')}")
                o = j
        return "\n".join(out) + "\n"


def run(rom, entries=(), far=()):
    d = Dis(rom, far)
    last = len(rom) // BANK - 1
    for v in (0x3FFA, 0x3FFC, 0x3FFE):
        o = last * BANK + v
        d.trace(last, rom[o] | rom[o + 1] << 8)
    for bank, pc in entries:
        d.trace(bank, pc)
    return d


def read_entries(path):
    out = []
    if path and os.path.exists(path):
        for line in open(path):
            f = line.split("#", 1)[0].split()
            if f:
                b, a = f[0].split(":")
                out.append((int(b, 16), int(a, 16)))
    return out


def read_cdl(paths, n):
    """OR of CDLHEX dumps (lib.lua's cdl_dump: hex text of emu.getCdlData(nesPrgRom), last token of the line)."""
    cdl = bytearray(n)
    for p in paths:
        raw = bytes.fromhex(open(p).read().split()[-1])
        for i, b in enumerate(raw[:n]):
            cdl[i] |= b
    return cdl


def cdl_entries(cdl, nb):
    """(bank, pc) of every code-run start, jump target or sub entry in a CDL."""
    ent = []
    for i, b in enumerate(cdl):
        if b & 1 and (b & 0x0C or not (i % BANK and cdl[i - 1] & 1)):
            bank = i // BANK
            ent.append((bank, (0xC000 if bank == nb - 1 else 0x8000) | i % BANK))
    return ent


def linear(rom, bank, pc, count):
    o = bank * BANK + (pc & 0x3FFF)
    for _ in range(count):
        name, mode = OPS[rom[o]]
        n = SIZE[mode]
        print(f"{bank:02X}:{pc:04X}  {rom[o:o + n].hex(' '):<9} {name} {operand(rom, o, pc, mode)}")
        o, pc = o + n, pc + n


FAR = []
while "--far" in sys.argv:
    k = sys.argv.index("--far"); FAR.append(int(sys.argv[k + 1], 16)); del sys.argv[k:k + 2]

if __name__ == "__main__":
    if sys.argv[1] == "cdl":
        rom = prg(sys.argv[2])
        have = set(read_entries(sys.argv[3])) | set(cdl_entries(read_cdl(sys.argv[4:], len(rom)), len(rom) // BANK))
        open(sys.argv[3], "w", newline="\n").write("".join(f"{b:02X}:{a:04X}\n" for b, a in sorted(have)))
        print(len(have), "entries")
    else:
        rom = prg(sys.argv[1])
        if sys.argv[2] == "-":
            b, a = sys.argv[3].split(":")
            linear(rom, int(b, 16), int(a, 16), int(sys.argv[4]))
        else:
            d = run(rom, read_entries(sys.argv[3]) if len(sys.argv) > 3 else (), FAR)
            open(sys.argv[2], "w", newline="\n").write(d.listing())
            print(f"{len(d.code)} instructions, {sum(n for _, n, _ in d.code.values())} code bytes")
