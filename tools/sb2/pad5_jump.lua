-- Multitap jump trick with a real multitap: needs a Mesen whose settings put a Multitap in SNES port 2
-- (Snes.Port2.Type = "Multitap" in settings.json). Pads 2-5 are multitap ports A-D.
-- In this Mesen build emu.setInput(input, 0, 1, N) drives multitap port N (0-3), so pad 5 = (0,1,3);
-- the game reads it through the multitap protocol ($4201 bit 7 / $4017), no RAM is touched.
-- Moves the title cursor to BATTLE GAME with pad 1, presses A on pad PAD (1, 4 or 5), goes to a battle,
-- prints $1C6E, presses Y on pad 1 and takes shots p<PAD>_0/1/2.
-- python tools/sb2/run.py tools/sb2/pad5_jump.lua rom PAD=5   (PAD=1 / PAD=4: control runs)
local n=0
emu.addEventCallback(function() if n>0 then emu.setInput({a=true},0,1,PAD-2) n=n-1 end end, emu.eventType.inputPolled)
title(function()
  wait(60) press({down=true},6) wait(20)
  if PAD==1 then press({a=true},6) else at(function() n=6 end) wait(12) end
  wait(150)
  for i=1,5 do press({a=true},6) wait(150) end
  wait(180)
  at(function() print('R pad PAD 1C6E', emu.read16(0x1C6E,emu.memType.snesMemory)) shot('pPAD_0') end)
  q[#q+1]={y=true} q[#q+1]={y=true} wait(6) at(function() shot('pPAD_1') end) wait(10) at(function() shot('pPAD_2') end)
end)
