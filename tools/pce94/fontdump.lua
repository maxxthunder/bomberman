-- Save the ASCII font tiles ($100-$17F, VRAM bytes $2000-$2FFF) from the Debug Version menu to <scratch>/font.bin for
-- debugpause.lua FONT=1. Applies the known patch in memory and enters the Sound Room code to reach that menu.
local p={0x29,0x85,0x67,0xA9,0x98}
for i=1,5 do emu.write(0x3F5A+i, p[i], emu.memType.pcePrgRom) end
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
for _,b in ipairs({{right=true},{left=true},{left=true,down=true},{down=true},{down=true,right=true},{down=true,right=true,ii=true}}) do
  for i=1,8 do q[#q+1]=b end
end
wait(200) at(function() shot('dbg') local t={} for a=0x2000,0x2FFF do t[#t+1]=string.char(emu.read(a,emu.memType.pceVideoRam)) end
 local f=io.open(STATES..'font.bin','wb') f:write(table.concat(t)) f:close() print('font saved') end)
