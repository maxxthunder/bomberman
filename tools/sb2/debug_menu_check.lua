-- Debug menu checks on a ROM patched with patches/sb2_debug_menu_<ver>.ips (no RAM or ROM writes here).
-- Stage 1-1 by password, SELECT opens the menu, then:
--   TEST=1 navigation: cursor wrap, every line's range and wrap, printed after each tap
--   TEST=2 FIRE 3, BOMB TYPE = 2^(CNT-1) (CNT Right taps, 0 = none), close, lay a bomb (A), shots bt<CNT>_<i>
--   TEST=3 NO DEATH = CNT (1 on, 0 off), close, lay a bomb and stand on it, print hearts, shots nd<CNT>_<i>
-- python tools/sb2/run.py tools/sb2/debug_menu_check.lua patched.sfc TEST=1 CNT=0
local R=function(a) return emu.read(a,emu.memType.snesMemory) end
local function st(tag) print(string.format('R %s cur=%d stage=%02X fire=%d bomb=%d type=%d | 1A=%02X speed=%d bombs=%d fire=%d hearts=%d type=%d FA=%d FB=%d FE=%d FF=%d',
  tag, R(0x7E5D50), R(0x7E5D42), R(0x7E5D46), R(0x7E5D48), R(0x7E5D4A), R(0x1A), R(0x7E80E0), R(0x7E80E1), R(0x7E80E2),
  R(0x7E80EF), R(0x7E80F3), R(0x7E80FA), R(0x7E80FB), R(0x7E80FE), R(0x7E80FF))) end
local function tap(b,n,tag) for i=1,(n or 1) do press(b,2) wait(4) end if tag then at(function() st(tag) end) end end
local U,D,L,Rt={up=true},{down=true},{left=true},{right=true}
title(function()
  wait(60) press(D,6) wait(20) press(D,6) wait(20) press({a=true},6) wait(200)
  pw('4361') wait(5) press({start=true},6) wait(600)
  at(function() st('before') end)
  press({select=true},6) wait(30) at(function() st('open') end)
  if TEST==1 then
    tap(U,1,'up-from-0') tap(D,1,'down-from-8')
    tap(L,1,'stage-left-from-1-0') tap(Rt,1,'stage-right-from-6-0') tap(Rt,8,'stage-right-x8') tap(L,8,'stage-back')
    tap(D) tap(Rt,1,'nodeath-right') tap(L,1,'nodeath-left')
    tap(D) tap(L,1,'fire-left-from-0') tap(Rt,1,'fire-right-from-9')
    tap(D) tap(L,1,'bomb-left-from-1') tap(Rt,1,'bomb-right-from-9')
    tap(D) for i=1,5 do tap(Rt,1,'type-right') end tap(L,1,'type-left-from-0') tap(L,1,'type-left-from-8')
    tap(D) tap(Rt,1,'itemfull-right') tap(L,1,'itemfull-left')
    for i=1,3 do tap(D) tap(Rt,1,'dash-right') tap(L,1,'dash-left') end
    at(function() shot('dbg_nav') end)
    press({start=true},6) wait(60) at(function() st('closed') end)
  elseif TEST==2 then
    tap(D,2) tap(Rt,3) tap(D,2) tap(Rt,CNT,'type') press({start=true},6) wait(60) press({start=true},6) wait(60)  -- START closes the menu, the game is left paused
    press({a=true},8) at(function() st('laid') end)
    for i=1,8 do wait(25) at(function() shot('btCNT_'..i) end) end
  else
    tap(D) if CNT==1 then tap(Rt,1,'nodeath') end press({start=true},6) wait(60) press({start=true},6) wait(60)  -- START closes the menu, the game is left paused
    wait(300) press({a=true},8)  -- after the start-of-stage blinking
    for i=1,8 do wait(60) at(function() st('nd'..i) shot('ndCNT_'..i) end) end
  end
end)
