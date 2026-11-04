"""Grow disasm/sb4/entries.txt from Mesen CDL dumps (HiROM). Mesen marks every executed byte but not
instruction starts, so: disassemble, then add the first CDL-code byte of every run the listing left as
db (m/x from its CDL flags), and repeat until nothing new.
Usage: python tools/sb4/cdl_fill.py <rom> <outdir> cdl.hex [...]"""
import os, re, subprocess, sys
rom, out, cdls = sys.argv[1], sys.argv[2], sys.argv[3:]
c = bytearray(len(open(rom, 'rb').read()))
for p in cdls:
    for i, b in enumerate(bytes.fromhex(open(p).read().strip())):
        c[i] |= b
ent = os.path.join(out, 'entries.txt')
have = {}
if os.path.exists(ent):
    for l in open(ent):
        f = l.split('#')[0].split()
        if f: have[int(f[0], 16)] = (f[1], f[2])
dis = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'disasm.py')
for rnd in range(30):
    with open(ent, 'w') as f:
        for a in sorted(have): f.write(f"{a:06X} {have[a][0]} {have[a][1]}\n")
    print(subprocess.run([sys.executable, dis, rom, out], capture_output=True, text=True).stdout.strip())
    covered = bytearray(len(c))
    for fn in os.listdir(out):
        if fn.endswith('.asm'):
            for l in open(os.path.join(out, fn)):
                m = re.search(r'; \$([0-9A-F]{6})  ((?:[0-9A-F]{2} ?)+)', l)
                if m and not l.lstrip().startswith('db'):
                    o = int(m[1], 16) - 0xC00000
                    for k in range(len(m[2].split())): covered[o + k] = 1
    new = 0
    for i in range(len(c)):
        if c[i] & 1 and not covered[i] and (i == 0 or not (c[i - 1] & 1) or covered[i - 1]):
            a = 0xC00000 + i
            if a not in have:
                have[a] = ('1' if c[i] & 0x20 else '0', '1' if c[i] & 0x10 else '0'); new += 1
    print('round', rnd, 'new entries', new)
    if not new: break
