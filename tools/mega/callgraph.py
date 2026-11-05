"""Static 68000 code map of a Genesis ROM: recursive descent from the vectors, every immediate/absolute operand that
points into the code range, and long-pointer tables (runs of longs that point at clean code) found anywhere outside
the code. Usage: callgraph.py rom.md [code_end_hex [seeds.txt]] > out.json  (default end $40000; seeds = hex addresses known
to be code, e.g. cover.lua hits, added as 'ran' entries)

Output (json): gapruns [[start, end, insns]] (clean code runs in the gaps, never reached statically); entries {addr: [kind, ...]} where kind is vector/call/jump/imm/table:<table addr>/data:<addr>;
blocks [[start, end]] (end exclusive) of decoded instructions; calls {caller_entry: [callee...]}; refs {target: [site]}.
"""
import sys, json, re, capstone

BAD = re.compile(r'\(\[|\{|\*[248]|^(bf|cas|callm|rtm|rtd|pack|unpk|chk2|cmp2|trap[a-z]|extb|move16|cinv|cpush|pflush|ptest|pmove|f[a-z]+)|\.l\s.*d\d:d\d|mul[su]\.l|div[su]\.l|divsl|divul|bkpt|illegal|moves|movec|link\.l')
BR = {'bra', 'bsr', 'jmp', 'jsr'} | {'b' + c for c in 'hi ls cc cs ne eq vc vs pl mi ge lt gt le hs lo'.split()}
END = {'rts', 'rte', 'rtr', 'bra', 'jmp', 'illegal', 'stop'}


class Code:
    def __init__(self, rom, end):
        self.d = rom; self.end = end; self.cache = {}
        self.md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)

    def ins(self, a):
        if a not in self.cache:
            r = None
            for i in self.md.disasm(self.d[a:a + 16], a):
                r = (i.size, i.mnemonic, i.op_str); break
            self.cache[a] = r
        return self.cache[a]

    def ok(self, a):
        r = self.ins(a)
        return r is not None and not BAD.search(r[1] + ' ' + r[2]) and not r[1].startswith('dc')


def nums(op):
    """Absolute values named in an operand string: ($x.l, $x.w, #$x, plain $x for branches)."""
    out = []
    for m in re.finditer(r'(#)?(-)?\$([0-9a-f]+)(\.[wl])?(\(pc|\(a)?', op):
        imm, neg, v, sz, pc = m.groups(); v = int(v, 16)
        if neg or pc == '(a': continue
        pc = bool(pc)
        if sz == '.w' and v >= 0x8000: v |= 0xFF0000
        out.append((v, bool(imm), bool(pc), sz))
    return out


def analyse(rom, end=0x40000, seeds=()):
    c = Code(rom, end); entries = {}; code = {}; refs = {}; work = []

    def add(a, kind):
        if a % 2 or not 0x200 <= a < end: return
        new = a not in entries
        entries.setdefault(a, set()).add(kind)
        if new: work.append(a)

    def clean(a, n=400):
        """Does code reached from a (bounded) decode as plain 68000? Used to accept pointer candidates."""
        seen = set(); st = [a]
        while st and len(seen) < n:
            p = st.pop()
            while p not in seen:
                if p in code: break
                if not (0x200 <= p < end) or not c.ok(p): return False
                seen.add(p); sz, m, op = c.ins(p); base = m.split('.')[0]
                for v, imm, pc, s in nums(op):
                    if base in BR and not imm and v < end: st.append(v)
                if base.startswith('db'): st.append(nums(op)[-1][0])
                if base in END: break
                p += sz
        return True

    for i in range(1, 64):
        v = int.from_bytes(rom[4 * i:4 * i + 4], 'big')
        if 0x200 <= v < end: add(v, 'vector')
    for v in seeds: add(v, 'ran')
    tables = set(); datarefs = {}
    while True:
        while work:
            a = work.pop()
            while a not in code and 0x200 <= a < end and c.ok(a):
                sz, m, op = c.ins(a); code[a] = sz; base = m.split('.')[0]
                for v, imm, pc, s in nums(op):
                    if v >= end: continue
                    if base in BR and not imm: add(v, 'call' if base in ('bsr', 'jsr') else 'jump')
                    elif base.startswith('db') and not imm: add(v, 'jump')
                    else:
                        refs.setdefault(v, set()).add(a)
                        if v >= 0x200: datarefs[v] = datarefs.get(v, False) or imm
                if base in END: break
                a += sz
        # pointer candidates: referenced values that land on clean code become entries; others are scanned as tables
        grew = False
        for v in sorted(datarefs):
            if v in code or v in entries or v % 2: continue
            if v in tables: continue
            tables.add(v)
            first = int.from_bytes(rom[v:v + 4], 'big')
            is_tab = first % 2 == 0 and 0x200 <= first < end and clean(first)
            if not is_tab and clean(v):     # move.l #routine,... / pea (imm) or lea/pc-relative (ref) to clean code
                add(v, 'imm' if datarefs[v] else 'ref'); grew = True; continue
            # long-pointer table at v?
            p = v; n = 0
            while p + 4 <= len(rom):
                t = int.from_bytes(rom[p:p + 4], 'big')
                if t % 2 or not 0x200 <= t < end or not clean(t): break
                add(t, 'table:%x' % v); n += 1; p += 4; grew = True
        if not grew and not work: break
    # global scan of non-code longs for code pointers (only kept if aligned and the target decodes cleanly)
    covered = set()
    for a, sz in code.items(): covered.update(range(a, a + sz))
    loose = {}
    for p in range(0, len(rom) - 3, 2):
        if p in covered or p < 0x200: continue
        t = int.from_bytes(rom[p:p + 4], 'big')
        if 0x200 <= t < end and t % 2 == 0 and t not in entries and c.ok(t) and clean(t, 60):
            loose.setdefault(t, []).append(p)
    blocks = []; cur = None
    for a in sorted(code):
        if cur and cur[1] == a: cur[1] = a + code[a]
        else: cur = [a, a + code[a]]; blocks.append(cur)
    # gaps inside the code area: linear runs that decode as clean code ending in rts/rte/bra/jmp (dead-code candidates)
    runs = []
    last = max(code) + code[max(code)]
    for (a, e), (n, _) in zip(blocks, blocks[1:]):
        p = e
        while p < n:
            q = p; k = 0; ok = True
            while q < n and c.ok(q):
                sz, m, op = c.ins(q); q += sz; k += 1
                if m.split('.')[0] in END: break
            else:
                ok = False
            if ok and k >= 3 and q <= n: runs.append((p, q, k))
            p = q if q > p else p + 2
    return c, entries, code, refs, blocks, loose, runs


if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read(); end = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x40000
    seeds = [int(l.split()[0], 16) for l in open(sys.argv[3]) if l.strip()] if len(sys.argv) > 3 else []
    c, entries, code, refs, blocks, loose, runs = analyse(rom, end, seeds)
    insn_starts = sorted(code)
    json.dump({'entries': {'%x' % a: sorted(k) for a, k in sorted(entries.items())},
               'blocks': [['%x' % a, '%x' % b] for a, b in blocks],
               'insns': ['%x' % a for a in insn_starts],
               'refs': {'%x' % a: ['%x' % s for s in sorted(v)] for a, v in sorted(refs.items()) if a in entries},
               'gapruns': [['%x' % a, '%x' % b, k] for a, b, k in runs],
               'loose': {'%x' % a: ['%x' % s for s in v[:8]] for a, v in sorted(loose.items())}}, sys.stdout, indent=0)
