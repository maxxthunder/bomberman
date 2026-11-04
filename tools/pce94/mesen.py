"""Run a Lua snippet headless in Mesen 2 (PC Engine): tools/pce94/run.sh wraps this.
Usage: python mesen.py script.lua rom outdir -> <outdir>/<name>.png for each shot(name), <name>.bin for dump(name,...).
A copy of tools/emu/mesen.py with a PC Engine prelude: r8/w8 read/write work RAM ($2000-$3FFF logical = pceWorkRam),
pad buttons are i, ii, select, run, up, down, left, right."""
import subprocess, sys, binascii, os
PRE = r'''
function hex(s) return (s:gsub('.', function(c) return string.format('%02x', c:byte()) end)) end
function r8(a) return emu.read(a & 0x1FFF, emu.memType.pceWorkRam) end
function w8(a,v) emu.write(a & 0x1FFF, v, emu.memType.pceWorkRam) end
function dump(name, mt, n) local t={} for a=0,(n or emu.getMemorySize(mt))-1 do t[#t+1]=string.format('%02x',emu.read(a,mt)) end print('DUMP '..name..' '..table.concat(t)) end
function shot(name) print("SHOT "..name.." "..hex(emu.takeScreenshot())) end
q={} qi=1  -- input queue: one entry per frame (a button table or a function to run); qi = next entry
function wait(n) for i=1,n do q[#q+1]={} end end
function press(b,n) n=n or 4; for i=1,n do q[#q+1]=b end; wait(6) end
function at(fn) q[#q+1]=fn end
emu.addEventCallback(function()
  local s=q[qi] qi=qi+1
  if s==nil then emu.stop(0) return end
  while type(s)=="function" do s() s=q[qi] or {} qi=qi+1 end
  emu.setInput(s,0)
end, emu.eventType.inputPolled)
'''
src = PRE + open(sys.argv[1]).read()
out = sys.argv[3]; os.makedirs(out, exist_ok=True)
open(os.path.join(out, '_s.lua'), 'w').write(src)
p = subprocess.run([os.environ["MESEN"], "--testrunner", "--timeout=590", sys.argv[2], os.path.join(out, '_s.lua')],
                   capture_output=True, text=True, timeout=600)
log = open(os.path.join(out, 'log.txt'), 'w')
for line in p.stdout.splitlines():
    if line.startswith("SHOT "):
        _, n, h = line.split(" ", 2); open(os.path.join(out, n + ".png"), "wb").write(binascii.unhexlify(h))
    elif line.startswith("DUMP "):
        _, n, h = line.split(" ", 2); open(os.path.join(out, n + ".bin"), "wb").write(binascii.unhexlify(h))
    else:
        log.write(line + "\n")
        if not line.startswith("[SCSI]"):  # CD reads go to log.txt only
            print(line)
print("rc", p.returncode, p.stderr[-500:] if p.returncode else "")
