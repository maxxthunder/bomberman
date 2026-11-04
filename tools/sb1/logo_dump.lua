-- dumps VRAM/CGRAM/OAM/PPU regs on the title for vram_render.py (logo rip)
function memhex(mt,n) local t={} for a=0,n-1 do t[#t+1]=string.format('%02x',emu.read(a,mt)) end return table.concat(t) end
wait(700)
at(function()
  local s=emu.getState()
  print('VRAM '..memhex(emu.memType.snesVideoRam,0x10000))
  print('CGRAM '..memhex(emu.memType.snesCgRam,0x200))
  print('OAM '..memhex(emu.memType.snesSpriteRam,0x220))
  local t={} for i=0,3 do for _,k in ipairs({'chrAddress','tilemapAddress','hscroll','vscroll','largeTiles','doubleWidth','doubleHeight'}) do t[#t+1]=i..k..'='..tostring(s['ppu.layers['..i..'].'..k]) end end
  print('REGS '..table.concat(t,' ')..' oamBase='..s['ppu.oamBaseAddress']..' oamOff='..s['ppu.oamAddressOffset']..' oamMode='..s['ppu.oamMode'])
  shot('title')
end)
