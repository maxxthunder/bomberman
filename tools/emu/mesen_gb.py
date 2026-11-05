"""Run a Mesen 2 Lua snippet headless on a Game Boy ROM (Mesen.exe --testrunner). Shared by tools/gb1-gb3.
Set MESEN to a portable Mesen.exe (its own settings.json with Gameboy.Model = "Gameboy").
Usage: python tools/emu/mesen_gb.py script.lua rom.gb
Output next to the script: <name>.png for each shot(name), <name>.ram for dump(name) (WRAM $C000-$DFFF then HRAM
$FF80-$FFFE), <name>.vram for vdump(name) (VRAM 8 KB, OAM 160, BGP/OBP0/OBP1, LCDC, SCY, SCX, WY, WX).
Other printed lines are passed through. Lua helpers: wait(n), press(buttons, n), at(fn) (fn may return the input
to hold), hold(buttons, n); buttons are {a,b,start,select,up,down,left,right}."""
import subprocess, sys, binascii, os
HERE = os.path.dirname(os.path.abspath(sys.argv[1]))
PRE = r'''
function hex(s) return (s:gsub('.', function(c) return string.format('%02x', c:byte()) end)) end
WR=emu.memType.gbWorkRam HR=emu.memType.gbHighRam VR=emu.memType.gbVideoRam OAM=emu.memType.gbSpriteRam
ROM=emu.memType.gbPrgRom BUS=emu.memType.gameboyMemory
function rd(a) return emu.read(a, BUS) end
function wr(a,v) emu.write(a, v, BUS) end
function dump(name) local t={} for a=0,0x1FFF do t[#t+1]=string.format('%02x',emu.read(a,WR)) end
  for a=0,0x7E do t[#t+1]=string.format('%02x',emu.read(a,HR)) end print('DUMP '..name..' '..table.concat(t)) end
function vdump(name) local t={} for a=0,0x1FFF do t[#t+1]=string.format('%02x',emu.read(a,VR)) end
  for a=0,159 do t[#t+1]=string.format('%02x',emu.read(a,OAM)) end
  for _,a in ipairs({0xFF47,0xFF48,0xFF49,0xFF40,0xFF42,0xFF43,0xFF4A,0xFF4B}) do t[#t+1]=string.format('%02x',rd(a)) end
  print('VRAM '..name..' '..table.concat(t)) end
function shot(name) print("SHOT "..name.." "..hex(emu.takeScreenshot())) end
function cdl_dump(name) local c=emu.getCdlData(ROM) local t={}
  for i=0,#c do t[#t+1]=string.format("%02x",c[i] or 0) end print('CDLHEX '..(name or 'cdl')..' '..table.concat(t)) end
q={} ; local last={}
function wait(n) for i=1,n do q[#q+1]={} end end
function press(b,n) n=n or 4; for i=1,n do q[#q+1]=b end; wait(6) end
function hold(b,n) for i=1,n do q[#q+1]=b end end
function at(fn) q[#q+1]=fn end
FRAME=0
emu.addEventCallback(function()
  FRAME=FRAME+1
  local s=table.remove(q,1)
  if s==nil then emu.stop(0) return end
  if type(s)=="function" then s=s() or {} end
  last=s
  emu.setInput(s,0)
end, emu.eventType.inputPolled)
'''
src = PRE + open(sys.argv[1]).read()
open(os.path.join(HERE, '_s.lua'), 'w').write(src)
p = subprocess.run([os.environ.get("MESEN", "Mesen.exe"), "--testrunner", "--timeout=590"] + os.environ.get("MESEN_ARGS", "").split()
                   + [sys.argv[2], os.path.join(HERE, '_s.lua')], capture_output=True, text=True, timeout=620)
for line in p.stdout.splitlines():
    k, _, rest = line.partition(" ")
    if k in ("SHOT", "DUMP", "VRAM", "CDLHEX"):
        n, h = rest.split(" ", 1)
        ext = {"SHOT": ".png", "DUMP": ".ram", "VRAM": ".vram", "CDLHEX": ".cdl"}[k]
        open(os.path.join(HERE, n + ext), "wb").write(binascii.unhexlify(h.strip()))
        print("wrote", n + ext)
    elif "Uninitialized" not in line:
        print(line)
print("rc", p.returncode)
