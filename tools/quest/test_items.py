"""GameShark item codes in Mesen (test_items.lua): for each version, a new game with the codes for the odd ids, then
one with the even ids (every weapon, equipment and item), and every bag page read back: the names on the menu must be
exactly the ones password.mjs names for the codes given. Usage: python tools/quest/test_items.py [us|jp ...]
(MESEN, SCRATCH set; see run.sh). Screenshots: $SCRATCH/quest/_t/ti_<ver>_<odd|even>/page<n>.png."""
import json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
scr = os.environ["SCRATCH"]
scr = scr[1] + ":" + scr[2:] if scr[:1] == "/" and scr[2:3] == "/" else scr
js = """import {encode, WEAPONS, EQUIPMENT, ITEMS} from './password.mjs'; const v = process.argv[1], out = {};
for (const par of [1, 0]) { const pick = l => l.filter(e => e.id % 2 === par);
  const st = {weapon: pick(WEAPONS).map(e => e.id), equipment: pick(EQUIPMENT).map(e => e.id), item: Object.fromEntries(pick(ITEMS).map(e => [e.id, 9]))};
  out[par ? 'odd' : 'even'] = {codes: encode(st, v), names: [...pick(WEAPONS), ...pick(EQUIPMENT), ...pick(ITEMS)].map(e => e.name)}; }
console.log(JSON.stringify(out))"""
# the bag pages' slots in reading order (seen on the US menu with every item; Japan has the same layout)
W = list(range(8, 29)) + list(range(1, 8))
LAYOUT = {(0, i // 7, i % 7): ("weapon", w) for i, w in enumerate(W)}
LAYOUT.update({(1, i // 4, i % 4): ("equipment", e) for i, e in enumerate(range(1, 17))})
LAYOUT.update({(2, i // 8, i % 8): ("item", t) for i, t in enumerate([1, 2, 3, 4, 9, 10, 11, 12, 5, 6, 7, 8, 13, 14, 15, 16])})
js_names = """import {WEAPONS, EQUIPMENT, ITEMS} from './password.mjs'; console.log(JSON.stringify({weapon: WEAPONS, equipment: EQUIPMENT, item: ITEMS}))"""
NAMES = json.loads(subprocess.run(["node", "--input-type=module", "-e", js_names], cwd=here, capture_output=True, text=True).stdout)
SLOT = {NAMES[k][i - 1]["name"]: pos for pos, (k, i) in LAYOUT.items()}
EMPTY = "ff00" * 32   # an empty slot: 4 tiles of flat colour 1
bad = 0
for ver in sys.argv[1:] or ["us", "jp"]:
    sets = json.loads(subprocess.run(["node", "--input-type=module", "-e", js, ver], cwd=here, capture_output=True, text=True).stdout)
    for tag, s in sets.items():
        d = os.path.join(scr, "quest", "_t", "ti_%s_%s" % (ver, tag)); os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "ti.lua")
        open(f, "w").write("CODES = {%s}\n" % ",".join('"%s"' % c for c in s["codes"]) + open(os.path.join(here, "test_items.lua")).read())
        out = subprocess.run(["sh", os.path.join(here, "run.sh"), f, ver], capture_output=True, text=True, env=dict(os.environ, OUT=d)).stdout
        got, names = {}, set()
        for l in out.splitlines():
            if l.startswith("NAME "):
                f = l.split(" ", 5) + [""]
                if f[4] != EMPTY: got[tuple(map(int, f[1:4]))] = f[5]
                if f[5]: names.add(f[5])
        # the normal start has the Normal Bomb (weapon 8) and the Flute (item 11) of its own
        want = set(s["names"]) | {"Normal Bomb", "Flute"}
        # exactly the expected slots show an icon; US: and the names the cursor prints are the expected ones (the cursor
        # starts where the page puts it, so names are compared as a set; Japan prints kana)
        ok = set(got) == {SLOT[n] for n in want} and (ver == "jp" or names == want)
        bad += not ok
        print("ok " if ok else "BAD", ver, tag, len(s["codes"]), "codes,", len(got), "slots filled", "" if ok else sorted(map(str, set(got) ^ {SLOT[n] for n in want})), flush=True)
print(bad, "bad")
