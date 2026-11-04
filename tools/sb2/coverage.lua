-- Code/data-log coverage run for the unused-graphics sweep (tools/sb2/unused_gfx.py). Needs a ROM patched with
-- patches/sb2_debug_menu_<ver>.ips. ROUTE=1: Normal Game 1-1, then the debug menu's STAGE NO. warps through
-- every stage up to 6-0 (ending and credits), laying a bomb in each with NO DEATH on. ROUTE=2: Normal Game
-- without the menu, blow yourself up until GAME OVER and the continue/password screen. ROUTE=3: Battle Game,
-- every stage 1-12 ($1CB5 set in RAM), each played for a while, then the results screens.
-- Prints 'CDL <hex>' at the end; python tools/sb2/run.py tools/sb2/coverage.lua patched.sfc ROUTE=1 > log
local function cdl() local c=emu.getCdlData(emu.memType.snesPrgRom) local t={} for i=1,#c do t[#t+1]=string.format('%02x',c[i]) end print('CDL '..table.concat(t)) end
local function bomb() press({a=true},8) wait(200) end
title(function()
  if ROUTE==1 then
    wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
    pw('4361') wait(5) press({start=true},6) wait(900)
        for s=1,40 do
      press({select=true},6) wait(20) press({right=true},3) wait(4) press({down=true},3) wait(4) press({right=true},3) wait(4) press({up=true},3) wait(4) press({start=true},6)
      wait(900) at(function() shot('cov_n'..s) end) press({select=true},6) wait(20) press({down=true},3) wait(4) press({right=true},3) wait(4) press({up=true},3) wait(4) press({start=true},6) wait(20) press({start=true},6) wait(30) bomb() press({left=true},30) press({up=true},30) bomb()
    end
    wait(20000)  -- ending and credits
  elseif ROUTE==2 then
    wait(60) press({a=true},6) wait(900)
    for i=1,5 do bomb() wait(700) end
    for i=1,6 do press({down=true},6) wait(200) press({a=true},6) wait(400) end
  else
    for s=1,12 do
      at(function() emu.write16(0x1CB5,0xFFFF,emu.memType.snesMemory) end)
      wait(30) press({down=true},6) wait(20) press({a=true},6) wait(150)
      for i=1,4 do press({a=true},6) wait(150) end   -- battle type, players, settings: now on the stage select
      for k=1,s-1 do press({right=true},3) wait(8) end
      press({a=true},6) wait(400) at(function() shot('cov_b'..s) end) bomb() press({right=true},20) bomb() press({down=true},20) bomb() wait(3000)
      for k=1,8 do press({a=true},6) wait(200) end   -- results, trophy
      if s<12 then at(function() emu.reset() end) wait(2900) end   -- intro plays out, title menu ready
    end
  end
  at(cdl)
end)
