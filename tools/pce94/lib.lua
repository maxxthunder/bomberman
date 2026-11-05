-- Helpers shared by the pce94 scripts (prepended by run.sh after the tools/emu/mesen.py prelude).
-- r8/w8: work RAM ($2000-$3FFF logical = pceWorkRam); dump(name, memType[, n]) -> <name>.bin; pad buttons are
-- i, ii, select, run, up, down, left, right
function r8(a) return emu.read(a & 0x1FFF, emu.memType.pceWorkRam) end
function w8(a,v) emu.write(a & 0x1FFF, v, emu.memType.pceWorkRam) end
function dump(name, mt, n) local t={} for a=0,(n or emu.getMemorySize(mt))-1 do t[#t+1]=string.format('%02x',emu.read(a,mt)) end print('DUMP '..name..' '..table.concat(t)) end
qi=1  -- input queue: one entry per frame (a button table or a function to run); qi = next entry
function tick()
  local s=q[qi] qi=qi+1
  if s==nil then emu.stop(0) return end
  while type(s)=="function" do s() s=q[qi] or {} qi=qi+1 end
  emu.setInput(s,0)
end
-- Savestates can only be made inside an exec callback, so the VDC IRQ handler ($E133, bank 0 is always at $E000)
-- does it on request: want='save' / want='load'.
want=nil st=nil
emu.addMemoryCallback(function()
  if want=='save' then st=emu.createSavestate() elseif want=='load' then emu.loadSavestate(st) end want=nil
end, emu.callbackType.exec, 0xE133, 0xE133)
function savefile(name) at(function() want='save' end) wait(2) at(function() local f=io.open(STATES..name,'wb') f:write(st) f:close() end) end
function loadfile(name) at(function() local f=io.open(STATES..name,'rb') st=f:read('a') f:close() want='load' end) wait(2) end
