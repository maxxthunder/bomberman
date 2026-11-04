-- Check the encoder ($1AF48): enter each code in CODES, start the area, set lives ($3704) to 0, drop a bomb and stand
-- on it. The GAME OVER screen encodes the state; the hook after the number-to-digits call ($1AFC3) logs the code as
-- shown (leftmost digit = $2FCC, the ones). Needs codes.lua's pw_type (run.sh prepends only lib.lua, so it is here too).
function pw_type(s)
  for i=1,4 do local d=tonumber(s:sub(i,i))
    if d<=5 then for k=1,d do press({up=true},3) end else for k=d,9 do press({down=true},3) end end
    if i<4 then press({right=true},3) end end
  press({i=true})
end
local cur=''
emu.addMemoryCallback(function()
  if emu.convertAddress(emu.getState()['cpu.pc'], emu.memType.pceMemory).address==0x1AFC3 then
    print(string.format('G %s -> %d%d%d%d', cur, r8(0x2FCC), r8(0x2FCB), r8(0x2FCA), r8(0x2FC9))) end
end, emu.callbackType.exec, 0xAFC3, 0xAFC3)
for c in CODES:gmatch('%d+') do
  at(function() cur=c end) loadfile('pw.mst') wait(4) pw_type(c) wait(430)
  for k=1,14 do press({run=true}) wait(24) end
  wait(700) at(function() shot(c..'_in') w8(0x3704,0) end) press({i=true}) wait(300) press({i=true}) wait(900) at(function() shot(c..'_over') end)
end
