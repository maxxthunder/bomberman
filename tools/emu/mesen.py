"""Run a Mesen 2 Lua snippet headless (Mesen.exe --testrunner). Set MESEN to Mesen.exe.
Usage: python tools/emu/mesen.py script.lua rom [outdir]
-> <name>.png for each shot(name), <name>.ram for dump(name) (SNES work RAM; a game's lib.lua may redefine dump, and a
name with a dot is kept as is) and <name>.cdl for 'CDLBIN <name> <hex>' lines, next to the script. With outdir: output
goes there, dumps are <name>.bin, nothing is printed per file and every other line also goes to <outdir>/log.txt
([SCSI] lines only there). Extra Mesen switches from env MESEN_ARGS; MESEN_TIMEOUT = seconds (default 590).
Queue: an at() function gets no input that frame, or (KEEP=true) its return value / the last input. stop() ends
the run; hold=true keeps it running on an empty queue, sending pad. lib.lua may replace tick() (one per poll)."""
import subprocess, sys, binascii, os  # --timeout: the test runner otherwise kills scripts after 100 s (rc 4294967295)
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(sys.argv[1]))  # default: next to the script
PRE=r'''
function hex(s) return (s:gsub('.', function(c) return string.format('%02x', c:byte()) end)) end
function dump(name) local t={} for a=0,0x1FFFF do t[#t+1]=string.format('%02x',emu.read(a,emu.memType.snesWorkRam)) end print('DUMP '..name..' '..table.concat(t)) end
function shot(name) print("SHOT "..name.." "..hex(emu.takeScreenshot())) end
q={} ; local last={}
hold=false pad={}
function stop() emu.stop(0) end
function wait(n) for i=1,n do q[#q+1]={} end end
function press(b,n) n=n or 4; for i=1,n do q[#q+1]=b end; wait(6) end
function at(fn) q[#q+1]=fn end
function tick()
  local s=table.remove(q,1)
  if s==nil then if hold then emu.setInput(pad or {},0) return end emu.stop(0) return end
  if type(s)=="function" then local r=s() s=KEEP and (r or last) or {} end
  last=s
  emu.setInput(s,0)
end
emu.addEventCallback(function() tick() end, emu.eventType.inputPolled)
'''
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT,'_s.lua'),'w').write(PRE+open(sys.argv[1]).read())
t=int(os.environ.get("MESEN_TIMEOUT", 590))
p=subprocess.run([os.environ.get("MESEN", "Mesen.exe"),"--testrunner",f"--timeout={t}"]+os.environ.get("MESEN_ARGS","").split()+[sys.argv[2],os.path.join(OUT,'_s.lua')],capture_output=True,text=True,timeout=t+10)
log = open(os.path.join(OUT, "log.txt"), "w") if len(sys.argv) > 3 else None
for line in p.stdout.splitlines():
    k, _, rest = line.partition(" ")
    if k in ("SHOT", "DUMP", "CDLBIN"):
        n, h = rest.split(" ", 1)
        ext = {"SHOT": ".png", "CDLBIN": ".cdl"}.get(k, "" if "." in n else ".bin" if log else ".ram")
        open(os.path.join(OUT, n + ext), "wb").write(binascii.unhexlify(h))
        if not log: print({"SHOT": "wrote", "DUMP": "dumped", "CDLBIN": "cdl"}[k], n)
    elif log:
        log.write(line + "\n")
        if not line.startswith("[SCSI]"): print(line)  # CD reads go to log.txt only
    elif "Uninitialized" not in line: print(line)
print("rc", p.returncode, *[p.stderr[-500:] if p.returncode else ""][:bool(log)])
