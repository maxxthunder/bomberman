"""Compare a fuzz.sh dump with password.py: python tools/pce93/check_fuzz.py out.txt us|jp|sp"""
import sys
from password import decode_vals

ver = sys.argv[2]
res = {}
for line in open(sys.argv[1]):
    if line.startswith("F "):
        for t in line.split()[1:]:
            c, v = t.split(":")
            res[c] = v
bad, acc = [], 0
for c, v in res.items():
    p = [int(c[i:i + 2], 16) for i in range(0, 16, 2)]
    d = decode_vals(p, ver)
    want = "X" if d is None else "A%02x%02x%02x%02x%02x%02x" % (d[0], d[1], d[2], d[3], d[5] & 3, (d[5] & 12) << 2 | d[4])
    acc += v != "X"
    if v != want:
        bad.append((c, v, want))
print(f"{ver}: {len(res)} distinct codes run, {acc} accepted by the game, {len(bad)} disagreements with password.py", bad[:5])
