"""Small recursive-descent SM83 (Game Boy CPU) disassembler for MBC1/MBC5 ROMs (16 KB banks). Shared by tools/gb1-gb3.

Usage: python tools/sm83.py <rom.gb> <out.asm> [entries.txt | run.cdl ...]   (.cdl: Mesen CDLs, all ORed)
       python tools/sm83.py <rom.gb> - <bank:addr> <count>       (linear listing to stdout)

Traces from the entry point $0100, the RST vectors and the interrupt vectors in bank 0. Code at $4000-$7FFF runs in
a known bank when the tracer is already in that bank, or after `LD A,n` followed by a store to $2000-$3FFF (the MBC
bank register) on the same path; with no known bank, a jump into $4000-$7FFF is not followed.
entries.txt lines: `bank:addr` (hex, e.g. `03:6A20`), extra code entries, e.g. every executed code start from a Mesen
CDL (`cdl_entries()` below: the ROM offset gives the bank directly). JP (HL) is not followed (the CDL covers it).
Listing lines: `bb:aaaa  bytes        op`; bb = ROM bank, unreached bytes are `db`. Labels: `; <- bb:aaaa call` comments
mark call targets.
"""
import sys

R8 = ["B", "C", "D", "E", "H", "L", "(HL)", "A"]
R16 = ["BC", "DE", "HL", "SP"]
R16S = ["BC", "DE", "HL", "AF"]
CC = ["NZ", "Z", "NC", "C"]
ALU = ["ADD A,", "ADC A,", "SUB ", "SBC A,", "AND ", "XOR ", "OR ", "CP "]
ROT = ["RLC", "RRC", "RL", "RR", "SLA", "SRA", "SWAP", "SRL"]
MISC = ["RLCA", "RRCA", "RLA", "RRA", "DAA", "CPL", "SCF", "CCF"]


def opinfo(op):
    """-> (template, size). Template fields: n8 {b}, n16 {w}, rel {r}, ff00+n {h}, signed {s}."""
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    p, q = y >> 1, y & 1
    if x == 1:
        return ("HALT", 1) if op == 0x76 else (f"LD {R8[y]},{R8[z]}", 1)
    if x == 2:
        return (f"{ALU[y]}{R8[z]}", 1)
    if x == 0:
        if z == 0:
            return [("NOP", 1), ("LD ({w}),SP", 3), ("STOP", 2), ("JR {r}", 2),
                    ("JR NZ,{r}", 2), ("JR Z,{r}", 2), ("JR NC,{r}", 2), ("JR C,{r}", 2)][y]
        if z == 1:
            return (f"LD {R16[p]},{{w}}", 3) if q == 0 else (f"ADD HL,{R16[p]}", 1)
        if z == 2:
            return (["LD (BC),A", "LD (DE),A", "LD (HL+),A", "LD (HL-),A",
                     "LD A,(BC)", "LD A,(DE)", "LD A,(HL+)", "LD A,(HL-)"][q * 4 + p], 1)
        if z == 3:
            return (f"{'INC' if q == 0 else 'DEC'} {R16[p]}", 1)
        if z == 4:
            return (f"INC {R8[y]}", 1)
        if z == 5:
            return (f"DEC {R8[y]}", 1)
        if z == 6:
            return (f"LD {R8[y]},{{b}}", 2)
        return (MISC[y], 1)
    # x == 3
    if z == 0:
        if y < 4:
            return (f"RET {CC[y]}", 1)
        return [("LDH ({h}),A", 2), ("ADD SP,{s}", 2), ("LDH A,({h})", 2), ("LD HL,SP+{s}", 2)][y - 4]
    if z == 1:
        if q == 0:
            return (f"POP {R16S[p]}", 1)
        return [("RET", 1), ("RETI", 1), ("JP (HL)", 1), ("LD SP,HL", 1)][p]
    if z == 2:
        if y < 4:
            return (f"JP {CC[y]},{{w}}", 3)
        return [("LD ($FF00+C),A", 1), ("LD ({w}),A", 3), ("LD A,($FF00+C)", 1), ("LD A,({w})", 3)][y - 4]
    if z == 3:
        return [("JP {w}", 3), ("CB", 2), ("?", 1), ("?", 1), ("?", 1), ("?", 1), ("DI", 1), ("EI", 1)][y]
    if z == 4:
        return (f"CALL {CC[y]},{{w}}", 3) if y < 4 else ("?", 1)
    if z == 5:
        if q == 0:
            return (f"PUSH {R16S[p]}", 1)
        return ("CALL {w}", 3) if p == 0 else ("?", 1)
    if z == 6:
        return (f"{ALU[y]}{{b}}", 2)
    return (f"RST ${y * 8:02X}", 1)


OPS = [opinfo(i) for i in range(256)]


def cbname(b):
    x, y, z = b >> 6, (b >> 3) & 7, b & 7
    return f"{ROT[y]} {R8[z]}" if x == 0 else f"{['BIT', 'RES', 'SET'][x - 1]} {y},{R8[z]}"


def decode(rom, o, pc):
    """-> (text, size, targets, flow) for the instruction at rom offset o, logical pc.
    flow: 'stop' (RET/JP/JR/RETI/JP HL), 'cond', 'call', 'jump', or None."""
    op = rom[o]
    t, n = OPS[op]
    if op == 0xCB:
        return cbname(rom[o + 1]), 2, None, None
    b = rom[o + 1] if n > 1 and o + 1 < len(rom) else 0
    w = rom[o + 1] | rom[o + 2] << 8 if n == 3 and o + 2 < len(rom) else 0
    r = (pc + 2 + (b ^ 0x80) - 0x80) & 0xFFFF
    s = (b ^ 0x80) - 0x80
    txt = t.format(b=f"${b:02X}", w=f"${w:04X}", r=f"${r:04X}", h=f"$FF{b:02X}", s=f"{s:+d}")
    tgt = None
    if t.startswith("JR"):
        tgt = r
    elif t.startswith(("JP ", "CALL")) and "{w}" in t:
        tgt = w
    elif t.startswith("RST"):
        tgt = y8 = op & 0x38
    flow = None
    if t in ("RET", "RETI", "JP (HL)", "JR {r}", "JP {w}", "?"):
        flow = "stop"
    elif t.startswith("CALL") or t.startswith("RST"):
        flow = "call"
    elif t.startswith(("JR", "JP", "RET ")):
        flow = "cond"
    return txt, n, tgt, flow


def off(bank, pc):
    if pc < 0x4000:
        return pc
    if pc < 0x8000 and bank is not None:
        return bank * 0x4000 + (pc - 0x4000)
    return None


def loc(o):
    """rom offset -> (bank, logical address)"""
    return (0, o) if o < 0x4000 else (o >> 14, 0x4000 | o & 0x3FFF)


class Dis:
    def __init__(self, rom):
        self.rom = rom
        self.nb = len(rom) // 0x4000
        self.code = {}       # rom offset -> (pc, size, text)
        self.calls = {}      # target rom offset -> set of source offsets
        self.noret = set()   # call targets that never return (extend here per game: e.g. a far-call that pops)

    def trace(self, bank, pc):
        work = [(bank, pc)]
        while work:
            bank, pc = work.pop()
            a = None                  # last LD A,n on this path
            while True:
                o = off(bank, pc)
                if o is None or o >= len(self.rom) or o in self.code:
                    break
                txt, n, tgt, flow = decode(self.rom, o, pc)
                self.code[o] = (pc, n, txt)
                op = self.rom[o]
                if op == 0x3E:
                    a = self.rom[o + 1]
                elif op == 0xEA and 0x2000 <= (self.rom[o + 1] | self.rom[o + 2] << 8) < 0x4000 and a is not None:
                    bank = a % self.nb or 1   # MBC1: bank 0 selects 1
                elif op == 0xAF:
                    a = 0
                elif txt.startswith(("LD A,", "LDH A,", "POP AF", "INC A", "DEC A", "ADD A", "SUB", "AND", "OR",
                                     "XOR", "ADC", "SBC", "CPL", "RLA", "RRA", "RLCA", "RRCA", "SWAP A", "CALL", "RST")):
                    a = None
                if tgt is not None:
                    tb = bank if tgt >= 0x4000 else 0
                    to = off(tb, tgt)
                    if to is not None:
                        if flow == "call":
                            self.calls.setdefault(to, set()).add(o)
                        work.append((tb, tgt))
                    if flow == "call" and to in self.noret:
                        break
                if flow == "stop":
                    break
                pc += n
                if pc >= 0x8000 or (pc == 0x4000 and o < 0x4000):
                    break

    def listing(self, out):
        rom, o = self.rom, 0
        while o < len(rom):
            b, a = loc(o)
            if o in self.code:
                pc, n, txt = self.code[o]
                c = f"  ; <- call" if o in self.calls else ""
                out.write(f"{b:02X}:{pc:04X}  {rom[o:o + n].hex(' ').upper():<9} {txt}{c}\n")
                o += n
            else:
                j = o + 1
                while j < len(rom) and j not in self.code and j - o < 8 and (j & 0x3FFF):
                    j += 1
                out.write(f"{b:02X}:{a:04X}  {'':<9} db {','.join('$%02X' % x for x in rom[o:j])}\n")
                o = j


def read_entries(path):
    ents = []
    for line in open(path):
        f = line.split("#", 1)[0].split()
        if f:
            b, a = f[0].split(":")
            ents.append((int(b, 16), int(a, 16)))
    return ents


def cdl_entries(cdl):
    """Mesen GB CDL (1 byte per ROM byte; bit 0 code, bit 2 jump target, bit 3 sub entry) -> [(bank, addr)]:
    every executed run start, jump target and sub entry."""
    ents = []
    for i, c in enumerate(cdl):
        if c & 1 and (c & 0x0C or not (i & 0x3FFF and cdl[i - 1] & 1)):
            ents.append(loc(i))
    return ents


def load_cdl(paths, n):
    """OR several CDL files (Mesen .cdl with CDLv2 header, or raw cdl_dump output) into one n-byte array."""
    c = bytearray(n)
    for p in paths:
        raw = open(p, "rb").read()[-n:]
        for i, v in enumerate(raw):
            c[i] |= v
    return c


def run(rom, entries=()):
    d = Dis(rom)
    for v in (0x100, 0x40, 0x48, 0x50, 0x58, 0x60):   # RST vectors are traced when an RST uses them
        d.trace(0, v)
    for b, a in entries:
        d.trace(b, a)
    return d


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    if sys.argv[2] == "-":
        b, a = (int(x, 16) for x in sys.argv[3].split(":"))
        for _ in range(int(sys.argv[4])):
            o = off(b, a)
            txt, n, _, _ = decode(rom, o, a)
            print(f"{b:02X}:{a:04X}  {rom[o:o + n].hex(' ').upper():<9} {txt}")
            a += n
    else:
        cdls = [p for p in sys.argv[3:] if p.endswith(".cdl")]
        ents = [e for p in sys.argv[3:] if not p.endswith(".cdl") for e in read_entries(p)]
        if cdls:
            ents += cdl_entries(load_cdl(cdls, len(rom)))
        d = run(rom, ents)
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            d.listing(f)
        print(len(d.code), "instructions,", sum(n for _, n, _ in d.code.values()), "code bytes", file=sys.stderr)
