"""Static sweeps over a HuCard disassembly plus Mesen code/data logs (shared by '93 and '94).

  python tools/pce93/sweep.py dead  <93|94> <rom> <out.txt> <cdl...>   never-executed code (see below)
  python tools/pce93/sweep.py pad   <93|94> <rom> <out.txt> <cdl...>   code that reads the pad bytes and compares
  python tools/pce93/sweep.py flags <93|94> <rom> <out.txt> <cdl...> [--wnz log.txt ...]   RAM read but never set

The code set is a recursive trace (tools/pce9x/huc6280.py) from the vectors plus one entry per run of logged code
(slot voting as cdl2entries.py; '94 also takes disasm/pce94/entries.txt). A CDL file is Mesen's raw log (a
9-byte 'CDLv2' header is skipped); bit 0 = executed as code, bit 1 = read as data.
dead: every traced instruction never executed, grouped into blocks; each block gets its static callers
(executed or not) so it can be classed. Also "orphans": runs of never-logged bytes in code banks that decode
as clean code ending in RTS/RTI/JMP and are reached by nothing traced.
"""
import os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
STOP = {"RTS", "RTI", "JMP", "BRA", "BRK"}


def load_cdl(files, n):
    c = bytearray(n)
    for f in files:
        d = open(f, "rb").read()
        if d[:5] == b"CDLv2":
            d = d[9:]
        for i, b in enumerate(d[:n]):
            c[i] |= b
    return c


def slots(rom, cdl):
    nb = len(rom) // 0x2000
    slot = {0: 7, 1: 6}
    for b in range(2, nb):
        c = collections.Counter()
        base = b * 0x2000
        for i in range(base, base + 0x1FFD):
            if cdl[i] & 1 and rom[i] in (0x20, 0x4C) and cdl[i + 1] & 1 and cdl[i + 2] & 1:
                t = rom[i + 1] | rom[i + 2] << 8
                if 0x4000 <= t < 0xC000 and cdl[base + (t & 0x1FFF)] & 1:
                    c[t >> 13] += 1
        if c:
            slot[b] = c.most_common(1)[0][0]
    return slot


class Code:
    """Normalised trace: code[off] = (pc, n, op, text); bank slot guesses in .slot."""
    def __init__(self, game, rom, cdl):
        self.game, self.rom, self.cdl = game, rom, cdl
        self.slot = slots(rom, cdl)
        if game == "93":
            sys.path.insert(0, HERE)
            import huc6280 as H
            d = H.Dis(rom)
            vec = [rom[i] | rom[i + 1] << 8 for i in range(0x1FF6, 0x2000, 2)]
            d.run([(v, tuple(d.default)) for v in vec])
            for o, s, mpr in self.entries():
                d.run([(s << 13 | o & 0x1FFF, tuple(mpr))])
            self.code = {o: (pc, n, t.split()[0], t) for o, (pc, n, t) in d.code.items() if not t.startswith("db ")}
            self.inl = {o: (pc, n, t) for o, (pc, n, t) in d.code.items() if t.startswith("db ")}
        else:
            sys.path.insert(0, os.path.join(HERE, "..", "pce94"))
            import huc6280 as H
            d = H.Dis(rom)
            mpr = [0xFF, 0xF8, None, None, None, None, None, 0]
            for v in (0x1FFE, 0x1FFC, 0x1FFA, 0x1FF8, 0x1FF6):
                d.run(rom[v] | rom[v + 1] << 8, mpr)
            ent = os.path.join(HERE, "..", "..", "disasm", "pce94", "entries.txt")
            lst = [(int(l.split()[0], 16), int(l.split()[1])) for l in open(ent) if l.split()]
            lst += [(o, s) for o, s, _ in self.entries()]
            for ph, page in lst:
                m = list(mpr)
                m[2], m[6] = 0x61, 0x01
                m[page] = ph >> 13
                if page in (4, 5):
                    m[page ^ 1] = m[page] ^ 1
                d.run(page << 13 | ph & 0x1FFF, m)
            self.code = {o: (v[2], v[1], v[0].split()[0], v[0]) for o, v in d.code.items()
                         if v and not v[0].startswith(("db ", "dw "))}
            self.inl = {o: (v[2], v[1], v[0]) for o, v in d.code.items() if v and v[0].startswith(("db ", "dw "))}

    def entries(self):
        rom, cdl, slot = self.rom, self.cdl, self.slot
        for o in range(len(rom)):
            if not cdl[o] & 1 or (o and cdl[o - 1] & 1 and not cdl[o] & 0x0C):
                continue
            b = o >> 13
            if b not in slot:
                continue
            s = slot[b]
            mpr = [0xFF, 0xF8, None, None, None, None, 1, 0]
            if self.game == "94":
                mpr[2] = 0x61
            mpr[s] = b
            if s in (4, 5):
                mpr[s ^ 1] = b ^ 1
            yield o, s, mpr

    def target(self, o):
        """Static jump/call target of the instruction at o as a logical address, or None."""
        pc, n, op, t = self.code[o]
        m = re.search(r"\$([0-9A-F]{4})\b", t)
        if op in ("JSR", "JMP", "BSR", "BRA") or op.startswith(("B", "BBR", "BBS")) and op not in ("BIT", "BRK"):
            if m and "(" not in t and op not in ("BIT",):
                return int(m.group(1), 16)
        return None


def xrefs(c):
    """logical target -> list of caller offsets; far calls (93: JSR $EAE7 + addr,bank) keyed (addr, bank)."""
    ref = collections.defaultdict(list)
    for o in c.code:
        t = c.target(o)
        if t is not None:
            ref[t].append(o)
    for o, (pc, n, t) in c.inl.items():
        b = c.rom[o:o + n]
        if n == 3 and b[1] >= 0x40:
            ref[(b[0] | b[1] << 8, b[2])].append(o)
    return ref


def dead(c, out):
    cdl, rom = c.cdl, c.rom
    ref = xrefs(c)
    blocks, cur = [], None
    for o in sorted(c.code):
        pc, n, op, t = c.code[o]
        if cdl[o] & 1:
            cur = None
            continue
        end = cur[-1] + c.code[cur[-1]][1] if cur else None
        if end in c.inl:
            end += c.inl[end][1]
        if cur and o == end:
            cur.append(o)
        else:
            cur = [o]
            blocks.append(cur)
    lines, tot = [], 0
    for bl in blocks:
        o0 = bl[0]
        pc0 = c.code[o0][0]
        size = bl[-1] + c.code[bl[-1]][1] - o0
        tot += size
        bk = o0 >> 13
        callers = [x for x in ref.get(pc0, []) if x != o0 and (pc0 >= 0xC000 or x >> 13 in (bk, bk ^ 1, 0, 1))]
        callers += ref.get((pc0, bk), []) + ref.get((pc0, bk ^ 1), [])
        exe = [x for x in callers if cdl[x] & 1]
        # a block that starts right after an executed conditional branch / instruction is "fall-through"
        prev = max((x for x in c.code if x < o0 and x > o0 - 8), default=None)
        ft = prev is not None and prev + c.code[prev][1] == o0 and cdl[prev] & 1 and c.code[prev][2] not in STOP
        kind = "branch-not-taken" if ft or exe else "dead-callers" if callers else "table/indirect"
        lines.append(f"{o0 >> 13:02X}:{pc0:04X} file ${o0:05X} {size:5d} bytes {len(bl):4d} ins  {kind:16s} callers "
                     + (" ".join(f"{x >> 13:02X}:{c.code[x][0] if x in c.code else c.inl[x][0]:04X}{'*' if cdl[x] & 1 else ''}" for x in callers[:8]) or "-")
                     + "  | " + "; ".join(c.code[x][3] for x in bl[:6]))
    orph = orphans(c)
    with open(out, "w") as f:
        f.write(f"# {len(blocks)} never-executed blocks, {tot} bytes of traced code ({sum(n for _, n, _, _ in c.code.values())} traced bytes in all)\n")
        f.write("# kinds: branch-not-taken = after an executed branch or called by executed code; dead-callers = only called"
                " from never-executed code; table/indirect = reached only through a jump table. '*' = caller executed\n")
        f.write("\n".join(lines) + "\n\n# orphans: never-logged, untraced bytes that decode as code ending in RTS/RTI/JMP (>= 12 bytes)\n")
        f.write("\n".join(orph) + "\n")
    print(out, len(blocks), "blocks", tot, "bytes;", len(orph), "orphans")


def decode(c, o, pc):
    if c.game == "93":
        import huc6280 as H
        n, t, _ = H.decode(c.rom, o, pc)
        return n, t, H.OPS[c.rom[o]][0]
    import huc6280 as H
    op, mode = H.OPS[c.rom[o]]
    n = H.SIZE[mode]
    return n, H.fmt(op, mode, c.rom[o:o + n], pc), op


def orphans(c):
    rom, cdl = c.rom, c.cdl
    covered = bytearray(len(rom))
    for o, (pc, n, op, t) in c.code.items():
        for q in range(o, o + n):
            covered[q] = 1
    for o, (pc, n, t) in c.inl.items():
        for q in range(o, o + n):
            covered[q] = 1
    res = []
    codebanks = {b for b in range(len(rom) // 0x2000) if any(cdl[b * 0x2000 + i] & 1 for i in range(0x2000))}
    for b in sorted(codebanks):
        s = c.slot.get(b, 4)
        base = b * 0x2000
        i = 0
        while i < 0x2000:
            o = base + i
            if covered[o] or cdl[o] or rom[o] in (0x00, 0xFF):
                i += 1
                continue
            # linear decode until a stop; reject on illegal ops, covered/logged bytes, or BRK
            q, ins, ok, txt = o, 0, False, []
            while q < base + 0x2000:
                if covered[q] or cdl[q]:
                    break
                n, t, op = decode(c, q, s << 13 | q & 0x1FFF)
                if op in ("?", "-", "BRK") or q + n > base + 0x2000 or any(covered[x] or cdl[x] for x in range(q, q + n)):
                    break
                txt.append(t)
                ins += 1
                q += n
                if op in ("RTS", "RTI", "JMP"):
                    ok = True
                    break
            if ok and q - o >= 12 and ins >= 5 and sum(1 for t in txt if re.search(r"\$[23][0-9A-F]{3}\b|\$[0-9A-F]{2}\b", t)) >= 2:
                res.append(f"{b:02X}:{s << 13 | o & 0x1FFF:04X} file ${o:05X} {q - o:5d} bytes  | " + "; ".join(txt[:8]))
                i = q - base
            else:
                i += 1
    return res


def pad(c, out, padzp):
    """Every executed-or-traced read of a pad byte, with the compares that follow within 10 instructions."""
    rom, cdl = c.rom, c.cdl
    order = sorted(c.code)
    idx = {o: k for k, o in enumerate(order)}
    rx = re.compile(r"\$(?:20)?([0-9A-F]{2})\b")
    res = []
    for o in order:
        pc, n, op, t = c.code[o]
        opnd = t.split(None, 1)[1] if " " in t else ""
        m = None if opnd.startswith("#") and op != "TST" else rx.search(opnd.split(",", 1)[1] if op == "TST" else opnd)
        if not m or op.startswith(("ST", "JSR", "JMP")) or op in ("INC", "DEC"):
            continue
        a = int(m.group(1), 16)
        long = "$20" + m.group(1) in t
        if a not in padzp or not (long or re.search(r"\$" + m.group(1) + r"\b", t)) or re.search(r"\$[0-9A-F]{4}", t.split(",")[0]) and not long:
            continue
        nxt = [c.code[x] for x in order[idx[o] + 1:idx[o] + 11]]
        cmp = [x[3] for x in nxt if x[2] in ("CMP", "CPX", "CPY", "EOR") or (x[2] == "AND" and "#" in x[3])]
        tab = [x[3] for x in nxt if x[2] in ("CMP", "EOR") and re.search(r"\$[0-9A-F]{4},[XY]|\(\$", x[3])]
        imm = [x for x in cmp if "#" in x]
        multi = [x for x in imm if (m2 := re.search(r"#\$([0-9A-F]{2})", x)) and bin(int(m2.group(1), 16)).count("1") >= 2
                 and x.startswith(("CMP", "EOR"))]
        # a held-button test next to a newly-pressed test (the '93 ending's I held + Run pressed)
        held, new = (range(0x32, 0x37), range(0x37, 0x3C)) if c.game == "93" else (range(0x28, 0x2D), range(0x2D, 0x32))
        near = [t] + [x[3] for x in nxt[:5]]
        zps = {int(z, 16) for x in near for z in re.findall(r"\$(?:20)?([0-9A-F]{2})", x.split(None, 1)[1] if " " in x else "")
               if not x.split(None, 1)[1].startswith("#")} if True else set()
        both = any(z in held for z in zps) and any(z in new for z in zps) and any(x.startswith(("BBR", "BBS", "TST", "AND", "BIT")) for x in near)
        flag = "TABLE" if tab else "COMBO" if multi else "HELD+NEW" if both else ""
        res.append(f"{o >> 13:02X}:{pc:04X} {'run ' if cdl[o] & 1 else 'DEAD'} {flag:8s} {t:24s} | " + "; ".join(cmp[:5]))
    open(out, "w").write("\n".join(res) + "\n")
    print(out, len(res), "pad reads;", sum(any(k in r for k in ("TABLE", "COMBO", "HELD+NEW")) for r in res), "flagged")


def flags(c, out, wnz):
    """RAM bytes ($2000-$3FFF, zero page as $20xx) read by traced code but never the target of a store, and
    (if logs are given) never written non-zero in any coverage run."""
    rx = re.compile(r"\$([0-9A-F]{2,4})\b")
    reads, writes = collections.defaultdict(list), set()
    idxw = []
    for o, (pc, n, op, t) in c.code.items():
        parts = t.split(None, 1)
        if len(parts) < 2 or "#" in parts[1].split(",")[0] and op not in ("TST", "TII", "TIN", "TIA", "TAI", "TDD") or op in ("JSR", "JMP"):
            continue
        ms = rx.findall(parts[1])
        if op in ("TII", "TIN", "TIA", "TAI", "TDD"):
            src, dst, ln = (int(x, 16) for x in ms[:3])
            idxw.append((dst, dst + ln))
            continue
        if not ms:
            continue
        a = int(ms[0] if op != "TST" else ms[-1], 16)
        if a < 0x100:
            a |= 0x2000
        if not 0x2000 <= a < 0x4000:
            continue
        w = op.startswith(("ST", "SMB", "RMB", "INC", "DEC", "TSB", "TRB", "ASL", "LSR", "ROL", "ROR")) and op not in ("STA#",)
        if w:
            writes.add(a)
            if ",X" in parts[1] or ",Y" in parts[1] or "(" in parts[1]:
                idxw.append((a, a + 0x100))
        else:
            reads[a].append(o)
    nz = None
    if wnz:
        nz = [0] * 0x2000
        for f in wnz:
            for line in open(f):
                if line.startswith("WNZ "):
                    for i, ch in enumerate(line[4:].strip()):
                        if ch == "1":
                            nz[i] = 1
    res = []
    for a in sorted(reads):
        if a in writes:
            continue
        cov = any(lo <= a < hi for lo, hi in idxw)
        z = "" if nz is None else ("written-nonzero" if nz[a - 0x2000] else "NEVER-NONZERO")
        if nz is not None and nz[a - 0x2000]:
            continue
        rs = reads[a]
        res.append(f"${a:04X} {z:14s} {'idx-write-range' if cov else 'no-store':15s} reads {len(rs):3d}: "
                   + " ".join(f"{o >> 13:02X}:{c.code[o][0]:04X}{'' if c.cdl[o] & 1 else '-'} {c.code[o][3]}" for o in rs[:4]))
    open(out, "w").write("\n".join(res) + "\n")
    print(out, len(res), "candidates")


if __name__ == "__main__":
    cmd, game, romf, out = sys.argv[1:5]
    rest = sys.argv[5:]
    wnz = []
    if "--wnz" in rest:
        k = rest.index("--wnz")
        wnz, rest = rest[k + 1:], rest[:k]
    rom = open(romf, "rb").read()
    c = Code(game, rom, load_cdl(rest, len(rom)))
    if cmd == "dead":
        dead(c, out)
    elif cmd == "pad":
        pad(c, out, set(range(0x32, 0x3C)) if game == "93" else set(range(0x28, 0x32)) | {0xC1, 0xC2, 0xC5})
    elif cmd == "flags":
        flags(c, out, wnz)
