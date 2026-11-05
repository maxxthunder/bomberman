"""Hidden-content sweeps over a disassembly (disasm/<g>/<ver>/bank_*.asm) plus Mesen code/data logs.
Shared by sb1 and sb2 (tools/sb2/sweep.py imports this file).

  python tools/sb1/sweep.py dead  <asmdir> <rom> <cdl...>   routines (call/jump targets) never executed
  python tools/sb1/sweep.py dead2 <asmdir> <rom> <cdl...>   never-run code: reachable from run code / islands
  python tools/sb1/sweep.py pads  <asmdir> <padaddrs>       code that tests pad bytes against constants/tables
  python tools/sb1/sweep.py flags <asmdir> [<cdl...> --rom R] RAM tested then branched on, never written
  python tools/sb1/sweep.py cov   <rom> <cdl...>            coverage numbers of the merged log
  python tools/sb1/sweep.py show  <asmdir> <addr> [n]       n listing lines from addr

<cdl> is a Mesen .cdl (9-byte header, CRC must match the ROM) or a hex text dump (CDLHEX/CDL lines or bare hex).
<padaddrs> is a comma list of RAM ranges, e.g. 0CE1-0CFF or 7F402E-7F404B,00C3-00C6.
"""
import binascii, glob, os, re, sys, zlib

LINE = re.compile(r"^\s+([A-Z]{3})\s*(.*?)\s*; \$([0-9A-F]{6})  ((?:[0-9A-F]{2} )+)\s*([Mm][Xx])")
LABEL = re.compile(r"^L_([0-9A-F]{6}):")


def load_asm(d):
    """-> ordered list of (addr, mnem, operand, nbytes, m8) for every decoded instruction."""
    out = []
    for p in sorted(glob.glob(os.path.join(d, "bank_*.asm"))):
        for line in open(p):
            g = LINE.match(line)
            if g:
                out.append((int(g[3], 16), g[1], g[2], len(g[4].split()), g[5][0] == "m"))
    return out


def load_cdl(rom, paths):
    """OR of every code/data log that belongs to this ROM (by CRC for .cdl files)."""
    crc = zlib.crc32(rom)
    acc = bytearray(len(rom))
    used = []
    for p in paths:
        force = p.startswith("force:")  # a log of a patched copy of this ROM
        p = p[6:] if force else p
        raw = open(p, "rb").read()
        if raw[:5] == b"CDLv2":
            if int.from_bytes(raw[5:9], "little") != crc and not force:
                continue
            c = raw[9:]
        else:
            toks = [t for t in raw.split() if len(t) >= len(rom) * 2 - 8]
            if not toks:
                continue
            t = toks[-1][: len(rom) * 2]
            c = binascii.unhexlify(t[: len(t) // 2 * 2])
            if b"CDL " + t[:16] in raw and len(c) == len(rom) - 1:  # sb2 coverage.lua dumped c[1..]: index 0 lost
                c = b"\0" + c
        if len(c) < len(rom) // 2:
            continue
        for i, b in enumerate(c[: len(rom)]):
            if b:
                acc[i] |= b
        used.append(p)
    return acc, used


def off(a):  # HiROM $C0-$FF
    return a - 0xC00000 if a >= 0xC00000 else (a & 0x3FFFFF)


def targets(ins):
    """call/jump targets: {target: kind}, kind 'call' (JSR/JSL) or 'jump' (JMP/JML/branch)."""
    t = {}
    for a, mn, op, n, _ in ins:
        g = re.match(r"L_([0-9A-F]{6})$", op)
        if not g:
            continue
        x = int(g[1], 16)
        if mn in ("JSR", "JSL"):
            t[x] = "call"
        elif mn in ("JMP", "JML"):
            t.setdefault(x, "jump")
    return t


def routines(ins):
    """Routine entry points: call targets plus labels nothing branches to (pointer-table entries)."""
    insaddr = {a for a, *_ in ins}
    called = targets(ins)
    branched = set()
    for a, mn, op, n, _ in ins:
        g = re.search(r"L_([0-9A-F]{6})", op)
        if g and mn not in ("JSR", "JSL"):
            branched.add(int(g[1], 16))
    ent = {a: "call" for a, k in called.items() if k == "call" and a in insaddr}
    prev = None
    for a, mn, op, n, _ in ins:  # an instruction after a stop that nothing jumps to = pointer entry
        if prev in ("RTS", "RTL", "RTI", "JMP", "JML", "BRA", "BRL") and a not in branched and a not in ent:
            ent[a] = "ptr"
        prev = mn
    return dict(sorted(ent.items()))


def cmd_dead(asmdir, rom, cdls):
    ins = load_asm(asmdir)
    c, used = load_cdl(rom, cdls)
    print(f"# logs merged: {len(used)}")
    ent = routines(ins)
    addrs = [a for a, *_ in ins]
    keys = list(ent)
    callers = {}
    for a, mn, op, n, _ in ins:
        g = re.search(r"L_([0-9A-F]{6})", op)
        if g:
            callers.setdefault(int(g[1], 16), []).append(a)
    import bisect
    def routine_ran(x):
        j = bisect.bisect_right(keys, x) - 1
        if j < 0:
            return False
        lo, hi = keys[j], keys[j + 1] if j + 1 < len(keys) else x + 1
        return any(c[off(a)] & 1 for a in range(lo, min(hi, x + 1)))
    dead = []
    for i, e in enumerate(keys):
        if c[off(e)] & 1:
            continue
        end = keys[i + 1] if i + 1 < len(keys) else e + 1
        size = sum(n for a, mn, op, n, _ in ins if e <= a < end)
        # live callers = callers inside a routine that did run (the call itself sits on a path not taken)
        cl = callers.get(e, [])
        live = [x for x in cl if routine_ran(x)]
        dead.append((e, ent[e], size, cl, live))
    print(f"# routines {len(ent)}, never executed {len(dead)}")
    for e, k, size, cl, live in dead:
        # pointer bytes: 24-bit anywhere, or 16-bit (also addr-1, for RTS/RTL tables) in the same bank
        p24 = rom.count(e.to_bytes(3, "little"))
        bank = rom[off(e) & ~0xFFFF:(off(e) & ~0xFFFF) + 0x10000]
        p16 = bank.count((e & 0xFFFF).to_bytes(2, "little")) + bank.count(((e - 1) & 0xFFFF).to_bytes(2, "little"))
        s = ("live caller" if live else "only dead callers") if cl else ("pointer?" if p24 or p16 else "unreferenced")
        print(f"{e:06X} {k:4} {size:5}B  {s:17} ptr24 {p24} ptr16 {p16:2}  callers {' '.join('%06X' % x for x in cl[:6])}")


def cmd_dead2(asmdir, rom, cdls, minlen=8):
    """Never-run code in two groups.
    A) reachable: instructions reached by direct branches/calls/fall-through from code that ran, but never run
       themselves; grouped by the entry where the run-time path left executed code.
    B) islands: decoded code nothing that ran leads to, kept only when it looks like real code: starts right
       after a return/jump, at least <minlen> instructions, no BRK/COP/WDM/STP, contains an RTS/RTL/RTI/JMP/JML."""
    ins = load_asm(asmdir)
    c, used = load_cdl(rom, cdls)
    at = {a: k for k, (a, *_r) in enumerate(ins)}
    ran = lambda a: c[off(a)] & 1
    stop = {"RTS", "RTL", "RTI", "JMP", "JML", "BRA", "BRL", "STP"}
    def succ(k):
        a, mn, op, n, _ = ins[k]
        out = []
        g = re.search(r"L_([0-9A-F]{6})", op)
        if g and int(g[1], 16) in at:
            out.append(at[int(g[1], 16)])
        if mn not in stop and k + 1 < len(ins) and ins[k + 1][0] == a + n:
            out.append(k + 1)
        return out
    seen, frontier = set(), []
    for k, (a, mn, *_r) in enumerate(ins):
        # from code that ran, only a conditional branch can lead to code that did not (a JSR/JMP/BRA that ran
        # always reaches its target; a miss there means the listing decoded those bytes wrongly)
        if ran(a) and mn in BRANCH:
            for t in succ(k):
                if not ran(ins[t][0]):
                    frontier.append((t, a))
    entry_of = {}
    for t, src in frontier:
        if t in seen:
            continue
        stack = [t]
        while stack:
            x = stack.pop()
            if x in seen or ran(ins[x][0]):
                continue
            seen.add(x)
            entry_of[x] = (ins[t][0], src)
            stack += succ(x)
    groups = {}
    for x, (e, src) in entry_of.items():
        g = groups.setdefault(e, [src, 0, 0])
        g[1] += 1
        g[2] += ins[x][3]
    print(f"# logs {len(used)}; A) never-run code reachable from code that ran: {len(groups)} entries, "
          f"{sum(g[2] for g in groups.values())} bytes")
    for e in sorted(groups):
        src, ni, nb = groups[e]
        print(f"A {e:06X} {nb:5}B {ni:4} ins  from {src:06X} {ins[at[src]][1]} {ins[at[src]][2]}")
    # islands
    isl, k = [], 0
    while k < len(ins):
        a = ins[k][0]
        if ran(a) or k in seen:
            k += 1
            continue
        j = k
        while j < len(ins) and not ran(ins[j][0]) and j not in seen and (j == k or ins[j][0] == ins[j - 1][0] + ins[j - 1][3]):
            j += 1
        blk = ins[k:j]
        prev = ins[k - 1][1] if k else "RTS"
        ok = (len(blk) >= minlen and prev in stop and any(b[1] in ("RTS", "RTL", "RTI", "JMP", "JML") for b in blk)
              and not any(b[1] in ("BRK", "COP", "WDM", "STP") for b in blk))
        if ok:
            isl.append((blk[0][0], len(blk), sum(b[3] for b in blk)))
        k = j
    print(f"# B) code islands nothing that ran leads to: {len(isl)}, {sum(i[2] for i in isl)} bytes")
    for a, ni, nb in isl:
        p24 = rom.count(a.to_bytes(3, "little"))
        bank = rom[off(a) & ~0xFFFF:(off(a) & ~0xFFFF) + 0x10000]
        p16 = bank.count((a & 0xFFFF).to_bytes(2, "little")) + bank.count(((a - 1) & 0xFFFF).to_bytes(2, "little"))
        # LDA #addr (an object's next-state pointer, STA $00,X) at a site that ran
        lo = bytes([0xA9, a & 0xFF, (a >> 8) & 0xFF])
        imm = [i for i in range(len(rom)) if rom[i:i + 3] == lo and (i >> 16) == (off(a) >> 16)]
        live = sum(1 for i in imm if c[i] & 1)
        print(f"B {a:06X} {nb:5}B {ni:4} ins  ptr24 {p24} ptr16 {p16} LDA# {len(imm)} (ran {live})")


# --- input-code scanner -----------------------------------------------------------------------------
def ranges(spec):
    r = []
    for part in spec.split(","):
        lo, hi = (part.split("-") + [part])[:2]
        r.append((int(lo, 16), int(hi, 16)))
    return r


def ram_of(op):
    """RAM address an operand names (no index), as a 24-bit value; abs < $2000 -> bank 0."""
    g = re.match(r"\$([0-9A-F]{2,6})(,[XY])?$", op)
    if not g:
        return None
    v = int(g[1], 16)
    return v


def in_ranges(v, rs):
    if v is None:
        return False
    cand = {v, v & 0xFFFF if v >> 16 in (0x7E, 0, 0x80) else -1}
    return any(lo <= x <= hi for x in cand for lo, hi in rs)


BTN = ["R", "L", "X", "A", "Right", "Left", "Down", "Up", "Start", "Select", "Y", "B"]  # bit 4 .. bit 15


def buttons(v, m8):
    """Names for a pad mask; an 8-bit value could be either byte, so both readings are given."""
    def nm(w):
        return "+".join(BTN[k - 4] for k in range(4, 16) if w >> k & 1) or "-"
    return f"lo:{nm(v)}/hi:{nm(v << 8)}" if m8 else nm(v)


def imm(op):
    g = re.match(r"#\$([0-9A-F]+)$", op)
    return int(g[1], 16) if g else None


def cmd_pads(asmdir, spec=None, rom=None):
    """Static input-code scanner. Patterns (each hit flagged 'pad' when the tested value was loaded from
    one of the pad ranges in <spec> within the few instructions before):
      window   CMP #a / Bcc / CMP #b / Bcc on one value, then INC: a frame counter checked against a rhythm window
      combo    AND #m then CMP/EOR #m (2+ bits): a held button combination
      exact    CMP #v (2+ button bits) right after a pad load
      table    CMP/EOR table,X|Y or (dp),Y|[dp],Y with an index register loaded from RAM: a sequence table"""
    ins = load_asm(asmdir)
    rs = ranges(spec) if spec else []
    stop = {"RTS", "RTL", "RTI", "JMP", "JML", "BRA", "BRL"}
    hits = []

    def padload(i, back=4):
        for j in range(i - 1, max(i - 1 - back, -1), -1):
            mn, op = ins[j][1], ins[j][2]
            if mn in stop:
                return None
            if mn in ("LDA", "AND", "ORA", "BIT", "EOR") and op.startswith("$") and in_ranges(ram_of(op.split(",")[0]), rs):
                return f"{mn} {op}"
            if mn == "LDA":
                return None
        return None

    for i, (a, mn, op, n, m8) in enumerate(ins):
        win = ins[i + 1:i + 8]
        v = imm(op)
        if mn in ("LDA", "BIT", "AND") and rs and op.startswith("$") and in_ranges(ram_of(op.split(",")[0]), rs):
            t = [w for w in win[:2] if w[1] in ("BIT", "AND") and imm(w[2]) is not None]
            if t and "," not in op:  # a fixed pad (not indexed by player): which pad and which buttons
                hits.append((a, "test", f"{mn} {op} / {t[0][1]} {t[0][2]} {buttons(imm(t[0][2]), t[0][4])}", None))
        if mn == "CMP" and v is not None and v < 0x40 and len(win) > 2:
            b1, c2, b2 = win[0], win[1], win[2]
            if b1[1] in ("BCC", "BCS") and c2[1] == "CMP" and imm(c2[2]) is not None and b2[1] in ("BCC", "BCS"):
                tail = ins[i + 4:i + 10]
                inc = [w for w in tail if w[1] == "INC" and w[2].startswith("$")]
                inc += [tail[k + 1] for k in range(len(tail) - 1) if tail[k][1] == "INC" and not tail[k][2] and tail[k + 1][1] == "STA"]
                if inc:
                    src = next((ins[j][2] for j in range(i - 1, max(i - 6, 0), -1) if ins[j][1] == "LDA"), "?")
                    hits.append((a, "window", f"{src} in [{v:#x},{imm(c2[2]):#x}) then INC {inc[0][2]}", padload(i, 12)))
        if mn == "AND" and v is not None and bin(v).count("1") >= 2:
            for w in win[:2]:
                if w[1] in ("CMP", "EOR") and imm(w[2]) == v:
                    hits.append((a, "combo", f"AND/{w[1]} #{v:#06x} {buttons(v, m8)}", padload(i)))
        if mn in ("CMP", "EOR") and v is not None and bin(v).count("1") >= 2 and (v & 0xFFF0 if not m8 else v):
            pl = padload(i, 2)
            if pl:
                hits.append((a, "exact", f"{mn} #{v:#06x} {buttons(v, m8)}", pl))
        if mn in ("CMP", "EOR") and (re.match(r"\$[0-9A-F]{4,6},[XY]$", op) or re.match(r"[\[(]\$[0-9A-F]{2}[\])],Y$", op)):
            reg = op[-1]
            idx = next((ins[j] for j in range(i - 1, max(i - 10, 0), -1) if ins[j][1] in ("LD" + reg,) or ins[j][1] in stop), None)
            if idx and idx[1] == "LD" + reg and idx[2].startswith("$") and "," not in idx[2]:
                tail = [w for w in ins[i + 1:i + 14] if w[1] in ("INC", "IN" + reg) or (w[1] == "ST" + reg and w[2] == idx[2])]
                pl = padload(i, 8)
                if tail or pl:
                    hits.append((a, "table", f"{mn} {op}, index {idx[2]}" + (f", then {tail[0][1]} {tail[0][2]}" if tail else ""), pl))
    for a, k, why, pl in hits:
        print(f"{a:06X} {k:6} {why}" + (f"   <- pad {pl}" if pl else ""))
    print(f"# {len(hits)} hits")


# --- read-but-never-written flags ------------------------------------------------------------------
WRITES = {"STA", "STZ", "STX", "STY", "INC", "DEC", "ASL", "LSR", "ROL", "ROR", "TSB", "TRB"}
TESTS = {"LDA", "LDX", "LDY", "BIT", "CMP", "CPX", "CPY", "AND", "ORA"}
BRANCH = {"BEQ", "BNE", "BMI", "BPL", "BVS", "BVC", "BCC", "BCS"}


def norm(v):
    """Fold mirrors: $00xxxx/$80xxxx/$7Exxxx low 8 KB to one key; keep $7E/$7F long addresses."""
    if v is None:
        return None
    if v < 0x10000:
        return v if v < 0x2000 else (0x7E0000 | v if v >= 0x6000 else None)  # $2000-$5FFF = I/O
    b = v >> 16
    if b in (0x7E,) or (b < 0x40 or 0x80 <= b < 0xC0):
        lo = v & 0xFFFF
        if b == 0x7E:
            return lo if lo < 0x2000 else v
        return lo if lo < 0x2000 else None
    if b == 0x7F:
        return v
    return None


def cmd_flags(asmdir, rom=None, cdls=()):
    ins = load_asm(asmdir)
    c = None
    if rom:
        c, _ = load_cdl(rom, cdls)
    writes, live_writes, tests = {}, {}, {}
    for i, (a, mn, op, n, m8) in enumerate(ins):
        base = op.split(",")[0]
        if not base.startswith("$") or op.startswith("#"):
            continue
        if re.match(r"\$[0-9A-F]{2},X$", op):  # object field: dp,X (X = object base); key 0x1000000+offset
            v = 0x1000000 + int(op[1:3], 16)
            fld = True
        else:
            v = norm(ram_of(base))
            fld = False
        if v is None:
            continue
        w = 1 if m8 else 2
        if mn in WRITES or (mn in ("STX", "STY")):
            for k in range(w if mn not in ("STX", "STY") else 2):
                writes.setdefault(v + k, []).append(a)
                if c is not None and c[off(a)] & 1:
                    live_writes[v + k] = 1
        if mn in TESTS and ("," not in op or fld) and (c is None or c[off(a)] & 1):  # with logs: tests that ran
            nxt = ins[i + 1][1] if i + 1 < len(ins) else ""
            nx2 = ins[i + 2][1] if i + 2 < len(ins) else ""
            if nxt in BRANCH or (nx2 in BRANCH and ins[i + 1][1] in ("AND", "CMP", "BIT", "ORA", "EOR")):
                tests.setdefault(v, []).append(a)
    print("# addr   tests  first-test   (writes: none / only from never-run code)")
    n = 0
    for v in sorted(tests):
        if v in writes and (c is None or v in live_writes):
            continue
        if v + 1 in writes and v - 1 in writes:
            pass
        kind = "none" if v not in writes else "dead-only " + " ".join("%06X" % x for x in writes[v][:4])
        if v not in writes and (v - 1 in writes):  # high byte of a 16-bit write
            continue
        n += 1
        name = f"obj+{v & 0xFF:02X}" if v >= 0x1000000 else f"{v:06X}"
        print(f"{name:7} {len(tests[v]):3}  {' '.join('%06X' % x for x in tests[v][:5])}  writes: {kind}")
    print(f"# {n} candidates")


def cmd_cov(rom, cdls):
    c, used = load_cdl(rom, cdls)
    code = sum(1 for b in c if b & 1)
    data = sum(1 for b in c if b & 2)
    print(f"logs {len(used)}; code bytes {code}, data bytes {data}, of {len(rom)}")
    for p in used:
        print("  ", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "dead":
        cmd_dead(a[1], open(a[2], "rb").read(), a[3:])
    elif a[0] == "dead2":
        cmd_dead2(a[1], open(a[2], "rb").read(), a[3:])
    elif a[0] == "pads":
        cmd_pads(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == "flags":
        rom = None
        if "--rom" in a:
            k = a.index("--rom")
            rom = open(a[k + 1], "rb").read()
            a = a[:k] + a[k + 2 :]
        cmd_flags(a[1], rom, a[2:])
    elif a[0] == "show":  # show <asmdir> <addr> [lines]: listing from addr on
        n = int(a[3]) if len(a) > 3 else 40
        out, on = [], False
        for p in sorted(glob.glob(os.path.join(a[1], "bank_*.asm"))):
            for line in open(p):
                if not on and ("; $" + a[2].upper() + " ") in line:
                    on = True
                if on:
                    out.append(line.rstrip()[:64])
                    if len(out) >= n:
                        break
            if len(out) >= n:
                break
        print("\n".join(out))
    elif a[0] == "cov":
        cmd_cov(open(a[1], "rb").read(), a[2:])
