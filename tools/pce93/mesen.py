"""Run a Mesen 2 Lua snippet headless on a PC Engine ROM (Mesen.exe --testrunner). Set MESEN to a portable Mesen.exe.
Usage: python tools/pce93/mesen.py script.lua rom -> writes <name>.png for each shot(name), <name>.ram for dump(name)
(8 KB work RAM, logical $2000-$3FFF) and <name>.vram / .pal / .spr for vdump(name)."""
import subprocess, sys, binascii, os
HERE = os.path.dirname(os.path.abspath(sys.argv[1]))  # output goes next to the script
PRE = r'''
W=emu.memType.pceWorkRam
function hex(s) return (s:gsub('.', function(c) return string.format('%02x', c:byte()) end)) end
local function memhex(mt,n) local t={} for a=0,n-1 do t[#t+1]=string.format('%02x',emu.read(a,mt)) end return table.concat(t) end
function dump(name) print('DUMP '..name..'.ram '..memhex(W,0x2000)) end
function vdump(name) print('DUMP '..name..'.vram '..memhex(emu.memType.pceVideoRam,0x10000))
  print('DUMP '..name..'.pal '..memhex(emu.memType.pcePaletteRam,0x400)) print('DUMP '..name..'.spr '..memhex(emu.memType.pceSpriteRam,0x200)) end
function shot(name) print("SHOT "..name.." "..hex(emu.takeScreenshot())) end
function r(a) return emu.read(a-0x2000,W) end            -- logical RAM address $2000-$3FFF
function wr(a,v) emu.write(a-0x2000,v,W) end
q={}
function wait(n) for i=1,n do q[#q+1]={} end end
function press(b,n) n=n or 4; for i=1,n do q[#q+1]=b end; wait(6) end
function at(fn) q[#q+1]=fn end
function S(n) at(function() shot(n) end) end
function D(n) at(function() dump(n) end) end
emu.addEventCallback(function()
  local s=table.remove(q,1)
  if s==nil then emu.stop(0) return end
  if type(s)=="function" then s() s={} end
  emu.setInput(s,0)
end, emu.eventType.inputPolled)
'''
src = PRE + open(sys.argv[1]).read()
open(os.path.join(HERE, '_s.lua'), 'w').write(src)
p = subprocess.run([os.environ.get("MESEN", "Mesen.exe"), "--testrunner", "--timeout=590", sys.argv[2], os.path.join(HERE, '_s.lua')],
                   capture_output=True, text=True, timeout=600)
for line in p.stdout.splitlines():
    if line.startswith("SHOT "):
        _, n, h = line.split(" ", 2); open(os.path.join(HERE, n + ".png"), "wb").write(binascii.unhexlify(h)); print("wrote", n)
    elif line.startswith("DUMP "):
        _, n, h = line.split(" ", 2); open(os.path.join(HERE, n), "wb").write(binascii.unhexlify(h)); print("dumped", n)
    elif line.startswith("CDLHEX "):
        _, n, h = line.split(" ", 2); open(os.path.join(HERE, n + ".cdl"), "wb").write(binascii.unhexlify(h)); print("cdl", n)
    elif "Uninitialized" not in line: print(line)
print("rc", p.returncode)
