-- Enter 5656, start a 1:00 battle, skip the hurry-up block counter $7E:5D12 to 74 and log it:
-- without the flag it stops at 81 (past the $FE marker), with it the blocks keep coming.
-- FLAG=0 clears $1C68 again for the control run. python tools/sb2/run.py tools/sb2/sudden_death.lua rom FLAG=1
local M=emu.memType.snesMemory
title(function()
  wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
  pw('5656') wait(5) press({start=true},6) wait(500)
  press({down=true},10) wait(30) press({a=true},10) wait(200)
  press({a=true},10) wait(150) press({a=true},10) wait(150)
  press({down=true},6) wait(20) press({down=true},6) wait(20) press({left=true},6) wait(20)
  press({a=true},10) wait(150) press({a=true},10) wait(150)
  if FLAG==0 then at(function() emu.write16(0x1C68,0,M) end) end
  wait(1920) at(function() emu.write16(0x7E5D12,74,M) end)
  for i=1,16 do wait(30) at(function() print('R time', emu.read16(0x7E5E06,M)*10+emu.read16(0x7E5E08,M), 'block', emu.read16(0x7E5D12,M)) end) end
  at(function() shot('sudden_death') end)
end)
