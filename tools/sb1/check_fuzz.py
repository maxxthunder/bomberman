"""Compare a fuzz.sh RES dump with password.py: python check_fuzz.py out.txt"""
import sys
from password import decode
toks = open(sys.argv[1]).read().split('RES ')[1].split()
r = dict(t.split(':') for t in toks if ':' in t)
bad = [c for c, v in r.items() if (None if v in 'XS' else int(v, 16)) != (None if not decode(c) else (decode(c)[0] - 1) * 8 + decode(c)[1] - 1)]
print(f"{len(r)} codes, {sum(v not in 'XS' for v in r.values())} accepted, special {[c for c, v in r.items() if v == 'S']}, mismatches {bad}")
