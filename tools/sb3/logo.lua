-- Dump VRAM/CGRAM/OAM/PPU state on the title screen (frame 1240) for vram.py. Run with tools/sb3/run.sh logo.lua [eu|jp|beta].
function memhex(mt,n) local t={} for a=0,n-1 do t[#t+1]=string.format('%02x',emu.read(a,mt)) end return table.concat(t) end
wait(1240) at(function() shot('title')
 print('VRAM '..memhex(emu.memType.snesVideoRam,0x10000)) print('CGRAM '..memhex(emu.memType.snesCgRam,0x200)) print('OAM '..memhex(emu.memType.snesSpriteRam,0x220))
 local s=emu.getState() local ks={} for k,v in pairs(s) do if k:find('^ppu') and not k:find('ppu%.vram') and type(v)~='table' then ks[#ks+1]=k..'='..tostring(v) end end table.sort(ks) print('PPU '..table.concat(ks,' ')) end)
