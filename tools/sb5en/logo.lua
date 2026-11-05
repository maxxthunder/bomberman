-- Dump PPU layer settings, VRAM and CGRAM at the title screen for bgrender.py.
-- Usage: cat ../sb5/lib.lua logo.lua > t.lua; run.sh t.lua [caravan] > dump.out; python ../sb5/bgrender.py dump.out out
to_title() wait(30)
at(function()
  local s=emu.getState() for k,v in pairs(s) do if k:find('ppu.layers') or k:find('bgMode') then print(k..'='..tostring(v)) end end
  local t={} for a=0,0xFFFF do t[#t+1]=string.format('%02x',emu.read(a,emu.memType.snesVideoRam)) end print('VRAM '..table.concat(t))
  t={} for a=0,0x1FF do t[#t+1]=string.format('%02x',emu.read(a,emu.memType.snesCgRam)) end print('CGRAM '..table.concat(t))
end)
