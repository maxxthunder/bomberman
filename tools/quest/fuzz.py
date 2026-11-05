"""Fuzz password.mjs's checkSave against the game's own save check (fuzz.lua): per version, N cart RAM images (valid
saves of random game blocks from makeSave, each mutated in one of several ways, plus pure noise) go through the
game's check in Mesen, and the answers are compared. Usage: python tools/quest/fuzz.py [N=2000] [us|jp ...]"""
import json, os, random, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
vers = sys.argv[2:] or ["us", "jp"]
scr = os.environ["SCRATCH"]
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr
js = """import {makeSave, checkSave} from './password.mjs'; let s = ''; process.stdin.on('data', d => s += d).on('end', () => {
const q = JSON.parse(s); console.log(JSON.stringify({made: q.blocks.map(b => Array.from(makeSave(Uint8Array.from(Buffer.from(b, 'hex'))))),
  ok: q.imgs ? q.imgs.map(h => checkSave(Uint8Array.from(Buffer.from(h, 'hex')))) : []})); });"""
node = lambda q: json.loads(subprocess.run(["node", "--input-type=module", "-e", js], cwd=here, input=json.dumps(q), capture_output=True, text=True).stdout)
total_bad = 0
for ver in vers:
    rnd = random.Random(ver)
    blocks = [bytes(rnd.randrange(256) for _ in range(0xE4)).hex() for _ in range(n)]
    imgs = []
    for k, img in enumerate(node({"blocks": blocks})["made"]):
        img, m = bytearray(img), k % 8
        if m == 1: img[rnd.randrange(0x0F, 0xF3)] ^= 1 << rnd.randrange(8)          # one game-block bit
        elif m == 2: img[0] = (img[0] + 1) & 255                                     # checksum off by one
        elif m == 3: img[0xF3] ^= 0x80                                               # second copy differs
        elif m == 4: img[rnd.randrange(1, 15)] ^= 0x20                               # signature letter case
        elif m == 5: img = bytearray(rnd.randrange(256) for _ in range(0xF4))          # noise
        elif m == 6: a, b = rnd.sample(range(0x0F, 0xF3), 2); img[a], img[b] = img[b], img[a]   # two bytes swapped (same sum)
        imgs.append(img.hex())                                                        # 0, 7: valid as made
    want = node({"blocks": [], "imgs": imgs})["ok"]
    got = []
    for c in range(0, n, 500):
        d = os.path.join(scr, "quest", "_t", "fuzz_%s_%d" % (ver, c)); os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "fuzz.lua")
        open(f, "w").write("IMGS = {%s}\n" % ",".join("'%s'" % h for h in imgs[c:c + 500]) + open(os.path.join(here, "fuzz.lua")).read())
        out = subprocess.run(["sh", os.path.join(here, "run.sh"), f, ver], capture_output=True, text=True, env=dict(os.environ, OUT=d)).stdout
        got += next(l for l in out.splitlines() if l.startswith("RES ")).split()[1:]
    assert len(got) == n, (ver, len(got))
    bad = sum((g == "1") != w for g, w in zip(got, want))
    total_bad += bad
    print(f"{ver}: {n} images, {got.count('1')} accepted by the game, {sum(want)} by checkSave, {bad} mismatches", flush=True)
print(total_bad, "mismatches")
