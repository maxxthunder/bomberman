"""Type codes in Mesen with real pad input (test_codes.lua, one Mesen per code, 2 at once) and check what the
game's check wrote against password.mjs. Usage: python tools/gb3/test_codes.py CODE [CODE...]  ('faq': every
GameFAQs code in faq_codes.txt). Screenshots: $SCRATCH/gb3/tc_<code>_jp/shot.png. MESEN set, see run.sh."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__))
codes = sys.argv[1:]
if codes == ["faq"]:
    codes = list(dict.fromkeys(open(os.path.join(here, "faq_codes.txt")).read().split()))
js = """import {decode} from './password.mjs'; console.log(JSON.stringify(process.argv.slice(1).map(decode)))"""
dec = dict(zip(codes, json.loads(subprocess.run(["node", "--input-type=module", "-e", js] + codes, cwd=here, capture_output=True, text=True).stdout)))
scr = os.environ.get("SCRATCH", "/d/tmp/bomberman/gb")
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr
os.makedirs(os.path.join(scr, "gb3", "_tc"), exist_ok=True)


def run(code):
    s = os.path.join(scr, "gb3", "_tc", "tc_%s.lua" % code)
    open(s, "w").write('CODE="%s" SHOTAT=%s\n' % (code, os.environ.get("SHOTAT", "300")) + open(os.path.join(here, "test_codes.lua")).read())
    out = subprocess.run(["sh", os.path.join(here, "run.sh"), s, "jp"], capture_output=True, text=True).stdout
    return next((l for l in out.splitlines() if l.startswith("CODE ")), "CODE %s none" % code)


bad = 0
with ThreadPoolExecutor(2) as ex:
    for line in ex.map(run, codes):
        p = line.split()
        r = dict(x.split("=") for x in p[2:]) if len(p) > 3 else {}
        f = dec[p[1]]
        if f is None:
            ok = r.get("rej") == "1"
        elif "special" in f:
            ok = r.get("rej") == "0" and r["boss"] == "1"
        else:
            ok = r.get("rej") == "0" and [int(r["area"]), int(r["stage"]), int(r["extra"]), r["cleared"], int(r["shop"]), int(r["check"])] == \
                [f["area"], f["stage"], f["extra"], "".join(map(str, f["cleared"])), f["shop"], f["check"]]
        bad += not ok
        print("ok " if ok else "BAD", line)
print(len(codes), "codes,", bad, "bad")
