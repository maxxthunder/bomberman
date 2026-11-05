"""Run a Lua test on any SB2 version: python tools/sb2/run.py script.lua rom.sfc [NAME=value ...]
(each NAME in the script is replaced by value before running)
Prepends ADDR (per-version addresses found by byte pattern) and title(): tap START until the title
menu polls input ($CC:138A USA), so menu presses don't depend on intro timing. Then use the
tools/emu/mesen.py helpers (wait/press/at/shot/dump) as usual; queue the rest inside title(function() ... end).
Also: pw(code) writes a code into the password digits $7F:0028-$7F:002F."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fuzz import find, TITLE_POLL, USA_CHECK

PATTERNS = {  # name: (bytes found in every version, offset added)
    "TITLE": (TITLE_POLL, 0),
    "CHECK": (USA_CHECK, 0),
    "JOYCARD": (bytes.fromhex("1a8fcf1c00c92000b042af32407f8940"), -6),  # X-turbo counter, $CC:14C0 USA
}

PRE = r"""
local _cb=nil
function title(fn)
  hold=true local f=0
  _cb=emu.addEventCallback(function() f=f+1 pad=(f%60<5) and {start=true} or {} end, emu.eventType.inputPolled)
  local id
  id=emu.addMemoryCallback(function()
    emu.removeMemoryCallback(id, emu.callbackType.exec, ADDR.TITLE, ADDR.TITLE)
    emu.removeEventCallback(_cb, emu.eventType.inputPolled) pad={} hold=false
    fn()
  end, emu.callbackType.exec, ADDR.TITLE, ADDR.TITLE)
end
function pw(s) at(function() for i=0,3 do emu.write16(0x7F0028+2*i,tonumber(s:sub(i+1,i+1)),emu.memType.snesMemory) end end) end
"""

if __name__ == "__main__":
    script, romp = sys.argv[1], sys.argv[2]
    rom = open(romp, "rb").read()
    addr = {k: find(rom, p) + o for k, (p, o) in PATTERNS.items()}
    head = "ADDR={" + ",".join(f"{k}=0x{v:06X}" for k, v in addr.items()) + "}\n"
    tmp = os.path.join(os.path.dirname(os.path.abspath(script)), "_run_" + os.path.basename(script))
    body = open(script).read()
    for kv in sys.argv[3:]:
        k, v = kv.split("=", 1)
        body = body.replace(k, v)
    open(tmp, "w").write(head + PRE + body)
    sys.exit(subprocess.run([sys.executable, os.path.join(HERE, "..", "emu", "mesen.py"), tmp, romp], env=dict(os.environ, MESEN_TIMEOUT="5990")).returncode)
