"""Hidden-content sweep for the Game Boy Bomberman ROMs (shared by tools/gb1-gb3), on top of tools/sm83.py.

python tools/gbsweep.py dead  <rom.gb> <cdl> [<cdl> ...] [--min N] [--write-entries entries.txt]
    The ROM is traced from the vectors plus every executed code start in the CDLs (Mesen GB CDL: bit 0 code,
    bit 2 jump target, bit 3 sub entry; all files ORed). Each stretch of traced code that never ran is printed with its
    static references (CALL/JP/JR/RST sources, and 16-bit pointers to it anywhere in data), classed as
      cond  - reached by a branch or call from code that ran (the branch was never taken in the runs)
      dead  - reached only from other never-run code
      noref - no reference found (a pointer this scan can't see, or unreferenced)
    Then 'orphan' candidates: stretches the trace never reached that decode as at least --min instructions with no
    undefined opcode, end in RET/RETI/JP, follow a RET/JP, and CALL known code.
python tools/gbsweep.py flags <rom.gb> <cdl> [<cdl> ...]
    RAM ($C000-$DFFF, $FF80-$FFFE) read by LD A,(nn) / LDH A,(n) / LD HL,nn + a (HL) read, with no direct write
    anywhere: LD (nn),A, LDH (n),A, LD HL,nn (or LD H,n / LD L,n pairs) followed by a (HL) store or INC/DEC (HL), and not
    inside a range cleared by `LD HL,nn / LD BC,len` before a CALL (the games' fill / copy helpers). Also a raw byte
    scan for EA nn / E0 n stores outside the traced code. '*' marks reads that never ran. Candidates need a dynamic check
    (a write watch in Mesen): indexed writes through a computed HL are invisible here.
python tools/gbsweep.py pad <listing.asm> <pad addr> [...]
    Every read of a pad byte (given as $C2E1, $FFA1 ...) or of $FF00 itself that is tested within the next 8
    instructions against a constant (CP n, AND n with 2+ bits, XOR n), a table (CP (HL)), or a counter (INC/DEC) -
    the shapes a held combination or a typed sequence takes.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sm83 as S

BR = ("JR", "JP", "CALL", "RST")


def load(argv):
    mn, went, rest = 4, None, []
    i = 0
    while i < len(argv):
        if argv[i] == "--min":
            mn = int(argv[i + 1]); i += 2
        elif argv[i] == "--write-entries":
            went = argv[i + 1]; i += 2
        else:
            rest.append(argv[i]); i += 1
    rom = open(rest[0], "rb").read()
    cdl = S.load_cdl(rest[1:], len(rom))
    for i in range(len(rom) - 8):        # code bits on $FF / $00 fill (patched loops) are dropped
        if rom[i:i + 8] in (b"\xff" * 8,):
            for k in range(i, i + 8):
                cdl[k] &= 0xFE
    ents = S.cdl_entries(cdl)
    d = S.run(rom, ents)
    if went:
        open(went, "w").write("".join(f"{b:02X}:{a:04X}\n" for b, a in sorted(set(ents))))
    return rom, cdl, d, mn


def target(o, pc, txt, rom):
    """static branch target (rom offset) of the instruction at o, or None"""
    op = txt.split(" ")[0]
    if op not in BR or txt in ("JP (HL)",):
        return None
    m = re.search(r"\$([0-9A-F]{2,4})$", txt)
    if not m:
        return None
    t = int(m.group(1), 16)
    if t >= 0x8000:
        return None
    return t if t < 0x4000 else (o >> 14) * 0x4000 + (t - 0x4000) if o >= 0x4000 else None


def dead(argv):
    rom, cdl, d, mn = load(argv)
    code = d.code
    refs = {}
    for o, (pc, n, txt) in code.items():
        t = target(o, pc, txt, rom)
        if t is not None:
            refs.setdefault(t, []).append((o, txt.split(" ")[0]))
    ran = lambda o: cdl[o] & 1
    offs = sorted(code)
    runs, cur = [], []
    for o in offs:
        if ran(o):
            if cur: runs.append(cur); cur = []
            continue
        if cur and cur[-1] + code[cur[-1]][1] != o:
            runs.append(cur); cur = []
        cur.append(o)
    if cur: runs.append(cur)

    def ptrs(o):
        b, a = S.loc(o)
        w = bytes([a & 255, a >> 8])
        hits, i = [], rom.find(w)
        while i >= 0:
            if not cdl[i] & 1 and i not in code and (i < 0x4000 or i >> 14 == o >> 14 or o < 0x4000):
                hits.append(i)
            i = rom.find(w, i + 1)
        return hits

    tot = {"cond": 0, "dead": 0, "noref": 0}
    print("# never-executed code (traced)")
    for r in runs:
        first, last = r[0], r[-1] + code[r[-1]][1]
        inside = set(range(first, last))
        rs = [(s, k) for o in r for s, k in refs.get(o, []) if s not in inside]
        prev = next((q for q in range(first - 1, max(first - 4, -1), -1) if q in code and q + code[q][1] == first), None)
        pt = code[prev][2] if prev is not None else ""
        if prev is not None and (pt.split(" ")[0] not in ("RET", "RETI", "JP", "JR") or "," in pt or pt[:4] == "RET "):
            rs.append((prev, "fall"))            # falls through, or after a conditional RET / JP / JR
        cls = "cond" if any(ran(s) for s, _ in rs) else ("dead" if rs else "noref")
        pr = ptrs(first) if cls == "noref" else []
        tot[cls] += last - first
        b, a = S.loc(first)
        src = ", ".join(sorted({"%02X:%04X %s%s" % (*S.loc(s), k, "" if ran(s) else "*") for s, k in rs}))[:160]
        print(f"{cls:5} {b:02X}:{a:04X}-{(S.loc(last - 1)[1]):04X} {last - first:5} bytes {len(r):4} ins  from: {src or '-'}"
              + (f"  ptr@{','.join('%05X' % p for p in pr[:4])}" if pr else ""))
    print("# totals (bytes):", tot, file=sys.stderr)
    known = {S.loc(o) for o in code}
    print("# orphan code candidates (not reached by the trace)")
    o, no = 0, 0
    while o < len(rom):
        if o in code or cdl[o] & 3:
            o += 1; continue
        if not (o and (rom[o - 1] in (0xC9, 0xD9) or (o >= 3 and rom[o - 3] in (0xC3,)))):
            o += 1; continue
        b, pc = S.loc(o)
        j, n, good, calls = o, 0, False, 0
        while j < len(rom) and j not in code and n < 300 and (j >> 14) == (o >> 14):
            txt, sz, t, flow = S.decode(rom, j, pc + (j - o))
            if txt == "?" or rom[j] in (0xFF, 0x00) and n == 0:
                break
            if t is not None and txt.startswith(("CALL", "JP")) and ((0, t) in known or (b, t) in known):
                calls += 1
            n += 1; j += sz
            if txt in ("RET", "RETI") or txt.startswith("JP $") or txt == "JP (HL)":
                good = True; break
        if good and n >= mn and calls:
            no += 1
            pr = []
            w = bytes([pc & 255, pc >> 8]); k = rom.find(w)
            while k >= 0:
                if not cdl[k] & 1: pr.append(k)
                k = rom.find(w, k + 1)
            jr = [k for k in pr if k and rom[k - 1] in (0xCD, 0xC3)]
            print(f"orphan {b:02X}:{pc:04X} {j - o:4} bytes {n:3} ins  calls {calls}"
                  + (f"  call/jp@{','.join('%02X:%04X' % S.loc(k - 1) for k in jr[:4])}" if jr else "")
                  + (f"  ptr@{','.join('%05X' % k for k in pr[:4])}" if pr and not jr else ""))
            o = j
        else:
            o += 1
    print(f"# {no} orphan candidates", file=sys.stderr)


def ram(a):
    return 0xC000 <= a < 0xE000 or 0xFF80 <= a < 0xFFFF


def flags(argv):
    rom, cdl, d, _ = load(argv)
    reads, writes, cover = {}, set(), set()
    seq = sorted(d.code)
    hl = None                              # (value, valid) of HL from LD HL,nn / LD H,n + LD L,n on a straight path
    h = l = None
    pend = None                            # last LD HL,nn for a fill (LD BC,len then CALL)
    bc = None
    for o in seq:
        pc, n, t = d.code[o]
        op = rom[o]
        w = rom[o + 1] | rom[o + 2] << 8 if n == 3 else None
        if op == 0xEA and ram(w):
            writes.add(w)
        elif op == 0xE0:
            writes.add(0xFF00 | rom[o + 1])
        elif op == 0xFA and ram(w):
            reads.setdefault(w, []).append(o)
        elif op == 0xF0 and ram(0xFF00 | rom[o + 1]):
            reads.setdefault(0xFF00 | rom[o + 1], []).append(o)
        if op == 0x21:
            hl, h, l, pend = w, w >> 8, w & 255, w
        elif op == 0x26:
            h = rom[o + 1]; hl = (h << 8 | l) if l is not None else None
        elif op == 0x2E:
            l = rom[o + 1]; hl = (h << 8 | l) if h is not None else None
        elif op == 0x01:
            bc = w
        elif t.startswith("CALL") and pend is not None and bc is not None and bc < 0x2000:
            cover.update(range(pend, pend + bc)); pend = None
        if hl is not None and ram(hl):
            if t.startswith(("LD (HL)", "INC (HL)", "DEC (HL)", "SET", "RES")) and "(HL)" in t and not t.startswith("BIT") \
                    or t in ("LD (HL+),A", "LD (HL-),A"):
                writes.add(hl)
            elif re.match(r"(LD [ABCDEHL],\(HL\)|CP \(HL\)|AND \(HL\)|OR \(HL\)|XOR \(HL\)|BIT \d,\(HL\)|ADD A,\(HL\)|SUB \(HL\))", t):
                reads.setdefault(hl, []).append(o)
        if op in (0x22, 0x32, 0x23, 0x2B, 0x2A, 0x3A, 0x09, 0x19, 0x29, 0x39, 0xE1, 0xF8) or t.startswith(("LD H,", "LD L,")) and op not in (0x26, 0x2E) \
                or t.startswith(("CALL", "RST", "RET", "JP", "JR")):
            if op not in (0x26, 0x2E, 0x21):
                hl = h = l = None
    def raw(a):
        pat = [bytes([0xEA, a & 255, a >> 8])] + ([bytes([0xE0, a & 255])] if a >= 0xFF00 else [])
        hits = []
        for p in pat:
            i = rom.find(p)
            while i >= 0:
                if i not in d.code: hits.append(i)
                i = rom.find(p, i + 1)
        return hits
    for a in sorted(reads):
        if a in writes or a in cover:
            continue
        rs = reads[a]
        where = ", ".join("%02X:%04X%s" % (*S.loc(o), "" if cdl[o] & 1 else "*") for o in rs[:5])
        r = raw(a)
        print(f"${a:04X}\tnever set\treads {len(rs)}\t{where}" + ("\tuntraced stores at " + ", ".join("%02X:%04X" % S.loc(i) for i in r[:6]) if r else ""))


def pad(argv):
    lines = [l.rstrip("\n") for l in open(argv[0], encoding="utf-8") if re.match(r"^[0-9A-F]{2}:[0-9A-F]{4}  ", l)]
    code = [l for l in lines if not l[19:].startswith("db ")]
    pads = {a.upper().lstrip("$") for a in argv[1:]} | {"FF00"}
    rd = re.compile(r"\b(LD A,\(\$(%s)\)|LDH A,\(\$(%s)\)|LD A,\(\$FF00\+C\))" % ("|".join(pads), "|".join(pads)))
    tst = re.compile(r"\b(CP \$[0-9A-F]{2}|AND \$[0-9A-F]{2}|XOR \$[0-9A-F]{2}|CP \(HL\)|INC |DEC )")
    hits = 0
    for i, l in enumerate(code):
        op = l[19:].strip()
        if not rd.search(op):
            continue
        win = code[i + 1:i + 9]
        t = [w for w in win if tst.search(w[19:])]
        multi = [w for w in t if re.search(r"(AND|CP|XOR) \$([0-9A-F]{2})", w[19:]) and
                 bin(int(re.search(r"\$([0-9A-F]{2})", w[19:]).group(1), 16)).count("1") >= 2]
        tables = [w for w in t if "CP (HL)" in w]
        if multi or tables:
            hits += 1
            print(f"== {l[:7]}  {op}   [{'TABLE ' if tables else ''}{'COMBO' if multi else ''}]")
            for w in win:
                print("     " + w[:7] + "  " + w[19:].strip())
    print(hits, "hits", file=sys.stderr)


if __name__ == "__main__":
    {"dead": dead, "flags": flags, "pad": pad}[sys.argv[1]](sys.argv[2:])
