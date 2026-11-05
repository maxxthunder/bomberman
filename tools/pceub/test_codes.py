"""Type codes in Mesen with real pad input (test_codes.lua, one Mesen per code) and check $2849-$284D against
password.py. Usage: python test_codes.py <scratch dir> CODE [CODE...]
BOMSOUND+CODE types both. Screenshots land in <scratch dir>/<code>/shot.png. MESEN set, see run.sh."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import password as P

d, codes = sys.argv[1], sys.argv[2:]
here = os.path.dirname(os.path.abspath(__file__))


def run(code):
    cd = os.path.join(d, code.replace("+", "_"))
    os.makedirs(cd, exist_ok=True)
    s = os.path.join(cd, "tc.lua")
    open(s, "w").write('CODE="%s" SHOTAT=%s\n' % (code, os.environ.get("SHOTAT", "250")) + open(os.path.join(here, "test_codes.lua")).read())
    out = subprocess.run(["sh", os.path.join(here, "run.sh"), s], capture_output=True, text=True).stdout
    return next((l for l in out.splitlines() if l.startswith("CODE ")), "CODE %s none" % code)


bad = 0
with ThreadPoolExecutor(2) as ex:
    for line in ex.map(run, codes):
        p = line.split()
        f = P.decode(p[1].split("+")[-1])
        ok = len(p) == 5 and (p[2] == "valid=1") == bool(f)
        if ok and f and "BOMSOUND" not in p[1]:
            ok = list(map(int, p[4][4:].split(","))) == [f["round"] - 1, f["stage"] - 1, f["bombs"], f["fire"], f["speed"]]
        bad += not ok
        print("ok " if ok else "BAD", line)
print(len(codes), "codes,", bad, "bad")
