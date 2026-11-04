-- JP: wait on the title for the native prologue, press X every 8 frames, log $A4/$0C8F
local last=-1
at(function() emu.addEventCallback(function() local a=emu.read(0xA4,W) local c=emu.read(0xC8F,W) if a*256+c~=last then last=a*256+c print(string.format('f=%d A4=%02x C8F=%d', emu.getState()['ppu.frameCount'], a, c)) end end, emu.eventType.endFrame) end)
wait(400) for i=1,700 do press({x=true},2) end
S('end')
