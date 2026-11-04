-- Normal Game 1-1; when Start would pause (C6:001B), jump to the unreferenced debug-menu entry C6:00D2 instead
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(700)
at(function() emu.addMemoryCallback(function()
  if not hooked then hooked=true local s=emu.getState() print('hook Y',s['cpu.y'],'X',s['cpu.x']) emu.setState({['cpu.pc']=0x00D2})
    emu.addEventCallback(function() for i=0,0x67F do emu.write(0xB180+i, emu.read(0x2180+i,W), emu.memType.snesVideoRam) end end, emu.eventType.endFrame) end
end, emu.callbackType.exec, 0xC6001B, 0xC6001B) end)
press({start=true},2) wait(60) S('d1')
press({down=true},2) wait(10) press({right=true},2) wait(20) S('d2')
for i=1,3 do press({down=true},2) wait(6) end press({right=true},2) press({right=true},2) wait(20) S('d3')
at(function() local s=emu.getState() print('pc',string.format('%02x%04x',s['cpu.k'],s['cpu.pc']),'0314',emu.read(0x314,W)) end)
