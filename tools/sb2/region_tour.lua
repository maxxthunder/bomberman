-- Screen tour for the region comparison: same presses on every version, a shot at each screen and the
-- clock RAM printed. ROUTE=0 boot/intro (no input, shot every 150 frames), ROUTE=1 Normal Game, ROUTE=2 Battle Game (A through each menu), ROUTE=3 password screen.
-- python tools/sb2/run.py tools/sb2/region_tour.lua rom ROUTE=2
local R=function(a) return emu.read(a,emu.memType.snesMemory) end
local function clk(tag) print(string.format('R %s frame=%d clock=%d:%d%d', tag, emu.getState()['ppu.frameCount'] or -1, R(0x7E5E04), R(0x7E5E06), R(0x7E5E08))) end
if ROUTE==0 then for i=1,16 do wait(150) at(function() shot('i_'..i) end) end else title(function()
  at(function() shot('t_menu') end)
  if ROUTE==1 then
    press({a=true},6) wait(100) at(function() shot('n_card') end) wait(500) at(function() shot('n_stage') end)
    wait(600) at(function() shot('n_stage10s') end)
  elseif ROUTE==2 then
    press({down=true},6) wait(20) press({a=true},6) wait(150) at(function() shot('b_1') end)
    for i=2,6 do press({a=true},6) wait(150) at(function() shot('b_'..i) end) end
    wait(180) at(function() shot('b_7') clk('b0') end) wait(600) at(function() clk('b600') shot('b_8') end)
    wait(3000) at(function() clk('b3600') shot('b_9') end)
  else
    press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200) at(function() shot('p_screen') end)
  end
end) end
