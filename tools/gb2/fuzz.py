"""Run fuzz.lua (all 10,000 codes through the game's check) and compare with password.mjs.
Usage: python tools/gb2/fuzz.py <jp|us>   (MESEN set; see run.sh)"""
import json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
v = sys.argv[1]
out = subprocess.run(["sh", os.path.join(here, "run.sh"), os.path.join(here, "fuzz.lua"), v], capture_output=True, text=True).stdout
res = next(l for l in out.splitlines() if l.startswith("RES ")).split()[1:]
assert len(res) == 10000, len(res)
js = "import {TABLES} from './password.mjs'; console.log(JSON.stringify(TABLES[process.argv[1]]))"
tab = json.loads(subprocess.run(["node", "--input-type=module", "-e", js, v], cwd=here, capture_output=True, text=True).stdout)
bad = 0
for n, r in enumerate(res):
    c = "%04d" % n
    want = "X" if c not in tab else "%x" % tab[c]
    if r != want:
        bad += 1
        print("MISMATCH", c, r, want)
print(f"{v}: 10000 codes, {sum(r != 'X' for r in res)} accepted by the game, {bad} mismatches with password.mjs")
