-- PAR code checks in Mesen's cheat engine (SB3). Prepend cdl.lua, pw.lua, battle.lua; set T and CODES.
at(function() for c in string.gmatch(CODES or '', '%S+') do emu.addCheat(emu.cheatType.snesProActionReplay, c) end end)
RST=0 emu.addMemoryCallback(function() RST=RST+1 end, emu.callbackType.exec, 0x80F000, 0x80F000)
if T=='reset' then
  to_password() wait(30) pw_enter('5358') wait(600) at(function() print('before', RST, r8(0x0346)) end)
  press({select=true,start=true,l=true,r=true},6) wait(200) at(function() print('after', RST) shot('reset') end)
elseif T=='stages' then
  to_password() wait(30) pw_enter('1511') to_stage_select() at(function() print('N', r8(0x542D), r8(0x6C6E)) end)
  press({left=true}) wait(40) at(function() print('LEFT', r8(0x6C6E)) shot('left') end)
elseif T=='kit' then
  to_password() wait(30) pw_enter('5358') wait(700)
  at(function() local t={} for x=0,31 do t[#t+1]=r8(0x12E7+x) end print('HP', table.concat(t,' '), 'bombs', r8(0x144F), 'fire', r8(0x48B9), 'spd', r8(0x126F), 'ab', r8(0x48D1)) end)
end
