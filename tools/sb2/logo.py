"""Rip the title logo from VRAM/CGRAM: boot in Mesen, dump the PPU once the title menu is polling input,
render BG1 (logo and menu text live there) with colour 0 transparent, crop to the logo, save indexed PNG.
Usage: python tools/sb2/logo.py <rom.sfc> <out.png> [workdir]   (MESEN = path to Mesen.exe)"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bgrender
from fuzz import find, TITLE_POLL

LUA = """
hold=true local f=0 local n=0
emu.addEventCallback(function() f=f+1 pad=(f%%60<5 and n==0) and {start=true} or {} if f>4000 then emu.stop(1) end end, emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 n=n+1 if n~=120 then return end
 local s=emu.getState() local ks={} for k,v in pairs(s) do if k:find('^ppu') then ks[#ks+1]=k..'='..tostring(v) end end print('ST '..table.concat(ks,' '))
 local t={} for a=0,0xFFFF do t[#t+1]=string.format('%%02x',emu.read(a,emu.memType.snesVideoRam)) end print('VRAM '..table.concat(t))
 t={} for a=0,0x1FF do t[#t+1]=string.format('%%02x',emu.read(a,emu.memType.snesCgRam)) end print('CGRAM '..table.concat(t))
 emu.stop(0)
end, emu.callbackType.exec, 0x%06X, 0x%06X)
"""

if __name__ == "__main__":
    romp, outp = sys.argv[1], sys.argv[2]
    work = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
    os.makedirs(work, exist_ok=True)
    t = find(open(romp, "rb").read(), TITLE_POLL)
    script = os.path.join(work, "logo.lua")
    open(script, "w").write(LUA % (t, t))
    p = subprocess.run([sys.executable, os.path.join(HERE, "mesen.py"), script, romp], capture_output=True, text=True)
    dump = os.path.join(work, "ppu.txt")
    open(dump, "w").write("\n".join(l for l in p.stdout.splitlines() if l[:3] in ("ST ", "VRA", "CGR")))
    img = bgrender.render(bgrender.load(dump), 0)
    top = img.crop((0, 0, 256, 140))  # the menu text starts below y=140
    top = top.crop(top.getbbox())
    pal = top.convert("RGB").quantize(colors=255)
    alpha = top.getchannel("A")
    q = pal.point(lambda i: i + 1)  # index 0 is transparent
    q.putpalette([0, 0, 0] + pal.getpalette()[:765])
    q.paste(0, mask=alpha.point(lambda a: 255 if a == 0 else 0))
    q.save(outp, transparency=0)
    print(outp, top.size)
