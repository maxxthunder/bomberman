"""Run fuzz.lua in Mesen (every code 0000-9999 through the game's own check) and compare with password.mjs.
Usage: python tools/pocket/fuzz.py   (MESEN set; see run.sh)"""
import json, os, subprocess
here = os.path.dirname(os.path.abspath(__file__))
out = subprocess.run(["sh", os.path.join(here, "run.sh"), os.path.join(here, "fuzz.lua")], capture_output=True, text=True).stdout
res = next(l for l in out.splitlines() if l.startswith("RES ")).split()[1:]
assert len(res) == 10000, len(res)
js = """import {decode} from './password.mjs';
console.log(JSON.stringify(Array.from({length: 10000}, (_, i) => decode(String(i).padStart(4, '0')))))"""
dec = json.loads(subprocess.run(["node", "--input-type=module", "-e", js], cwd=here, capture_output=True, text=True).stdout)
# game: index, world $C1DC, stage-1 $C1DD, $C352 mode, $C353-$C356 (player $0E, bombs, fire, lives)
MODE = {"stage": 0, "power": 1, "boss": 2, "ending": 3}
bad = 0
for i, (r, f) in enumerate(zip(res, dec)):
    if f is None:
        want = "X"
    elif f["kind"] == "ending":
        want = "31,0,0,3,0,0,4,3"
    else:
        p = f["kind"] != "stage"
        want = ",".join(map(str, [f["index"], f["world"], f["stage"] - 1, MODE[f["kind"]]] + ([6, 4, 4, 3] if p else [0, 0, 0, 0])))
    if r != want:
        bad += 1
        print("MISMATCH %04d" % i, r, want)
print(f"10000 codes, {sum(r != 'X' for r in res)} accepted by the game, {bad} mismatches with password.mjs")
