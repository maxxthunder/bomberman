"""Shift-tolerant ROM diff: lists 16-byte-aligned runs of ROM X whose bytes occur nowhere in ROM Y.
python romdiff.py X.sfc Y.sfc [minrun=32]"""
import sys
X, Y = open(sys.argv[1], 'rb').read(), open(sys.argv[2], 'rb').read()
minrun = int(sys.argv[3]) if len(sys.argv) > 3 else 32
K = 16
have = {Y[i:i + K] for i in range(len(Y) - K)}
runs, start = [], None
for o in range(0, len(X), K):
    miss = X[o:o + K] not in have and len(set(X[o:o + K])) > 1
    if miss and start is None: start = o
    if not miss and start is not None: runs.append((start, o)); start = None
if start is not None: runs.append((start, len(X)))
runs = [r for r in runs if r[1] - r[0] >= minrun]
print(f"{len(runs)} runs, {sum(e - s for s, e in runs)} bytes")
for s, e in runs: print(f"  ${0xC00000 + s:06X}-${0xC00000 + e - 1:06X} ({e - s} bytes)")
