"""Run a Mesen 2 Lua snippet headless (Mesen.exe --testrunner) on an NES ROM. Set MESEN to a portable Mesen.exe.
Usage: python tools/emu/mesen_nes.py script.lua rom -> <name>.png for each shot(name), <name>.ram (2 KB CPU RAM) for dump(name), next to the script;
CDLHEX lines (lib.lua cdl_dump) go to <name>.cdlhex.
Extra Mesen switches from env MESEN_ARGS. A function queued with at() may return the input to hold."""
import subprocess, sys, re, binascii, os  # --timeout: the test runner otherwise kills scripts after 100 s (rc 4294967295)
HERE=os.path.dirname(os.path.abspath(sys.argv[1]))  # output goes next to the script
PRE=r'''
function hex(s) return (s:gsub('.', function(c) return string.format('%02x', c:byte()) end)) end
function dump(name) local t={} for a=0,0x7FF do t[#t+1]=string.format('%02x',emu.read(a,emu.memType.nesInternalRam)) end print('DUMP '..name..' '..table.concat(t)) end
function shot(name) print("SHOT "..name.." "..hex(emu.takeScreenshot())) end
q={} ; local last={}
function wait(n) for i=1,n do q[#q+1]={} end end
function press(b,n) n=n or 4; for i=1,n do q[#q+1]=b end; wait(6) end
function at(fn) q[#q+1]=fn end
emu.addEventCallback(function()
  local s=table.remove(q,1)
  if s==nil then emu.stop(0) return end
  if type(s)=="function" then s=s() or last end
  last=s
  emu.setInput(s,0)
end, emu.eventType.inputPolled)
'''
src=PRE+open(sys.argv[1]).read()
open(os.path.join(HERE,'_s.lua'),'w').write(src)
rom=sys.argv[2]
p=subprocess.run([os.environ.get("MESEN", "Mesen.exe"),"--testrunner","--timeout=590"]+os.environ.get("MESEN_ARGS","").split()+[rom,os.path.join(HERE,'_s.lua')],capture_output=True,text=True,timeout=600)
for line in p.stdout.splitlines():
    if line.startswith("SHOT "):
        _,n,h=line.split(" ",2); open(os.path.join(HERE,n+".png"),"wb").write(binascii.unhexlify(h)); print("wrote",n)
    elif line.startswith("DUMP "):
        _,n,h=line.split(" ",2); open(os.path.join(HERE,n+".ram"),"wb").write(binascii.unhexlify(h)); print("dumped",n)
    elif line.startswith("CDLHEX "):
        _,n,h=line.split(" ",2); open(os.path.join(HERE,n+".cdlhex"),"w").write(h); print("cdl",n)
    elif "Uninitialized" not in line: print(line)
print("rc",p.returncode)
