"""Run the game's decoder on every y in [y0, y1) as bytes 1-3 with a fixed byte 0 (fuzz_all.lua, an in-ROM loop) and
compare with password.py. All 2^24 is y0=0 y1=1000000 (hours at ~750 codes/s per Mesen instance on a loaded machine).
Usage: python fuzz_all.py <us|jp> <scratch dir> [byte0 hex=10] [y0 hex=0] [y1 hex=30d40] [chunks=1] [parallel=4]"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import password as P

reg, d = sys.argv[1], sys.argv[2]
b0 = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x10
Y0 = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0
Y1 = int(sys.argv[5], 16) if len(sys.argv) > 5 else 200000
nch = int(sys.argv[6]) if len(sys.argv) > 6 else 1
par = int(sys.argv[7]) if len(sys.argv) > 7 else 4
here = os.path.dirname(os.path.abspath(__file__))


def code(y):
    b = [b0, y >> 16 & 255, y >> 8 & 255, y & 255]
    return "".join(P.ROWS[k][b[k] & 15] + P.ROWS[k][b[k] >> 4] for k in range(4))


def want(f):
    return ",".join("%x" % v for v in (f["round"] - 1, f["stage"] - 1, f["bombs"], f["fire"], f["speed"]))


def run(i):
    y0, y1 = Y0 + (Y1 - Y0) * i // nch, Y0 + (Y1 - Y0) * (i + 1) // nch
    cd = os.path.join(d, "c%02d" % i)
    os.makedirs(cd, exist_ok=True)
    s = os.path.join(cd, "fa.lua")
    open(s, "w").write("B0=%d Y0=%d Y1=%d\n" % (b0, y0, y1) + open(os.path.join(here, "fuzz_all.lua")).read())
    out = subprocess.run(["sh", os.path.join(here, "run.sh"), s, reg], capture_output=True, text=True).stdout
    open(os.path.join(cd, "out.txt"), "w").write(out)
    done = next(l for l in out.splitlines() if l.startswith("DONE ")).split()
    acc = dict(e.split(":") for e in next(l for l in out.splitlines() if l.startswith("ACC")).split()[1:])
    assert int(done[1]) + int(done[2]) == y1 - y0 and int(done[3]) == int(done[2]) == len(acc), done  # no ring overrun
    bad = 0
    for y in range(y0, y1):
        f = P.decode(code(y))
        got = acc.get("%x" % y)
        if (f and want(f)) != got and not (f is None and got is None):
            bad += 1
            if bad < 10:
                print("MISMATCH", code(y), got, f)
    return y1 - y0, len(acc), bad


with ThreadPoolExecutor(par) as ex:
    res = list(ex.map(run, range(nch)))
print("byte0 %02x, y %06x-%06x: %d codes, %d accepted by the game, %d mismatches" % (b0, Y0, Y1 - 1, *map(sum, zip(*res))))
