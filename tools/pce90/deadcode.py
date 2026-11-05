"""Dead-code sweep for the PC Engine Bomberman cards: what code exists but never ran in any Mesen run.

Usage: python tools/pce90/deadcode.py <rom.pce> "<MAPS line>" <cdl> [<cdl> ...] [--entries extra.txt] [--min N]
                                      [--write-entries entries.txt]

- <cdl>: Mesen .cdl files (CDLv2 header + 1 byte per ROM byte; bit 0 code, bit 1 data) or CDLHEX dumps; all ORed.
- MAPS: `bb:p` tokens from lib.lua's maps_dump() (which logical page each ROM bank was seen at).
- The ROM is traced from the vectors plus every executed code run (huc6280.py), so branches and calls out of
  executed code into code that never ran are followed. Each never-executed stretch of traced code is printed with
  its static references (JSR/JMP/branch sources, `JMP (tab,X)` tables and 16-bit pointers seen anywhere in the
  bank's data), classed as:
    cond   - referenced from executed code (a branch or call that was never taken in the runs)
    dead   - referenced only from other never-executed code
    noref  - no reference found (entered from a pointer this scan can't see, or unreferenced)
- Orphans: stretches the trace never reached that still decode as code (>= --min instructions, no undefined
  opcodes, ending in RTS/RTI/JMP, with a JSR/JMP into known code) are listed as 'orphan' candidates.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import huc6280 as H

args = sys.argv[1:]
extra, mn = [], 4
if "--entries" in args:
    k = args.index("--entries"); extra = H.read_entries(args[k + 1]); del args[k:k + 2]
wents = None
if "--write-entries" in args:
    k = args.index("--write-entries"); wents = args[k + 1]; del args[k:k + 2]
if "--min" in args:
    k = args.index("--min"); mn = int(args[k + 1]); del args[k:k + 2]
rom = open(args[0], "rb").read()
N = len(rom)
pages = {}
for t in args[1].split():
    b, p = t.split(":"); pages.setdefault(int(b, 16), []).append(int(p))
cdl = bytearray(N)
for p in args[2:]:
    raw = open(p, "rb").read()
    if raw[:5] != b"CDLv2":
        raw = bytes.fromhex(raw.decode().split()[-1])
    raw = raw[-N:]
    for i, b in enumerate(raw):
        cdl[i] |= b
for i in range(N - 8):           # fuzz/patch runs leave code bits on $FF fill: drop them
    if rom[i:i + 8] == bytes([0xFF]) * 8:
        for k in range(i, i + 8):
            cdl[k] &= 0xFE
ent = list(extra)
for i in range(N):
    if cdl[i] & 1 and (cdl[i] & 0x0C or not (i % 0x2000 and cdl[i - 1] & 1)):  # run start, jump target or sub entry
        for p in pages.get(i >> 13, []):
            ent.append((i >> 13, p << 13 | i & 0x1FFF))
d = H.run(rom, ent)
if wents:                                        # entries.txt for huc6280.py (all executed code starts)
    open(wents, "w").write("".join(f"{b:02X}:{a:04X}" + chr(10) for b, a in sorted(set(ent))))
code = d.code                                    # off -> (pc, size, text)
page_of = {o: pc >> 13 for o, (pc, n, t) in code.items()}
ran = lambda o: cdl[o] & 1

# static references: target rom offset -> list of (source offset, kind)
refs = {}
for o, (pc, n, t) in code.items():
    op, *rest = t.split(" ", 1)
    a = rest[0] if rest else ""
    tgt = None
    if op in ("JSR", "JMP") and a.startswith("$") and len(a) == 5:
        tgt = int(a[1:], 16)
    elif op in ("BRA", "BEQ", "BNE", "BCC", "BCS", "BPL", "BMI", "BVC", "BVS", "BSR") and a.startswith("$"):
        tgt = int(a[1:5], 16)
    elif op.startswith(("BBR", "BBS")):
        tgt = int(a.split(",")[1][1:], 16)
    if tgt is None:
        continue
    # same bank if the target is in the source's page, else any bank seen at that page
    bank = o >> 13
    if tgt >> 13 == pc >> 13:
        cand = [bank * 0x2000 + (tgt & 0x1FFF)]
    else:
        cand = [b * 0x2000 + (tgt & 0x1FFF) for b, ps in pages.items() if tgt >> 13 in ps]
    for c in cand:
        refs.setdefault(c, []).append((o, op))

# stretches of traced code that never ran
offs = sorted(code)
runs, cur = [], []
for o in offs:
    if ran(o):
        if cur: runs.append(cur); cur = []
        continue
    if cur and code[cur[-1]][1] + cur[-1] != o:
        runs.append(cur); cur = []
    cur.append(o)
if cur: runs.append(cur)


codebanks = {i >> 13 for i in range(N) if cdl[i] & 1}


def ptr_refs(o):
    pc = page_of.get(o)
    if pc is None: return []
    lo = (pc << 13 | o & 0x1FFF)
    w = bytes([lo & 255, lo >> 8])
    bank = o >> 13
    hits, i = [], rom.find(w)
    while i >= 0:
        if not cdl[i] & 1 and i not in code and i >> 13 in codebanks: hits.append(i)
        i = rom.find(w, i + 1)
    return hits


tot = {"cond": 0, "dead": 0, "noref": 0}
print("# never-executed code (traced)")
for r in runs:
    first, last = r[0], r[-1] + code[r[-1]][1]
    inside = set(range(first, last))
    rs = [(s, k) for o in r for s, k in refs.get(o, []) if s not in inside]
    prev = next((q for q in range(first - 1, max(first - 8, -1), -1) if q in code and q + code[q][1] == first), None)
    if prev is not None and code[prev][2].split(" ")[0] not in ("RTS", "RTI", "JMP", "BRA", "BRK"):
        rs.append((prev, "fall"))
    cls = "cond" if any(ran(s) for s, _ in rs) else ("dead" if rs else "noref")
    pr = ptr_refs(first) if cls == "noref" else []
    tot[cls] += last - first
    pc = code[first][0]
    src = ", ".join(sorted({f"{s >> 13:02X}:{code[s][0]:04X} {k}{'' if ran(s) else '*'}" for s, k in rs}))[:160]
    print(f"{cls:5} {first >> 13:02X}:{pc:04X}-{(code[r[-1]][0] + code[r[-1]][1] - 1) & 0xFFFF:04X} {last - first:5} bytes  "
          f"{len(r):3} ins  from: {src or '-'}{'  ptr@' + ','.join('%05X' % p for p in pr[:4]) if pr else ''}")
print("# totals (bytes):", tot, file=sys.stderr)

# orphans: decode stretches outside the trace
known = {pc for pc, n, t in code.values()}
print("# orphan code candidates (not reached by the trace)")
o = 0
norph = 0
while o < N:
    if o in code or cdl[o] & 1:
        o += 1; continue
    pcs = pages.get(o >> 13)
    if not pcs:
        o += 1; continue
    pc = pcs[0] << 13 | o & 0x1FFF
    # a routine starts right after code that ends (RTS/RTI/JMP abs), or where a JSR/JMP in the bank points
    prev_end = o - 1 in code and code[o - 1][2] in ("RTS", "RTI") or rom[o - 1] in (0x60, 0x40) or \
        (o >= 3 and rom[o - 3] == 0x4C and (o - 3 in code or not cdl[o - 3] & 1))
    w = bytes([0x20, pc & 255, pc >> 8]); jw = bytes([0x4C, pc & 255, pc >> 8])
    if not prev_end and rom.find(w, o & ~0x1FFF, (o | 0x1FFF) + 1) < 0 and rom.find(jw, o & ~0x1FFF, (o | 0x1FFF) + 1) < 0:
        o += 1; continue
    j, n, good, calls = o, 0, False, 0
    while j < N and j not in code and n < 400 and (j >> 13) == (o >> 13):
        name, mode = H.OPS[rom[j]]
        if name in ("?", "BRK"): break
        sz = H.SIZE[mode]
        if name in ("JSR", "JMP") and mode == "abs":
            t = rom[j + 1] | rom[j + 2] << 8
            if t in known: calls += 1
        n += 1; j += sz
        if name in ("RTS", "RTI", "JMP"):
            good = True; break
    if good and n >= mn and calls:
        norph += 1
        w = bytes([pc & 255, pc >> 8]); pr, k = [], rom.find(w)
        while k >= 0:
            if k >> 13 in codebanks and not cdl[k] & 1: pr.append(k)
            k = rom.find(w, k + 1)
        jr = [k for k in pr if k and rom[k - 1] in (0x20, 0x4C)]   # JSR/JMP abs to it in untraced bytes
        print(f"orphan {o >> 13:02X}:{pc:04X} {j - o:4} bytes {n:3} ins  calls {calls}"
              + (f"  jsr/jmp@{','.join('%02X:%04X' % (k >> 13, k & 0x1FFF) for k in jr[:4])}" if jr else "")
              + (f"  ptr@{','.join('%05X' % k for k in pr[:4])}" if pr and not jr else ""))
        o = j
    else:
        o += 1
print(f"# {norph} orphan candidates", file=sys.stderr)
