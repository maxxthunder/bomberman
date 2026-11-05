-- 4-player SGB multitap battle: run with tools/emu/sgb_dump.py tools/gb2 <us|jp> tools/gb2/multitap.lua <out>.
-- With 4 players answered the title adds BATTLE (4th line). PLAYER page: each pad joins with Up/Down ($00:3063,
-- one bit per pad in $C1AA-$C1AD); with all four joined Start skips the COMPUTER page -> MODE (TIME / BATTLE count)
-- -> STAGE -> play. Pads are read 4 per frame by $00:086A into $FFA0/$FFA2/$FFA4/$FFA6 (held) and +1 (new).
function pad(n,b,f) at(function() SGBPAD[n]=b end) wait(f or 8) at(function() SGBPAD[n]=nil end) wait(12) end
for k=1,4 do wait(100) press({start=true},8) end wait(150)
for k=1,3 do press({down=true},8) wait(20) end
press({a=true},8) wait(120)
pad(2,{up=true}) pad(3,{up=true}) pad(4,{up=true}) wait(30) at(function() shot('j1') end)
for k=1,(NST or 3) do press({start=true},8) wait(60) at(function() shot('k'..k) end) end
local dirs={'up','down','left','right'}
math.randomseed(5)
for k=1,(NIT or 600) do
  local bs={} for n=1,4 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end bs[n]=b end
  at(function() for n=2,4 do SGBPAD[n]=bs[n] end end) hold(bs[1],6)
  if k%(SHOT or 50)==0 then at(function() shot('p'..k) end) end
end
at(function() cdl_dump('cov_mt') end)
