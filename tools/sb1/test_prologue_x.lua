-- set PRESSES first (48+ needed; 40 is not enough). US: redirects NORMAL GAME into the cut prologue ($A4=$33)
-- Normal Game, but redirect the next scene to $33 (the Japanese prologue) and press X every 8 frames
wait(700)
at(function() emu.addMemoryCallback(function() if not done then emu.write(0xA4,0x33,W) done=true end end, emu.callbackType.exec, 0xC55026, 0xC55026) end)
press({start=true},4) wait(120) S('c1')
for i=1,PRESSES do press({x=true},2) if i==24 then S('c2') end end
at(function() print('C8F',emu.read(0xC8F,W),'C96',emu.read(0xC96,W),'A4',string.format('%02x',emu.read(0xA4,W))) end) S('c3')
wait(1500) S('c4') at(function() print('A4',string.format('%02x',emu.read(0xA4,W)),'lives',emu.read(0xD7D,W)) end)
press({start=true},4) wait(100) press({start=true},4) wait(900) S('c5')
at(function() print('A4',string.format('%02x',emu.read(0xA4,W)),'lives',emu.read(0xD7D,W),'C8F',emu.read(0xC8F,W)) end)
