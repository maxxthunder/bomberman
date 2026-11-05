-- Story-id and battle map capture (SB3). Prepend cdl.lua, pw.lua, battle.lua. WHICH='story' (ids FIRST..LAST forced at the
-- decoder's RTL $C2:67FC) or WHICH='battle' (stages 1-12 x arena variants 0-3).
if WHICH=='story' then
local S, want = nil, nil
emu.addMemoryCallback(function() if want=='save' then S=emu.createSavestate() elseif want=='load' then emu.loadSavestate(S) end want=nil end, emu.callbackType.exec, 0xC00024, 0xC00024)
local ID=nil
emu.addMemoryCallback(function() if ID then w8(0x5430,ID) w8(0x0346,ID) ID=nil end end, emu.callbackType.exec, 0xC267FC, 0xC267FC)
to_password() wait(30) at(function() want='save' end) wait(2)
for id=FIRST,LAST do
  at(function() want='load' end) wait(2)
  at(function() ID=id end) pw_enter('5358') wait(WAITF or 700)
  at(function() print('ID', id, r8(0x0346), r8(0x0349)) shot(string.format('s%02X', id)) end)
end
else
local S, want = nil, nil
emu.addMemoryCallback(function() if want=='save' then S=emu.createSavestate() elseif want=='load' then emu.loadSavestate(S) end want=nil end, emu.callbackType.exec, 0xC00024, 0xC00024)
PAR=nil
emu.addEventCallback(function() if PAR then w8(0x6C6E,PAR) end end, emu.eventType.endFrame)
to_password() wait(30) pw_enter('1511') to_stage_select() at(function() want='save' end) wait(2)
for v=0,3 do for stg=1,12 do
  at(function() want='load' PAR=stg end) wait(2) at(function() w8(0x542E, v) end)
  press({start=true}) wait(60) press({start=true}) wait(150) at(function() PAR=nil end) wait(300)
  at(function() print('B', v, stg, r8(0x6C6E), r8(0x542E)) shot(string.format('b%d_%02d', v, stg)) end)
end end
end
