-- Turn on the disabled debug menu switch ($C1:5B3E, operand byte $C1:5B40), start stage 1-1 by password,
-- press SELECT: the menu opens. python tools/sb2/run.py tools/sb2/debug_menu.lua rom
emu.write(0x15B40,1,emu.memType.snesPrgRom)
title(function()
  wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
  pw('4361') wait(5) press({start=true},6) wait(600)
  press({select=true},6) wait(30) at(function() shot('debug_menu') end)
end)
