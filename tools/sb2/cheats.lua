-- Pro Action Replay checks on the unpatched ROM through Mesen's cheat engine (emu.addCheat), real presses only.
-- python tools/sb2/run.py tools/sb2/cheats.lua rom.sfc TEST=inv   (tests in CODES; see tools/sb2/cheats.sh)
-- Normal-Game tests type 4361 on the password screen, lay a bomb under player 1 and stand on it.
-- Battle tests go BATTLE GAME -> A through the setup screens -> stage select.
local CODES={
  none={}, inv={'7E80EF90'},
  kit={'7E80E003','7E80E109','7E80E209','7E80F304','7E80FA01','7E80FB01','7E80FE01','7E80FF01'},
  stages={'7E1CB5FF','7E1CB6FF'}, jump={'7E1C6EFF','7E1C6FFF'}, sudden={'7E1C68FF','7E1C69FF'},
}
local M=emu.memType.snesMemory
for _,c in ipairs(CODES[TEST]) do local ok,e=pcall(emu.addCheat,emu.cheatType.snesProActionReplay,c) print('cheat',c,ok,e) end
local function st(tag) at(function() print(string.format('%s stage=%02x hearts=%02x spd=%d bombs=%d fire=%d type=%d pass=%d,%d glove=%d kick=%d 1CB5=%04x 1C6E=%04x 1C68=%04x 1CCD=%d',
  tag,emu.read(0x1A,M),emu.read(0x7E80EF,M),emu.read(0x7E80E0,M),emu.read(0x7E80E1,M),emu.read(0x7E80E2,M),emu.read(0x7E80F3,M),
  emu.read(0x7E80FA,M),emu.read(0x7E80FB,M),emu.read(0x7E80FE,M),emu.read(0x7E80FF,M),emu.read16(0x1CB5,M),emu.read16(0x1C6E,M),emu.read16(0x1C68,M),emu.read16(0x1CCD,M))) end) end
local function digit(n) for i=1,n do press({up=true},3) wait(3) end end
title(function()
  if TEST=='stages' or TEST=='jump' or TEST=='sudden' then
    wait(30) press({down=true},6) wait(20) press({a=true},6) wait(150)
    for i=1,4 do press({a=true},6) wait(150) end   -- battle type, players, settings: now the stage select
    press({left=true},6) wait(30) st('select') at(function() shot('cheat_'..TEST..'_select') end)
    press({right=true},6) wait(30) press({a=true},6) wait(500) st('battle')
    for i=1,3 do press({y=true},3) wait(4) end at(function() shot('cheat_'..TEST..'_battle') end) wait(60) st('end')
  else
    wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
    digit(4) press({right=true},3) digit(3) press({right=true},3) digit(6) press({right=true},3) digit(1) press({start=true},6)
    wait(700) st('start') at(function() shot('cheat_'..TEST..'_start') end)
    press({b=true},4) press({a=true},4) wait(20) press({down=true},12) press({right=true},12) wait(40) press({b=true},4) press({a=true},4)
    wait(40) at(function() shot('cheat_'..TEST..'_blast') end) wait(300) st('after') at(function() shot('cheat_'..TEST..'_after') end)
  end
  at(stop)
end)
