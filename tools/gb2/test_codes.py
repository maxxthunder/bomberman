"""Type codes in Mesen with real pad input (test_codes.lua, one Mesen per code, 2 at once) and check the RAM the
check writes against password.mjs. Usage: python tools/gb2/test_codes.py <jp|us> CODE [CODE...]  (or 'all')
Screenshots: $SCRATCH/gb2/tc_<code>_<ver>/shot.png. MESEN set, see run.sh."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__))
v, codes = sys.argv[1], sys.argv[2:]
js = "import {allCodes} from './password.mjs'; console.log(JSON.stringify(Object.fromEntries(allCodes(process.argv[1]))))"
tab = json.loads(subprocess.run(["node", "--input-type=module", "-e", js, v], cwd=here, capture_output=True, text=True).stdout)
if codes == ["all"]:
    codes = list(tab) + ["0000", "7824"]
scr = os.environ.get("SCRATCH", "/d/tmp/bomberman/gb")
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr   # MSYS /d/... -> d:/...
os.makedirs(os.path.join(scr, "gb2", "_tc_" + v), exist_ok=True)


def run(code):
    s = os.path.join(scr, "gb2", "_tc_" + v, "tc_%s.lua" % code)   # per-version dir: two runs may share a code
    open(s, "w").write('CODE="%s" SHOTAT=%s\n' % (code, os.environ.get("SHOTAT", "200")) + open(os.path.join(here, "test_codes.lua")).read())
    out = subprocess.run(["sh", os.path.join(here, "run.sh"), s, v], capture_output=True, text=True).stdout
    os.remove(s)
    return next((l for l in out.splitlines() if l.startswith("CODE ")), "CODE %s none" % code)


bad = 0
with ThreadPoolExecutor(2) as ex:
    for line in ex.map(run, codes):
        p = line.split()
        r = dict(x.split("=") for x in p[2:]) if len(p) > 3 else {}
        d = tab.get(p[1])
        if d is None:
            ok = r.get("rej") == "1"
        else:
            ok = r["rej"] == "0" and int(r["C1BD"], 16) == d["value"]
            if d["kind"] == "world":
                ok = ok and int(r["C100"], 16) == (d["world"] - 1) << 4
            if d["kind"] == "powerup":
                ok = ok and r["C125"] == r["C126"] == "7F"
            if d["kind"] == "battle":
                ok = ok and r["C11A"] == "01"
        bad += not ok
        print("ok " if ok else "BAD", line, d)
print(len(codes), "codes,", bad, "bad")
