"""Type codes in Mesen with real pad input (test_codes.lua, one Mesen at a time) and check what the game's check wrote
against password.mjs. Usage: python tools/pocket/test_codes.py CODE [CODE...]  ('all': the 32 table codes).
Screenshots: $SCRATCH/pocket/tc_<code>_us/{pw,go}.png. MESEN set, see run.sh."""
import json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
codes = sys.argv[1:]
js = """import {decode, TABLE} from './password.mjs'; const c = process.argv[1] === 'all' ? TABLE : process.argv.slice(1);
console.log(JSON.stringify([c, c.map(decode)]))"""
codes, dec = json.loads(subprocess.run(["node", "--input-type=module", "-e", js] + codes, cwd=here, capture_output=True, text=True).stdout)
scr = os.environ["SCRATCH"]
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr
os.makedirs(os.path.join(scr, "pocket", "_tc"), exist_ok=True)
MODE = {"stage": 0, "power": 1, "boss": 2, "ending": 3}
bad = 0
for code, f in zip(codes, dec):
    s = os.path.join(scr, "pocket", "_tc", "tc_%s.lua" % code)
    open(s, "w").write('CODE="%s" SHOTAT=%s\n' % (code, os.environ.get("SHOTAT", "900")) + open(os.path.join(here, "test_codes.lua")).read())
    out = subprocess.run(["sh", os.path.join(here, "run.sh"), s], capture_output=True, text=True).stdout
    line = next((l for l in out.splitlines() if l.startswith("CODE ")), "CODE %s none" % code)
    r = dict(x.split("=") for x in line.split()[2:] if "=" in x)
    if f is None:
        ok = r.get("rej") == "1"
    else:
        p = "6,4,4,3" if f["kind"] in ("power", "boss") else "0,0,4,3" if f["kind"] == "ending" else "0,0,0,0"
        ok = r.get("rej") == "0" and r["idx"] == str(f["index"]) and r["mode"] == str(MODE[f["kind"]]) and r["p"] == p and \
            (f["kind"] == "ending" or (r["world"], r["stage"]) == (str(f["world"]), str(f["stage"] - 1)))
    bad += not ok
    print("ok " if ok else "BAD", line, flush=True)
print(len(codes), "codes,", bad, "bad")
