-- PAR code checks in Mesen's cheat engine (SB4). Prepend lib.lua (job.sh); set T and CODES (space-separated 8-digit PAR codes).
at(function() for c in string.gmatch(CODES or '', '%S+') do emu.addCheat(emu.cheatType.snesProActionReplay, c) end end)
local M=emu.memType.snesMemory
if T=='pause' then
  to_pw() typepw('7352') press({start=true}) wait(450) press({start=true}) wait(300) press({start=true}) wait(30) at(function() shot('pause') end)
elseif T=='stages' then
  to_stage() at(function() print('SEL', emu.read(0x7F202B,M), emu.read(0x7F202D,M)) end) press({left=true}) wait(30) at(function() print('LEFT', emu.read(0x7F202B,M)) shot('left') end)
  press({left=true}) wait(30) at(function() print('LEFT2', emu.read(0x7F202B,M)) shot('left2') end)
elseif T=='filler' then
  to_pw() typepw(PW) press({start=true}) wait(450) press({start=true}) wait(300) at(function() print('IDX', rd(0x92)) shot('f'..PW) end)
elseif T=='inv' then
  to_pw() typepw('7352') press({start=true}) wait(450) press({start=true}) wait(200)
  press({b=true}) wait(400) at(function() shot('inv1') print('LIVES?', rd(0x03D2), rd(0x1F2A)) end) wait(400) at(function() shot('inv2') end)
end
