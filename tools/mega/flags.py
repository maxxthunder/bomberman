"""RAM bytes the code tests but never writes by address. Usage: flags.py listing.asm codemap.json [lo hi] [window]
Reads = tst/btst/cmp/cmpi or any source operand; writes = destination operands (move/clr/bset/bclr/bchg/add/sub/
or/and/eor/not/neg/scc/movem/addx...) of the given absolute RAM address, widened by the operand size. Addresses
loaded as a base (lea / move.l #, pea) count as "pointer" bases: every byte up to `window` (default $30) above one is
treated as written through the pointer. Only instructions in the code map (callgraph.py insns + gap runs) count.
With A6=1 in the environment, $x(a6) operands count as RAM $x too (the 8-player demo keeps a6 = $FF0000).
Prints the never-written ones with their read sites, split into "no base nearby" (real candidates) and the rest."""
import json, os, re, sys
L = sys.argv[1]; cm = json.load(open(sys.argv[2]))
lo, hi = (int(sys.argv[3], 16), int(sys.argv[4], 16)) if len(sys.argv) > 4 else (0x8000, 0xFFFF)
win = int(sys.argv[5], 16) if len(sys.argv) > 5 else 0x30
ins = {int(a, 16) for a in cm['insns']}
for a, b, k in cm.get('gapruns', []): ins.add(int(a, 16))   # run starts; the rest of each run is added below
runs = [(int(a, 16), int(b, 16)) for a, b, k in cm.get('gapruns', [])]
SZ = {'b': 1, 'w': 2, 'l': 4}
R = re.compile(r'\$([0-9a-f]{4})\.w|\$ff([0-9a-f]{4})\.l')
READ_ONLY = {'tst', 'btst', 'cmp', 'cmpi', 'cmpa', 'cmpm', 'pea', 'lea', 'jsr', 'jmp', 'chk'}
reads, writes, bases = {}, set(), set()
for line in open(L):
    p = line.split(None, 2)
    if len(p) < 2: continue
    a = int(p[0], 16)
    if a not in ins and not any(s <= a < e for s, e in runs): continue
    m = p[1]; op = p[2].strip() if len(p) > 2 else ''
    if os.environ.get('A6'): op = re.sub(r'(?<![\w$-])\$([0-9a-f]{1,4})\(a6\)', lambda q: '$%04x.w' % int(q.group(1), 16), op)
    base = m.split('.')[0]; sz = SZ.get(m.split('.')[1][0], 2) if '.' in m else 2
    ops = [o.strip() for o in re.split(r',\s*(?![^()]*\))', op)] if op else []
    for i, o in enumerate(ops):
        for mm in R.finditer(o):
            v = int(mm.group(1) or mm.group(2), 16)
            if not lo <= v <= hi: continue
            if '(' in o and not o.startswith('$'): continue
            is_dst = i == len(ops) - 1 and (len(ops) > 1 or base in ('clr', 'not', 'neg', 'negx', 'nbcd', 'tas') or base.startswith('s') and base not in ('sub', 'subq', 'subi', 'suba', 'swap'))
            if base in ('lea', 'pea') or (o.startswith('#')):
                bases.add(v); continue
            if base == 'movem' and i == len(ops) - 1: is_dst = True
            if base in READ_ONLY or not is_dst or base in ('btst',):
                reads.setdefault(v, []).append((a, line.split(None, 1)[1].strip()))
                if base in ('bset', 'bclr', 'bchg') and is_dst: pass
            if is_dst and base not in READ_ONLY:
                n = 4 * 16 if base == 'movem' else sz
                writes.update(range(v, v + n))
            if base in ('bset', 'bclr', 'bchg', 'addq', 'subq', 'add', 'sub', 'or', 'and', 'eor', 'ori', 'andi', 'eori', 'addi', 'subi') and is_dst:
                writes.update(range(v, v + sz))
cand = sorted(v for v in reads if v not in writes)
near = lambda v: [b for b in bases if 0 <= v - b < win]
print('tested addresses: %d, never written by address: %d' % (len(reads), len(cand)))
for tag, sel in (('NO BASE NEARBY', lambda v: not near(v)), ('inside a pointer base window', lambda v: near(v))):
    print('== ' + tag)
    for v in cand:
        if sel(v):
            print('%04X  bases %s  reads %s' % (v, ' '.join('%04X' % b for b in sorted(near(v))) or '-',
                                                 '; '.join('%06x %s' % r for r in reads[v][:4])))
