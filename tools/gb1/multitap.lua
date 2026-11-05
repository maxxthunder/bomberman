-- 4-player SGB multitap battle (title START -> NORMAL/BATTLE, only offered when the SGB answers MLT_REQ). Run with
-- tools/emu/sgb_dump.py tools/gb1 <jp|wario> tools/gb1/multitap.lua <out>: sgb.lua answers MLT_REQ 4 and feeds
-- SGBPAD[2..4] as pads 2-4. Join screen: each pad's A turns its player ON; Start -> TECHNIQUE / ROUND SELECT; Start
-- plays. Then NIT x 6 frames of random input on all four pads (bank 9 code, arena C3F0 = $20 + C3EF).
function pad(n,b,f) at(function() SGBPAD[n]=b end) wait(f or 4) at(function() SGBPAD[n]=nil end) wait(8) end
wait(900) press({start=true}) wait(60) press({down=true}) press({start=true}) wait(120)
press({a=true}) pad(2,{a=true}) pad(3,{a=true}) pad(4,{a=true}) wait(30) press({start=true}) wait(60)
press({a=true}) press({down=true}) at(function() shot('r0') end) press({right=true}) at(function() shot('r1') end)
press({start=true}) wait(30) at(function() shot('s0') end)
-- all four pads random
local dirs={'up','down','left','right'}
math.randomseed(7)
for k=1,(NIT or 400) do
  local bs={} for n=1,4 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end bs[n]=b end
  at(function() for n=2,4 do SGBPAD[n]=bs[n] end end) hold(bs[1],6)
  if k%(SHOT or 25)==0 then at(function() shot('p'..k) print('F',FRAME,'C3F0',rd(0xC3F0),'alive',rd(0xC000),rd(0xC100),rd(0xC200),rd(0xC300)) end) end
end
at(function() cdl_dump('cov_mt') end)
