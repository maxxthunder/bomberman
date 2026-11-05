-- Dump the collision map $7F:C000-$7F:C7FF (32 x 32 tiles of 8 px, one word each, low byte = the tile's
-- collision code, built at $C0:F71B from the BG map $7F:E000 through the stage's tile-attribute table) of every
-- Normal Game stage and every battle stage, plus a screenshot. Normal Game: the debug menu (PAR C15B4001) steps
-- STAGE NO. one up per stage. Battle: BATTLE=1, stage select with $1CB5 set, then a reset.
-- python tools/sb2/run.py tools/sb2/map_dump.lua rom.sfc [BATTLE=1 (replaces the word BATTLE)] > out; python tools/sb2/maps.py out docs/img/sb2/maps
local M=emu.memType.snesMemory
local function dumpmap(tag) at(function()
  local t={} for a=0x7FC000,0x7FC7FF,2 do t[#t+1]=string.format('%02x',emu.read(a,M)) end
  print(string.format('MAP %s %02x ',tag,emu.read(0x1A,M))..table.concat(t))
  shot('map_'..tag) end) end
title(function()
  if BATTLE~=1 then
    at(function() emu.addCheat(emu.cheatType.snesProActionReplay,'C15B4001') emu.addCheat(emu.cheatType.snesProActionReplay,'7E80EF90') end)  -- debug menu, NO DEATH
    wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
    pw('4361') wait(5) press({start=true},6) wait(700) dumpmap('10')
    for s=1,44 do
      press({select=true},6) wait(20) press({right=true},3) wait(6) press({start=true},6) wait(20) press({start=true},6)
      wait(600) at(function() end) dumpmap(string.format('n%02d',s))
    end
  else
    for s=1,12 do
      at(function() emu.write16(0x1CB5,0xFFFF,M) end)
      wait(30) press({down=true},6) wait(20) press({a=true},6) wait(150)
      for i=1,4 do press({a=true},6) wait(150) end
      for k=1,s-1 do press({right=true},3) wait(8) end
      press({a=true},6) wait(300) dumpmap(string.format('b%02d',s))
      at(function() emu.reset() end) wait(2900)
    end
  end
  at(stop)
end)
