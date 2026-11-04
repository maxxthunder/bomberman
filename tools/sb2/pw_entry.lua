-- Password screen controls with real presses: prints the digits $7F:0028-2E and cursor $7F:0032 after each
-- step. Checks the start value, Down 0->9, Up 9->0, cursor stops at both ends, a wrong code (A) clears the
-- digits, and a right code typed with Down only is accepted with A.
-- python tools/sb2/run.py tools/sb2/pw_entry.lua rom
local R=function(a) return emu.read16(a,emu.memType.snesMemory) end
local function st(tag) print(string.format('R %s digits=%d%d%d%d cur=%d result=%d idx=%d 1C60=%d%d%d%d', tag,
  R(0x7F0028),R(0x7F002A),R(0x7F002C),R(0x7F002E),R(0x7F0032),R(0x7F0030),R(0x1C6A),R(0x1C60),R(0x1C62),R(0x1C64),R(0x1C66))) end
local function tap(b,n,tag) for i=1,(n or 1) do press(b,3) wait(3) end if tag then at(function() st(tag) end) end end
local U,D,L,Rt={up=true},{down=true},{left=true},{right=true}
title(function()
  wait(60) press(D,6) wait(20) press(D,6) wait(20) press({a=true},6) wait(200)
  at(function() st('start') shot('pw_start') end)
  tap(D,1,'down-from-0') tap(U,1,'up-from-9') tap(L,1,'left-at-first') tap(Rt,5,'right-x5') tap(Rt,1,'right-again')
  tap(U,3,'up-x3-last') press({a=true},6) wait(90) at(function() st('wrong-A') end)
  -- 9564 by Down only: 0 -1 = 9, 0 -5 = 5, 0 -4 = 6, 0 -6 = 4 (needs the cursor back at digit 1)
  tap(L,3,'left-x3') tap(D,1) tap(Rt) tap(D,5) tap(Rt) tap(D,4) tap(Rt) tap(D,6,'typed')
  press({a=true},6) wait(30) at(function() st('right-A') end)
end)
