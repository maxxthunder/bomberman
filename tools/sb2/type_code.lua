-- Type CODE on the password screen with real button presses (Up = digit+1, Right = next digit), press
-- START, then print what the game set. python tools/sb2/run.py tools/sb2/type_code.lua rom CODE=6763
local R=function(a) return emu.read(a,emu.memType.snesMemory) end
title(function()
  wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
  local s='CODE'
  for i=1,4 do for k=1,tonumber(s:sub(i,i)) do press({up=true},3) end press({right=true},3) end
  press({start=true},6) wait(700)
  at(function() print(string.format('R CODE 1A=%02X idx=%d 1C68=%04X speed=%d bombs=%d fire=%d type=%d glove=%d',
    R(0x1A), R(0x1C6A), R(0x1C68)+256*R(0x1C69), R(0x7E80E0), R(0x7E80E1), R(0x7E80E2), R(0x7E80F3), R(0x7E80FE))) shot('code_CODE') end)
end)
