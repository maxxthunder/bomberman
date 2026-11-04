-- Emulate a turbo X on pad 1 at the title menu: PRESSES presses, PERIOD frames apart, then print the
-- hidden-stage flag $1CB5 ($FFFF = stages 11/12 unlocked). Needs 49 presses 7-9 frames apart.
-- python tools/sb2/run.py tools/sb2/joycard.lua rom PRESSES=49 PERIOD=8
title(function()
  wait(10)
  for i=1,PRESSES do q[#q+1]={x=true} wait(PERIOD-1) end
  wait(60) at(function() print('R presses PRESSES period PERIOD 1CB5', emu.read16(0x1CB5,emu.memType.snesMemory)) end)
end)
