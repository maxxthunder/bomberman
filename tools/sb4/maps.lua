-- Battle and normal-stage map capture (SB4). Prepend lib.lua (job.sh). WHICH='battle' (all 4 sets x 14 table entries,
-- writes $024A and $7F202B at the stage select) or WHICH='normal' (stage slots FIRST..LAST: $0092 forced at the password hit).
if WHICH=='battle' then
local S, want = nil, nil
emu.addMemoryCallback(function()
  if want == 'save' then S = emu.createSavestate() elseif want == 'load' then emu.loadSavestate(S) end
  want = nil end, emu.callbackType.exec, 0x00F001, 0x00F001)
local M=emu.memType.snesMemory
local function grab(tag) at(function()
  local p = rd(0x28) + rd(0x29)*256 + rd(0x2A)*65536
  local t={} for i=0,0x7FF do t[#t+1]=string.format('%02x', emu.read(p+i, M)) end
  print(string.format('GRID %s %06X %s', tag, p, table.concat(t))) shot(tag) end) end
to_stage() at(function() want='save' end) wait(2)
for set=0,3 do for stg=0,(LAST or 13) do
  at(function() want='load' end) wait(2)
  at(function() emu.write(0x00024A, set, M) emu.write(0x7F202B, stg, M) end)
  press({start=true}) wait(690) grab(string.format('b%d_%02d', set, stg))
end end
else
local S, want = nil, nil
emu.addMemoryCallback(function()
  if want == 'save' then S = emu.createSavestate() elseif want == 'load' then emu.loadSavestate(S) end
  want = nil end, emu.callbackType.exec, 0x00F001, 0x00F001)
local IDX=nil
emu.addMemoryCallback(function() if IDX then emu.write(0x92, IDX, W) emu.write(0x93, 0, W) IDX=nil end end, emu.callbackType.exec, 0xC2A9C9, 0xC2A9C9)
to_pw() typepw('7352') at(function() want='save' end) wait(2)
for i=FIRST,LAST do
  at(function() want='load' end) wait(2)
  at(function() IDX=i end) press({start=true}) wait(450) press({start=true}) wait(300) at(function() print('IDX',i,rd(0x92)) shot(string.format('n%02d',i)) end)
end
end
