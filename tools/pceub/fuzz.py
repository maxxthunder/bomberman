"""Build the decoder fuzz set, run fuzz.lua in Mesen and compare with password.py.
Usage: python fuzz.py <scratch dir>   (MESEN set; see run.sh)"""
import os, random, subprocess, sys
import password as P

rnd = random.Random(90)
codes = []
for r in range(1, 9):                       # every state, random flip, random shift that fits (0-7)
    for s in range(1, 9):
        for bo in range(1, 11):
            for fi in range(1, 16):
                for d in (0, 1):
                    st = dict(round=r, stage=s, bombs=bo, fire=fi, speed=d)
                    ok = [c for sh in range(8) for c in [P.encode(**st, flip=rnd.randrange(8), shift=sh)] if c]
                    codes.append(rnd.choice(ok))
L = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
codes += ["".join(rnd.choice(P.ROWS[k // 2]) for k in range(8)) for _ in range(10000)]  # random in-row letters
base = P.encode(3, 5, 4, 2, 1, flip=5, shift=1)
codes += [base[:i] + c + base[i + 1:] for i in range(8) for c in L]                      # every letter everywhere
for tail in (base, P.encode(8, 8, 10, 15, 1), P.encode(1, 1)):                          # every byte 0
    codes += [a + b + tail[2:] for a in P.ROWS[0] for b in P.ROWS[0]]
codes += [P.BOMSOUND]
d = sys.argv[1]
os.makedirs(d, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(d, "fz.lua"), "w").write('CODES="%s"\n' % "".join(codes) + open(os.path.join(here, "fuzz.lua")).read())
out = subprocess.run(["sh", os.path.join(here, "run.sh"), os.path.join(d, "fz.lua")], capture_output=True, text=True).stdout
res = next(l for l in out.splitlines() if l.startswith("RES ")).split()[1:]
assert len(res) == len(codes), (len(res), len(codes))
bad = valid = 0
for c, r in zip(codes, res):
    f = P.decode(c)
    want = "X" if f is None else ",".join("%x" % v for v in (f["round"] - 1, f["stage"] - 1, f["bombs"], f["fire"], f["speed"]))
    valid += r != "X"
    if r != want:
        bad += 1
        print("MISMATCH", c, r, want)
print(f"{len(codes)} codes, {valid} accepted by the game, {bad} mismatches")
