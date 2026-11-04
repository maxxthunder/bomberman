"""Run every 4-digit code (0000-9999) through the game's own password check in Mesen 2 and compare
with password.py. Usage: python tools/sb2/fuzz.py <rom.sfc> [outdir]   (MESEN = path to Mesen.exe)

The check routine (USA $CC:1926) is found in the ROM by its bytes, so this works on every version.
The script boots to the password screen, presses START once, and when the check starts it saves a
state. Each code is then written into the digit buffer $7F:0028-$7F:002F, the check runs, and the
"found" ($CC:19A8, index in $46) or "not found" ($CC:1971) branch is logged before reloading the state.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import password

USA_CHECK = bytes.fromhex(  # $CC:1926-$CC:1975 in the USA ROM: no absolute code addresses inside
    "c220a9000085 76e220a9cc8578c220a900008546a5460a0aa8e220b776cf28007fd01dc8b776cf2a007fd014c8"
    "b776cf2c007fd00bc8b776cf2e007fd0028042c220e646a546c90b00d0c9".replace(" ", ""))
TITLE_POLL = bytes.fromhex("af2e407fd001")  # LDA $7F402E / BNE: title menu waits for a button


def find(rom, pat):
    i = rom.find(pat)
    if i < 0:
        sys.exit("pattern not found")
    return 0xC00000 + i


def lua(base, title):
    return f"""
local MEM=emu.memType.snesMemory
local base=0x{base:06X}
local st=nil local n=0 local res={{}}
local function put(code) for i=0,3 do emu.write16(0x7F0028+2*i, math.floor(code / 10^(3-i)) % 10, MEM) end end
emu.addMemoryCallback(function()
  if st==nil then st=emu.createSavestate() put(n) end
end, emu.callbackType.exec, base, base)
local function done(v)
  res[#res+1]=string.format('%04d:%d', n, v) n=n+1
  if n>9999 then print('RES '..table.concat(res,' ')) emu.stop(0) return end
  emu.loadSavestate(st) put(n)  -- the exec callback at base does not fire again after a load
end
emu.addMemoryCallback(function() done(-1) end, emu.callbackType.exec, base+0x4B, base+0x4B)
emu.addMemoryCallback(function() done(emu.read16(0x46,MEM)) end, emu.callbackType.exec, base+0x82, base+0x82)
-- boot: tap START until the title menu runs, wait out its input delay, then PASSWORD (2 down, A)
hold=true
local f=0 local stage=0 local t=0
emu.addEventCallback(function()
  f=f+1 t=t+1
  if stage==0 then pad=(f%60<5) and {{start=true}} or {{}} if f>3000 then print('NOMENU') emu.stop(1) end
  elseif stage==1 then
    if t==300 or t==330 then pad={{down=true}} elseif t==360 then pad={{a=true}} elseif t==400 then pad={{}} stage=2 t=0 else pad={{}} end
  elseif stage==2 then pad=(t>=300 and t<304) and {{start=true}} or {{}} if t>1500 then print('NOCHECK') emu.stop(1) end
  end
end, emu.eventType.inputPolled)
emu.addMemoryCallback(function() if stage==0 then stage=1 t=0 end end, emu.callbackType.exec, 0x{title:06X}, 0x{title:06X})
"""


if __name__ == "__main__":
    romp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    rom = open(romp, "rb").read()
    base = find(rom, USA_CHECK)
    TITLE = find(rom, TITLE_POLL)
    os.makedirs(out, exist_ok=True)
    script = os.path.join(out, "fuzz.lua")
    open(script, "w").write(lua(base, TITLE))
    p = subprocess.run([sys.executable, os.path.join(HERE, "mesen.py"), script, romp], capture_output=True, text=True)
    line = next((l for l in p.stdout.splitlines() if l.startswith("RES ")), None)
    if not line:
        sys.exit(p.stdout[-2000:])
    got = dict(x.split(":") for x in line[4:].split())
    bad = 0
    for code, v in got.items():
        want = password.decode(code)
        if (int(v) if int(v) >= 0 else None) != (want["index"] if want else None):
            bad += 1
            print("MISMATCH", code, v, want)
    ok = sum(int(v) >= 0 for v in got.values())
    print(f"{os.path.basename(romp)}: check at ${base:06X}, {len(got)} codes run, {ok} accepted, {bad} mismatches")
