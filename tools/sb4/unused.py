"""Unused-data sweep: union of Mesen CDL dumps (cdl.hex from cover.lua runs), then list ROM runs that no run
read as code or data (>= MIN bytes, filler like all-$00/$FF skipped) and render each as a 4bpp grey tile sheet.
Usage: python unused.py <rom> <outdir> cdl.hex [...]   (MIN=512 by default, env MIN)"""
import os, sys, subprocess
rom = open(sys.argv[1], 'rb').read(); out = sys.argv[2]; MIN = int(os.environ.get('MIN', 512))
c = bytearray(len(rom))
for p in sys.argv[3:]:
    for i, b in enumerate(bytes.fromhex(open(p).read().strip())): c[i] |= b
print(f'{len(sys.argv) - 3} logs; read as code {sum(1 for b in c if b & 1)}, data {sum(1 for b in c if b & 2)}, unread {sum(1 for b in c if not b & 3)} of {len(rom)}')
os.makedirs(out, exist_ok=True); i = 0; here = os.path.dirname(os.path.abspath(__file__))
while i < len(rom):
    if c[i] & 3: i += 1; continue
    j = i
    while j < len(rom) and not c[j] & 3: j += 1
    blk = rom[i:j]
    if j - i >= MIN and len(set(blk)) > 2:
        name = f'{0xC00000 + i:06X}-{0xC00000 + j - 1:06X}'
        print(name, j - i, 'distinct bytes', len(set(blk)))
        n = min((j - i) // 32, 512)
        subprocess.run([sys.executable, os.path.join(here, 'tilesheet.py'), sys.argv[1], f'{i:x}', str(n), '4', os.path.join(out, name + '.png')])
    i = j
