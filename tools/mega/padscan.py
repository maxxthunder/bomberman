"""List every instruction that touches the pad RAM, with the next few instructions, from a disassembly listing.
Usage: padscan.py listing.asm ranges... (hex lo-hi, RAM short addresses) > padreads.txt
Each hit is tagged with what follows it: the bit tests / compares / masks (so button codes and sequence checks stand
out: a sequence check compares the pad against a value loaded from a table with a moving index)."""
import re, sys
lines = [l.rstrip('\n') for l in open(sys.argv[1])]
rng = [tuple(int(x, 16) for x in r.split('-')) for r in sys.argv[2:]]
addr = re.compile(r'\$([0-9a-f]{4})\.w')
def hit(op):
    for m in addr.finditer(op):
        v = int(m.group(1), 16)
        if any(lo <= v <= hi for lo, hi in rng): return v
for i, l in enumerate(lines):
    p = l.split(None, 2)
    if len(p) < 3: continue
    v = hit(p[2])
    if v is None: continue
    ctx = lines[i:i + 6]
    tags = sorted({t for c in ctx[1:] for t in re.findall(r'(btst\S*\s+#\$?\w+|cmpi?\S*\s+#\$?\w+|andi\S*\s+#\$?\w+|cmp\S*\s+\(a\d[^,]*)', c)})
    print('%s  [%04X]  %s' % (p[0], v, '; '.join(tags)))
    for c in ctx: print('    ' + c)
