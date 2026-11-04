-- 5656 in play: normal game 1-1 with ($7F70B7 set by typing 5656) or without the code. The rider type is put
-- in $0322 by hand (1), then the super attack (hold B, tap a direction) is tried every 40 frames.
-- job.sh <dir> "CODE=1" "$(cat super5656.lua)"
local function hook(pc,name) emu.addMemoryCallback(function() local s=emu.getState() if s['cpu.x']==0x300 then print(name, 'f'..(s.frameCount-(T0 or 0)), string.format('tired timer $03E2=%02x', rd(0x3E2))) end end, emu.callbackType.exec, pc, pc) end
hook(0xC2447D,'super attack')
if CODE then to_pw() typepw('5656') press({start=true}) wait(300) press({start=true}) wait(120) press({up=true}) wait(10) press({up=true}) wait(10)
else to_title() end
press({start=true}) wait(80) press({start=true}) wait(700)
at(function() print('$7F70B7 =', rd(0x170B7)) wr(0x322,1) T0=emu.getState().frameCount end)
for n=1,20 do for i=1,6 do q[#q+1]={b=true} end for i=1,3 do q[#q+1]={b=true,right=(n%2==1),left=(n%2==0)} end
  at(function() shot('a'..n) end) for i=1,30 do q[#q+1]={} end end
