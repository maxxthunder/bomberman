-- Bomberman '94: log reads of the two asset-pointer lists in bank $03 (file $6000 and $65E4) through MPR2-5:
-- "SC frame=<n> slot=<s> table=<0|1> rec=<index> pc=<pc>". Prepend to tour94.lua / stages94.lua / ending94.lua.
local F=0 emu.addEventCallback(function() F=F+1 end, emu.eventType.endFrame)
local last=''
for s=2,5 do local key='memoryManager.mpr['..s..']'
  for t,rg in ipairs({{0x0000,0x0159},{0x05E4,0x0746}}) do
    emu.addMemoryCallback(function(addr)
      if emu.getState()[key]==3 then local i=((addr&0x1FFF)-rg[1])>>1 local k=t..':'..i
        if k~=last then last=k print(string.format('SC frame=%d slot=%d table=%d rec=%d pc=%04x', F, s, t-1, i, emu.getState()['cpu.pc'])) end end
    end, emu.callbackType.read, s*0x2000+rg[1], s*0x2000+rg[2])
  end
end
