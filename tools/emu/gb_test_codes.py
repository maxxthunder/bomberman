"""Type codes in Mesen with real pad input (tools/<game>/test_codes.lua, one Mesen per code, 2 at once) and check the
RAM the check writes against password.mjs. Usage: python tools/emu/gb_test_codes.py <gb1|gb2> <ver> CODE [CODE...]
(or 'all'); ver is jp|wario for gb1, jp|us for gb2.
Screenshots: $SCRATCH/<game>/tc_<code>_<ver>/shot.png. MESEN set, see run.sh."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
g, v, codes = sys.argv[1], sys.argv[2], sys.argv[3:]
here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", g)
js = "import {allCodes} from './password.mjs'; console.log(JSON.stringify(Object.fromEntries(allCodes(process.argv[1]))))"
tab = json.loads(subprocess.run(["node", "--input-type=module", "-e", js, v], cwd=here, capture_output=True, text=True).stdout)
if codes == ["all"]:
    codes = list(tab) + ["0000", {"gb1": "1234", "gb2": "7824"}[g]]
scr = os.environ.get("SCRATCH", "/d/tmp/bomberman/gb")
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr   # MSYS /d/... -> d:/...
os.makedirs(os.path.join(scr, g, "_tc_" + v), exist_ok=True)


def run(code):
    s = os.path.join(scr, g, "_tc_" + v, "tc_%s.lua" % code)   # per-version dir: two runs may share a code
    open(s, "w").write('CODE="%s" SHOTAT=%s\n' % (code, os.environ.get("SHOTAT", "200")) + open(os.path.join(here, "test_codes.lua")).read())
    out = subprocess.run(["sh", os.path.join(here, "run.sh"), s, v], capture_output=True, text=True).stdout
    os.remove(s)
    return next((l for l in out.splitlines() if l.startswith("CODE ")), "CODE %s none" % code)


def gb1(d, r):
    if d["kind"] == "stage":
        return r["rej"] == "0" and int(r["C3F0"], 16) == (d["value"] & 0x1F) and (v == "jp" or r["C3D5"] == ("01" if d["player"] == "bomberman" else "00"))
    if d["kind"] == "powerup":
        return r["C3FB"] == "01" and r["rej"] == "0"
    return r["bat"] == "1"


def gb2(d, r):
    return (r["rej"] == "0" and int(r["C1BD"], 16) == d["value"]
            and (d["kind"] != "world" or int(r["C100"], 16) == (d["world"] - 1) << 4)
            and (d["kind"] != "powerup" or r["C125"] == r["C126"] == "7F")
            and (d["kind"] != "battle" or r["C11A"] == "01"))


bad = 0
with ThreadPoolExecutor(2) as ex:
    for line in ex.map(run, codes):
        p = line.split()
        r = dict(x.split("=") for x in p[2:]) if len(p) > 3 else {}
        d = tab.get(p[1])
        ok = r.get("rej") == "1" if d is None else {"gb1": gb1, "gb2": gb2}[g](d, r)
        bad += not ok
        print("ok " if ok else "BAD", line, d)
print(len(codes), "codes,", bad, "bad")
