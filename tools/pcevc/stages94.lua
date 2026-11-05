-- Bomberman '94: start every stage from the Debug Version's STAGE SELECT (patched in memory, see ending94.lua) and
-- shoot it 300 frames in (s<nn>.png). Prepend romreads94.lua to log which changed ROM pages each stage reads.
-- run.sh pce94 <rom> stages94.lua [FIRST=0 LAST=19]
local p={0x29,0x85,0x67,0xA9,0x98}
for i=1,5 do emu.write(0x3F5A+i, p[i], emu.memType.pcePrgRom) end
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
for _,b in ipairs({{right=true},{left=true},{left=true,down=true},{down=true},{down=true,right=true},{down=true,right=true,ii=true}}) do
  for i=1,8 do q[#q+1]=b end
end
wait(150) press({run=true}) wait(120) savefile('stagesel.mst')
for s=(FIRST or 0),(LAST or 19) do
  loadfile('stagesel.mst') wait(4) q[#q+1]={} wait(4)
  at(function() print(string.format('STAGE %02x', s)) end)
  for i=1,s do press({down=true},3) wait(4) end
  at(function() shot(string.format('sel%02d', s)) end)
  press({run=true}) wait(300) at(function() shot(string.format('s%02d', s)) end)
end
