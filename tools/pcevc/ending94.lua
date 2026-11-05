-- Bomberman '94: open the Debug Version menu (ROM $3F5B patch in memory, as tools/pce94/soundtest.lua DEBUG=1),
-- pick ITEM (1 STAGE SELECT, 2 BOSS BATTLE, 3 IMPRESSIVE ENDING, 4 SOUND MODE) and take a shot every STEP frames
-- for FRAMES frames, pressing Run every PRESS frames (0 = never). run.sh pce94 <rom> ending94.lua ITEM=3
local p={0x29,0x85,0x67,0xA9,0x98}
for i=1,5 do emu.write(0x3F5A+i, p[i], emu.memType.pcePrgRom) end
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
for _,b in ipairs({{right=true},{left=true},{left=true,down=true},{down=true},{down=true,right=true},{down=true,right=true,ii=true}}) do
  for i=1,8 do q[#q+1]=b end
end
wait(150)
for i=1,(ITEM or 3)-1 do press({down=true},4) wait(10) end
press({run=true})
local n=0
for f=1,(FRAMES or 6000),(STEP or 60) do
  if (PRESS or 0)>0 and f%PRESS<(STEP or 60) then press({run=true}) wait((STEP or 60)-10) else wait(STEP or 60) end
  n=n+1 local k=n at(function() shot(string.format('e%03d',k)) end)
end
