"""Dead-code sweep for the NES Bomberman carts (nes1, nes2): what code exists but never ran in any Mesen run.

Usage: python tools/nes1/deadcode.py <rom.nes> <cdlhex> [<cdlhex> ...] [--far C852] [--min N] [--write-entries entries.txt]

- <cdlhex>: lib.lua cdl_dump() files (hex of Mesen's PRG CDL; bit 0 code, bit 1 data, bit 2 jump target, bit 3 sub
  entry); all are ORed.
- The PRG is traced (tools/m6502.py) from the vectors plus every executed code start, so branches and calls out of
  executed code into code that never ran are followed. Each never-executed stretch of traced code is printed with
  its static references (JSR/JMP/branch sources, far calls, and 16-bit pointers to it in data), classed as:
    cond   - referenced from executed code (a branch or call that was never taken in the runs)
    dead   - referenced only from other never-executed code
    noref  - no reference found (entered from a pointer this scan can't see, or unreferenced)
- Orphans: stretches the trace never reached that still decode as code (>= --min instructions, no undefined
  opcodes, ending in RTS/RTI/JMP, with a JSR/JMP into known code).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import m6502 as M

args = sys.argv[1:]
mn, wents, far = 4, None, list(M.FAR)
if "--min" in args:
    k = args.index("--min"); mn = int(args[k + 1]); del args[k:k + 2]
if "--write-entries" in args:
    k = args.index("--write-entries"); wents = args[k + 1]; del args[k:k + 2]
rom = M.prg(args[0])
N, NB = len(rom), len(rom) // M.BANK
cdl = M.read_cdl(args[1:], N)
ent = M.cdl_entries(cdl, NB)
d = M.run(rom, ent, far)
if wents:
    open(wents, "w", newline="\n").write("".join(f"{b:02X}:{a:04X}\n" for b, a in sorted(set(ent))))
code = d.code
ran = lambda o: cdl[o] & 1
base = lambda o: d.base(o // M.BANK) | o % M.BANK


def tgt_offs(o, pc, tgt):
    """rom offsets a target address can mean from source o: same bank if switchable or fixed region, else every bank."""
    bank = o // M.BANK
    if tgt >= 0xC000 or NB == 1:
        r = d.off(tgt, bank)
        return [r] if r is not None else []
    if tgt >= 0x8000:
        return [d.off(tgt, bank)] if bank != NB - 1 else [b * M.BANK + (tgt & 0x3FFF) for b in range(NB - 1)]
    return []


refs = {}
for o, (pc, n, t) in code.items():
    op, *rest = t.split(" ", 1)
    a = rest[0] if rest else ""
    tg = []
    if op == ".far":
        b, x = a.split(":"); tg = [int(b[1:], 16) * M.BANK + (int(x[1:], 16) & 0x3FFF)]
    elif op in ("JSR", "JMP") and a.startswith("$") and len(a) == 5:
        tg = tgt_offs(o, pc, int(a[1:], 16))
    elif op[0] == "B" and op not in ("BIT", "BRK") and a.startswith("$"):
        tg = tgt_offs(o, pc, int(a[1:5], 16))
    for c in tg:
        if c is not None:
            refs.setdefault(c, []).append((o, op))

runs, cur = [], []
for o in sorted(code):
    if code[o][2].startswith(".far"):     # inline far-call operands: data, not code
        continue
    if ran(o):
        if cur: runs.append(cur); cur = []
        continue
    if cur and code[cur[-1]][1] + cur[-1] != o:
        runs.append(cur); cur = []
    cur.append(o)
if cur: runs.append(cur)
codebanks = {i // M.BANK for i in range(N) if cdl[i] & 1}


def ptr_refs(o):
    w = bytes([base(o) & 255, base(o) >> 8])
    hits, i = [], rom.find(w)
    while i >= 0:
        if not cdl[i] & 1 and i not in code: hits.append(i)
        i = rom.find(w, i + 1)
    return hits


tot = {"cond": 0, "dead": 0, "noref": 0}
print("# never-executed code (traced)")
for r in runs:
    first, last = r[0], r[-1] + code[r[-1]][1]
    inside = set(range(first, last))
    rs = [(s, k) for o in r for s, k in refs.get(o, []) if s not in inside]
    prev = next((q for q in range(first - 1, max(first - 4, -1), -1) if q in code and q + code[q][1] == first), None)
    if prev is not None and code[prev][2].split(" ")[0] not in ("RTS", "RTI", "JMP", "BRK"):
        rs.append((prev, "fall"))
    cls = "cond" if any(ran(s) for s, _ in rs) else ("dead" if rs else "noref")
    pr = ptr_refs(first) if cls == "noref" else []
    tot[cls] += last - first
    src = ", ".join(sorted({f"{s // M.BANK:02X}:{code[s][0]:04X} {k}{'' if ran(s) else '*'}" for s, k in rs}))[:160]
    print(f"{cls:5} {first // M.BANK:02X}:{code[first][0]:04X}-{(code[r[-1]][0] + code[r[-1]][1] - 1) & 0xFFFF:04X} {last - first:5} bytes  "
          f"{len(r):3} ins  from: {src or '-'}{'  ptr@' + ','.join('%05X' % p for p in pr[:4]) if pr else ''}")
print("# totals (bytes):", tot, "executed:", sum(1 for b in cdl if b & 1), file=sys.stderr)

known = {pc for pc, n, t in code.values()}
print("# orphan code candidates (not reached by the trace)")
o, norph = 0, 0
while o < N:
    if o in code or cdl[o] & 3 or o // M.BANK not in codebanks:
        o += 1; continue
    pc = base(o)
    prev_end = rom[o - 1] in (0x60, 0x40) or (o >= 3 and rom[o - 3] == 0x4C)
    lo = o - o % M.BANK
    w = bytes([0x20, pc & 255, pc >> 8])
    if not prev_end and rom.find(w, lo, lo + M.BANK) < 0 and rom.find(w, (NB - 1) * M.BANK) < 0:
        o += 1; continue
    j, n, good, calls = o, 0, False, 0
    while j < N and j not in code and n < 400 and j // M.BANK == o // M.BANK:
        name, mode = M.OPS[rom[j]]
        if name in ("?", "BRK"): break
        if name in ("JSR", "JMP") and mode == "abs" and j + 2 < N and (rom[j + 1] | rom[j + 2] << 8) in known: calls += 1
        n += 1; j += M.SIZE[mode]
        if name in ("RTS", "RTI", "JMP"):
            good = True; break
    if good and n >= mn and calls:
        norph += 1
        w2 = bytes([pc & 255, pc >> 8]); pr, k = [], rom.find(w2)
        while k >= 0:
            if not cdl[k] & 1: pr.append(k)
            k = rom.find(w2, k + 1)
        jr = [k for k in pr if k and rom[k - 1] in (0x20, 0x4C)]
        print(f"orphan {o // M.BANK:02X}:{pc:04X} {j - o:4} bytes {n:3} ins  calls {calls}"
              + (f"  jsr/jmp@{','.join('%05X' % k for k in jr[:4])}" if jr else "") + (f"  ptr@{','.join('%05X' % k for k in pr[:4])}" if pr and not jr else ""))
        o = j
    else:
        o += 1
print(f"# {norph} orphan candidates", file=sys.stderr)
