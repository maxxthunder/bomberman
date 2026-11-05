"""Join the static code map (callgraph.py) with routine coverage (cover.lua hits) into a dead-code listing.
Usage: dead.py rom codemap.json cand.txt hits.txt listing.asm [eu [classes.json]] > deadcode.txt
For every candidate that never ran: how the static pass found it (call/jump/imm/ref/table/vector, or gap = clean
code no reference reaches), who references it (instruction sites, and any long in the ROM equal to its address),
and its first instructions. `eu` adds the Europe address (USA - 6 from $7C4A, - 12 from $1E75A)."""
import json, re, sys
rom = open(sys.argv[1], 'rb').read(); cm = json.load(open(sys.argv[2]))
cand = [int(l, 16) for l in open(sys.argv[3]) if l.strip()]
hits = {int(l.split()[0], 16) for l in open(sys.argv[4]) if l.strip()}
L = {}; order = []
for l in open(sys.argv[5]):
    p = l.split(None, 1)
    if len(p) == 2: a = int(p[0], 16); L[a] = p[1].rstrip(); order.append(a)
idx = {a: i for i, a in enumerate(order)}
eu = len(sys.argv) > 6 and sys.argv[6] == 'eu'
cls = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else {}
kinds = {int(a, 16): k for a, k in cm['entries'].items()}
refs = {int(a, 16): v for a, v in cm['refs'].items()}
gap = {int(a, 16): (int(b, 16), k) for a, b, k in cm['gapruns']}
dead = [a for a in cand if a not in hits]
print('candidates %d, ran %d, never ran %d' % (len(cand), len(cand) - len(dead), len(dead)))
if cls:
    from collections import Counter
    print('classes: ' + ', '.join('%s %d' % kv for kv in Counter(cls.get('%x' % a, '?') for a in dead).most_common()))
for a in dead:
    k = ','.join(kinds.get(a, ['gap']))
    longs = [m.start() for m in re.finditer(re.escape(a.to_bytes(4, 'big')), rom)][:4]
    e = '' if not eu else '  EU %06X' % (a if a < 0x7C4A else a - 6 if a < 0x1E75A else a - 12)
    print('\n%06X%s  %s [%s]  refs %s  longs %s' % (a, e, cls.get('%x' % a, ''), k, ' '.join(refs.get(a, [])[:6]) or '-', ' '.join('%X' % x for x in longs) or '-'))
    i = idx.get(a)
    if i is None: continue
    for b in order[i:i + 8]: print('    %06x  %s' % (b, L[b]))
