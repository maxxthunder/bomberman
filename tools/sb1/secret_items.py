"""Run secret_items.lua for every stage with a secret item (US). Writes scripts to argv[1] and prints results.
Each case meets the stage's condition by real input (waiting, holding Start) or by writing the RAM the
condition routine reads (see docs/sb1.md, Secret items)."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from password import encode
here = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
P = 0x0D40
BOMBSELF = "for i=1,3 do press({b=true},4) press({y=true},4) press({a=true},4) wait(200) end"
PUNCH5 = "wait(20) for i=1,5 do press({y=true},4) wait(14) end"
# stage: (condition, inject lua or '', hold lua or '', frames[, extra lua queued after the inject])
CASES = {
 (1, 2): (7, "emu.write(0x0D25, emu.read(0x0D25,W)+1, W)", "", 120),            # enemy count goes up (as when the exit is bombed)
 (1, 3): (6, "emu.write(0x0C3F, 3, W)", "", 120),                                 # 3 kills in one chain (P1 counter)
 (1, 4): (2, "EXIT=true", "", 3000),                                              # P1 kept on the exit cell for 1280+ frames
 (1, 5): (4, "for _,c in ipairs({0x44,0x5C,0x2C4,0x2DC}) do emu.write(0x0916+c,0x20,W) end", "", 120),  # bomb flag in the 4 corner cells
 (1, 7): (1, "", "", 1400),                                                       # no buttons for 1280 frames
 (2, 2): (3, "", "{start=true}", 30),                                             # Start held
 (2, 4): (5, "emu.write(0x0C91, emu.read(0x0D03,W)+1, W)", "", 120),            # items on the board = $0D03+1
 (3, 3): (11, "emu.write(0x%04X, 0x20, W)" % (P + 0x1C), "", 120),               # score ends in 20
 (3, 4): (0, "emu.write(0x%04X, 1, W)" % (P + 0x3D), "", 300, BOMBSELF),          # lives = 1, then die
 (3, 6): (10, "emu.write(0x%04X, 6, W)" % (P + 0x24), "", 120),                  # 6 bombs out
 (3, 7): (7, "emu.write(0x0D25, emu.read(0x0D25,W)+1, W)", "", 120),
 (4, 1): (4, "for _,c in ipairs({0x44,0x5C,0x2C4,0x2DC}) do emu.write(0x0916+c,0x20,W) end", "", 120),
 (4, 4): (6, "emu.write(0x0C3F, 3, W)", "", 120),
 (4, 5): (0, "emu.write(0x%04X, 1, W)" % (P + 0x3D), "", 300, BOMBSELF),
 (4, 7): (2, "EXIT=true", "", 1400),
 (6, 2): (9, "emu.write16(0x0D40, 0x159E, W)", "", 120),                        # player put in the state a punched bomb causes ($C4:1593)
 (6, 4): (11, "emu.write(0x%04X, 0x20, W)" % (P + 0x1C), "", 120),
 (6, 5): (8, "emu.write(0x0D79, emu.read(0x0D79,W)|2, W)", "", 60, PUNCH5),       # glove flag ($39 bit 1), then 5 punches with Y
 (6, 7): (3, "", "{start=true}", 30),
}
EXIT = """
-- find the exit cell (low 5 bits = $10) and keep P1 on it
local ex=nil for c=0,0x33E,2 do if emu.read(0x0916+c,W)&0x1F==0x10 then ex=c end end
print(string.format('EXIT cell=%03x', ex or 0xFFF))
if ex then emu.addEventCallback(function() emu.write16(0x0D51,((ex%64)//2)*16+8,W) emu.write16(0x0D54,(ex//64)*16+8,W) end, emu.eventType.startFrame) end
"""
os.makedirs(out, exist_ok=True)
only = sys.argv[2:]
for (w, s), (cond, inj, hold, frames, *extra) in CASES.items():
    if only and f'{w}{s}' not in only: continue
    if not frames:
        print(f"{w}-{s} cond {cond}: not run (static)"); continue
    pw = encode(w, s, 0)
    body = EXIT if inj == "EXIT=true" else inj
    ex = f"function() {extra[0]} end" if extra else "nil"
    lua = f"PW='{pw}'\nINJECT=function()\n{body}\nend\nEXTRA={ex}\nHOLD={hold or 'nil'}\nWAITF={frames}\n" + open(os.path.join(here, 'secret_items.lua')).read()
    p = os.path.join(out, f"si_{w}{s}.lua"); open(p, 'w').write(lua)
    r = subprocess.run(['sh', os.path.join(here, 'run.sh'), p], capture_output=True, text=True).stdout
    print(f"{w}-{s} cond {cond}: " + ' | '.join(l for l in r.splitlines() if l.split(' ')[0] in ('START', 'SPAWN', 'NOSPAWN', 'BEFORE', 'AFTER', 'CELL', 'EXIT')))
