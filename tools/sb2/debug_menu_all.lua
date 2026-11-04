-- Debug menu, every line: ROM switch $C1:5B40 = 1, stage 1-1 by password, SELECT opens the menu, then set
-- NO DEATH on, FIRE 3, BOMB 3, BOMB TYPE 2, ITEM FULL on, close with START and print the player's RAM.
-- Taps (not holds), so each Right is one step. python tools/sb2/run.py tools/sb2/debug_menu_all.lua rom
local R=function(a) return emu.read(a,emu.memType.snesMemory) end
local function dumpkit(tag) print(string.format('R %s 1A=%02X speed=%d bombs=%d fire=%d hearts=%d type=%d FA=%d FB=%d FE=%d FF=%d cursor=%d',
  tag, R(0x1A), R(0x7E80E0), R(0x7E80E1), R(0x7E80E2), R(0x7E80EF), R(0x7E80F3), R(0x7E80FA), R(0x7E80FB), R(0x7E80FE), R(0x7E80FF), R(0x7E5D50))) end
emu.write(0x15B40,1,emu.memType.snesPrgRom)
local function tap(b,n) for i=1,(n or 1) do press(b,2) wait(4) end end
title(function()
  wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
  pw('4361') wait(5) press({start=true},6) wait(600)
  at(function() dumpkit('before') end)
  press({select=true},6) wait(30)
  tap({down=true}) tap({right=true})        -- NO DEATH ON
  tap({down=true}) tap({right=true},3)      -- FIRE 3
  tap({down=true}) tap({right=true},2)      -- BOMB 3
  tap({down=true}) tap({right=true},2)      -- BOMB TYPE 2
  tap({down=true}) tap({right=true})        -- ITEM FULL ON
  at(function() dumpkit('menu') shot('dbg_all_menu') end)
  tap({down=true},4) at(function() dumpkit('wrap') end)   -- 4 more: past the three '-' lines back to line 0
  press({start=true},6) wait(60)
  at(function() dumpkit('after') shot('dbg_all_after') end)
end)
