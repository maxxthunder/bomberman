-- Helpers shared by the pce94 scripts (prepended by run.sh after the mesen.py prelude).
-- Savestates can only be made inside an exec callback, so the VDC IRQ handler ($E133, bank 0 is always at $E000)
-- does it on request: want='save' / want='load'.
want=nil st=nil
emu.addMemoryCallback(function()
  if want=='save' then st=emu.createSavestate() elseif want=='load' then emu.loadSavestate(st) end want=nil
end, emu.callbackType.exec, 0xE133, 0xE133)
function savefile(name) at(function() want='save' end) wait(2) at(function() local f=io.open(STATES..name,'wb') f:write(st) f:close() end) end
function loadfile(name) at(function() local f=io.open(STATES..name,'rb') st=f:read('a') f:close() want='load' end) wait(2) end
