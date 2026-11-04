-- Coverage run for the unused-graphics sweep: play one stage with a random bot, then dump the CDL.
-- job.sh <dir> "PW='7352'" "$(cat cover.lua)"   normal game from a password (FRAMES of play)
-- job.sh <dir> "BST=3" "$(cat cover.lua)"       battle stage BST (0-based, $7F202B written at stage select)
-- job.sh <dir> "PW='1009' END=1 FRAMES=20000" ... no bot (ending); DEMO=1: leave the title alone (attract mode)
FRAMES = FRAMES or 2500
math.randomseed(SEED or 1)
local dirs = {{up=true},{down=true},{left=true},{right=true}}
local function bot(n) for i=1,n//12 do local d=dirs[math.random(4)] for k=1,10 do q[#q+1]=d end
  if math.random(3)==1 then q[#q+1]={b=true} q[#q+1]={} else q[#q+1]={} q[#q+1]={a=(math.random(4)==1)} end end end
if DEMO then wait(FRAMES)
elseif END then to_pw() typepw(PW) press({start=true}) wait(FRAMES)
elseif BST then to_stage() at(function() emu.write(0x7F202B, BST, emu.memType.snesMemory) end) press({start=true}) wait(400) at(function() shot("in") end) bot(FRAMES)
else to_pw() typepw(PW) press({start=true}) wait(400) press({start=true}) wait(200) at(function() shot("in") end) bot(FRAMES) end
at(function() shot('end') end)
cdl_dump()
wait(60)
