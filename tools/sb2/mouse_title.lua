-- Title screen with a SNES Mouse in port 2: tap START, then A, and see whether the menu reacts.
for i=1,15 do press({start=true},4) wait(56) end
at(function() shot('m1') print('R 1FFE', emu.read16(0x1FFE,emu.memType.snesMemory)) end)
press({a=true},6) wait(200) at(function() shot('m2') end)
press({start=true},6) wait(200) at(function() shot('m3') end)
