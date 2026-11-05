"""Build the decoder fuzz set, run fuzz.lua in Mesen and compare with password.mjs.
Usage: python tools/gb3/fuzz.py [N random codes, default 20000]   (MESEN set; see run.sh)
Set: every GameFAQs code, N random 7-digit codes, every hex digit at every position of 8 valid codes, and one
encoded code for each (area, stage, extra) with random cleared/shop choices that balance."""
import json, os, random, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
rnd = random.Random(3)
H = "0123456789ABCDEF"
FAQ = open(os.path.join(here, "faq_codes.txt")).read().split()
js = """import {decode, encode} from './password.mjs';
const [n, seed] = process.argv.slice(1).map(Number); let r = seed;
const rand = k => { r = (r * 1103515245 + 12345) % 2147483648; return r % k; };
const enc = [];
for (let a = 0; a < 7; a++) for (let s = 1; s <= 6; s++) for (const x of s === 6 ? [0, 1, 2] : [0])
  for (let t = 0; t < 40; t++) { const c = encode(a, s, [0,1,2,3,4,5,6].map(() => rand(2)), rand(256), x); if (c) { enc.push(c); if (enc.length % 4 === 0) break; } }
process.stdout.write(JSON.stringify(enc));"""
enc = json.loads(subprocess.run(["node", "--input-type=module", "-e", js, "0", "7"], cwd=here, capture_output=True, text=True).stdout)
codes = FAQ + enc + ["".join(rnd.choice(H) for _ in range(7)) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 20000)]
for base in enc[:8]:
    codes += [base[:i] + c + base[i + 1:] for i in range(7) for c in H]
scr = os.environ.get("SCRATCH", "/d/tmp/bomberman/gb")
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr
os.makedirs(os.path.join(scr, "gb3"), exist_ok=True)
s = os.path.join(scr, "gb3", "fz.lua")
open(s, "w").write('CODES="%s"\n' % "".join(codes) + open(os.path.join(here, "fuzz.lua")).read())
out = subprocess.run(["sh", os.path.join(here, "run.sh"), s, "jp"], capture_output=True, text=True).stdout
res = next(l for l in out.splitlines() if l.startswith("RES ")).split()[1:]
assert len(res) == len(codes), (len(res), len(codes))
js2 = """import {decode} from './password.mjs'; let s = '';
process.stdin.on('data', d => s += d).on('end', () => console.log(JSON.stringify(s.split(' ').map(decode))));"""
dec = json.loads(subprocess.run(["node", "--input-type=module", "-e", js2], cwd=here, input=" ".join(codes), capture_output=True, text=True).stdout)
bad = valid = 0
for c, r, f in zip(codes, res, dec):
    if f is None:
        want = "X"
    elif "special" in f:
        want = "boss"
    else:
        want = "%d,%d,%d,%s,%d,%d" % (f["area"], f["stage"], f["extra"], "".join(map(str, f["cleared"])), f["shop"], f["check"])
    valid += r != "X"
    if r != want:
        bad += 1
        print("MISMATCH", c, r, want)
print(f"{len(codes)} codes ({len(FAQ)} GameFAQs, {len(enc)} encoded), {valid} accepted by the game, {bad} mismatches with password.mjs")
for c, r in zip(FAQ, res):
    print("FAQ", c, r)
