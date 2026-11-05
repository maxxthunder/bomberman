"""Small recursive-descent HuC6280 disassemblers for PC Engine HuCard images (no header, banks of 8 KB).

Usage: python tools/huc6280.py <rom.pce> <out.asm> [entries.txt]                ('90, Users Battle)
       python tools/huc6280.py <rom.pce> - <bank:addr> <count>                  (linear listing to stdout)
       python tools/huc6280.py cdl <entries.txt> "<MAPS line>" cdl.hex...       (merge CDL dumps into entries.txt)
       python tools/huc6280.py 93 <rom.pce> <out.asm> [entries.txt]             ('93, see Dis93)
       python tools/huc6280.py 94 <rom.pce> <outdir> [entries.txt]              ('94, see Dis94)

All trace from the vectors at the end of bank 0 (mapped at $E000 on power-up) and track the MPR bank registers
where code sets them (LDA #n / TAM #m, or CLA / TAM). They differ in what else they follow and how they list:

Dis ('90, Users Battle): a TAM with an unknown A marks those pages unknown, and code is not followed into an
unknown page. JSR assumes the callee keeps the mapping. JMP (abs,X) tables are followed while their entries land
in a mapped ROM page. entries.txt lines: `bank:addr` (hex, e.g. `03:6A20`) = extra code entry, that bank mapped
at addr's page. Listing lines: `bb:aaaa  bytes  op` with bb = ROM bank, aaaa = logical address; unreached bytes
are `db`.

Dis93: JSRs to routines that take inline argument bytes are recognised (see inline_len); a 3-byte task call
(address, bank) is followed with that bank at $8000 and the next at $A000 ($EAE7 in the US game). JMP (abs,X)
tables are followed (see table). Each line is  BB:LLLL  bytes  instruction, BB = ROM bank, LLLL = logical address
it was traced at. entries.txt lines: "logical mpr0 ... mpr7" in hex, e.g. "dcb0 ff f8 -- -- 06 07 01 00" (extra
code starts with the bank mapping there, "--" = unknown; pce93/cdl2entries.py makes them from Mesen code/data
logs). Bytes never reached are written as db. Zero page is logical $2000 (work RAM at MPR1 = $F8).

Dis94: code reached through a page whose bank is unknown is not followed (the target is noted as `; ?bank`).
entries.txt lines: `<phys hex> <page 0-7>` (an entry point: ROM offset and the 8 KB page it runs in), e.g. taken
from an emulator trace (pce94/trace.lua). Pages 2 and 6 are taken to hold banks $61 and $01 and pages 4/5 an
even/odd pair, as every trace of the game showed. Writes <outdir>/bankNN.asm (one per 8 KB bank, unreached bytes
as db) and <outdir>/labels.txt; entries.txt defaults to <outdir>/entries.txt.
"""
import os
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


def decode(rom, off, pc, bare=False):
    """-> (size, text, branch target or None). bare ('94 listings): `ASL` for ASL A, `db $xx` for undefined ops."""
    op = rom[off]
    m, mode = OPS[op]
    n = SIZE[mode]
    b = rom[off + 1:off + n]
    if bare and (mode == "acc" or m == "?"):
        return n, m if m != "?" else "db $%02X" % op, None
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


# ---- '90 / Users Battle ----
WRITES_A = {"PLA", "TXA", "TYA", "ADC", "SBC", "AND", "ORA", "EOR", "SAX", "SAY", "TMA", "JSR", "BSR"}
STOP = {"RTS", "RTI", "BRA", "?", "BRK"}


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
                n, text, _ = decode(self.rom, o, pc)
                self.code[o] = (pc, n, text)
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
                elif mode == "zpr":
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
        n, text, _ = decode(rom, o, pc)
        print(f"{bank:02X}:{pc:04X}  {rom[o:o + n].hex(' '):<20} {text}" + " " * (OPS[rom[o]][1] == "imp"))
        o, pc = o + n, pc + n


def cdl_entries(cdl_hex_files, maps, out):
    """Merge Mesen CDL dumps (hex text) into entries.txt: each run of code bytes starts an instruction, mapped at
    the page(s) the bank was seen at (maps: 'bb:p' tokens from lib.lua's maps_dump)."""
    pages = {}
    for t in maps.split():
        b, p = t.split(":")
        pages.setdefault(int(b, 16), []).append(int(p))
    have = set(read_entries(out)) if os.path.exists(out) else set()
    for path in cdl_hex_files:
        c = bytes.fromhex(open(path).read().strip())
        for i, b in enumerate(c):
            if b & 1 and not (i and c[i - 1] & 1 and i % 0x2000):
                for p in pages.get(i >> 13, []):
                    have.add((i >> 13, p << 13 | i & 0x1FFF))
    open(out, "w").write("".join(f"{b:02X}:{a:04X}\n" for b, a in sorted(have)))
    print(len(have), "entries")


# ---- '93 ----
STOP93 = {"RTS", "RTI", "JMP", "BRA", "BRK", "?"}
KEEP_A = {"TAM", "STA", "PHA", "TAX", "TAY", "CMP", "BIT", "SEI", "CLI", "CLC", "SEC", "CSH", "CSL"}
TASK_FRAME = bytes.fromhex("860385026885066885076885")   # STX $03 / STA $02 / PLA / STA $06 / PLA / STA $07 / PLA / STA


class Dis93:
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
                if m in STOP93:
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


def main93(argv):
    rom = open(argv[0], "rb").read()
    d = Dis93(rom)
    vec = [rom[i] | rom[i + 1] << 8 for i in range(0x1FF6, 0x2000, 2)]
    d.run([(v, tuple(d.default)) for v in vec])
    if len(argv) > 2:
        for line in open(argv[2]):
            f = line.split("#", 1)[0].split()
            if not f:
                continue
            pc, mpr = int(f[0], 16), [None if x == "--" else int(x, 16) for x in f[1:9]]
            d.mark(mpr, pc, "E")
            d.run([(pc, tuple(mpr))])
    d.write(argv[1])
    print(f"{sum(n for _, n, _ in d.code.values())} code bytes of {len(rom)}")


# ---- '94 ----
AW = WRITES_A | {"LDA"}
# JSRs followed by inline data (bank 0, always at $E000): $E501 sets the current task's next handler to
# (return address + signed byte), $E528 to the inline word; both return past the data. $E405/$E409 take 3/4
# bytes of inline data (a pointer, a bank for $E409, a mode).
INLINE = {0xE501: 1, 0xE528: 2}
STOP94 = {"RTS", "RTI", "JMP", "BRA", "BRK", "?"}


class Dis94:
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
                self.code[p] = (decode(self.rom, p, pc, True)[1], n, pc)
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
                elif op in AW or mode == "acc":
                    a = None
                if op in STOP94:
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


def main94(argv):
    rom = open(argv[0], "rb").read()
    d = Dis94(rom)
    mpr = [0xFF, 0xF8, None, None, None, None, None, 0]
    for name, v in (("reset", 0x1FFE), ("nmi", 0x1FFC), ("timer", 0x1FFA), ("irq1", 0x1FF8), ("irq2", 0x1FF6)):
        d.run(rom[v] | rom[v + 1] << 8, mpr, name)
    ent = argv[2] if len(argv) > 2 else os.path.join(argv[1], "entries.txt")
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
    d.write(argv[1])
    n = sum(1 for v in d.code.values() if v)
    print("instructions", n, "bytes", len(d.code))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "cdl":  # cdl <entries.txt> "<MAPS line>" cdl.hex...
        cdl_entries(a[3:], a[2], a[1])
    elif a[0] in ("93", "94"):
        (main93 if a[0] == "93" else main94)(a[1:])
    elif a[1] == "-":
        b, ad = a[2].split(":")
        linear(open(a[0], "rb").read(), int(b, 16), int(ad, 16), int(a[3]))
    else:
        d = run(open(a[0], "rb").read(), read_entries(a[2]) if len(a) > 2 else ())
        open(a[1], "w").write(d.listing())
        print(f"{len(d.code)} instructions, {sum(n for _, n, _ in d.code.values())} code bytes")
