-- Coverage segments for the dead-code sweep (cov.py writes VER, OFF (RAM shift: 0, Special Version -9) and the
-- segment calls after this file). Each run ends with cdl_dump('cov'), the Mesen code/data log.
local keep=false
emu.addEventCallback(function() if keep and FRAME%30==0 then wr(0x389F+OFF,5) end end, emu.eventType.endFrame)
local function keeplives(on) at(function() keep=on end) end
function softreset() press({select=true,run=true},6) wait(400) end
local function pwscreen() if VER=='sp' then sp_password() else to_password() end end
-- In a stage Select+Run only pauses, so a run does not reset between segments: start() types a password and
-- starts it; warp(w,s) writes world, stage and the cleared planets before w, drops a bomb to lose a life, and the
-- death path (planet map, Run) starts w-s. $2301/$2305/$2C9B are 1 while paused (RAM diff); unpause() presses Run then.
local function unpause() at(function() if VER~='sp' and (r(0x2301)==1 or r(0x2305)==1 or r(0x2C9B)==1) then
  for j=1,10 do table.insert(q,1,j<=4 and {run=true} or {}) end end end) end
function start(idx) pwscreen() type_pw(idx) submit(VER=='us' and 22 or 28) wait(400)
  keeplives(true) press({run=true}) wait(200) press({run=true}) wait(300) unpause() end
function warp(w,st,n,seed) at(function() wr(0x3895+OFF,w-1) wr(0x3896+OFF,st-1) wr(0x38AF+OFF,w==7 and 63 or (1<<(w-1))-1) end)
  press({i=true}) wait(420) press({run=true}) wait(200) press({run=true}) wait(300) unpause() unpause()
  at(function() print(string.format('warp %d-%d: world %d stage %d state %d',w,st,r(0x3895+OFF)+1,r(0x3896+OFF)+1,r(0x38A1+OFF))) end)
  S(string.format('w%d_%d',w,st)) mash(n,seed) end
-- lives 0, then random play into the continue / game-over screens, which get random input too
function gameover(seed) at(function() keep=false wr(0x389F+OFF,0) end) mash(3000,seed)
  for i=1,10 do press({run=true}) wait(100) end mashr(1500,seed+1) end
-- the ending: password for 7-8, then the stage state is replaced by "stage cleared" with stage 8, which runs the
-- boss-clear path into the ending (02:84B6). Then hold I and press Run (the CONFIGRATION code), soft reset, new game.
local armed=false
on_exec(0x83BF,2,function() if armed and r(0x38A1+OFF)==2 then wr(0x38A1+OFF,4) wr(0x3896+OFF,7) armed=false print('forced clear at',FRAME) end end)
-- ENDCHK = logical address of the ending's one-time I+Run test (US 08:8C7D, JP 08:8C85): it runs once, after
-- about 1000 frames of waits on the end screen, and reads I held ($32 bit 0) and Run newly pressed ($37 bit 3).
function ending(idx)
  if ENDCHK then on_exec(ENDCHK,8,function() print(string.format('end check at %d: $32=%02x $37=%02x',FRAME,r(0x2032),r(0x2037))) end) end
  pwscreen() type_pw(idx) at(function() armed=true end) submit(VER=='us' and 22 or 28) wait(1500)
  S('end_pic') press({run=true}) for k=1,8 do wait(1000) S('end'..k) end
  for j=1,1500 do q[#q+1]= j%2==0 and {i=true,run=true} or {i=true} end
  at(function() print('$3FFB =',r(0x3FFB)) end) S('end_ir') softreset()
  press({run=true}) wait(400) press({run=true}) for i=1,20 do wait(100) if i%3==0 then press({run=true}) end end S('after_reset')
  mash(3000,77) end
-- random input that also presses Run now and then (menus need it; in a match it pauses / unpauses)
function mashr(n,seed) math.randomseed(seed) local k={'up','down','left','right','i','ii','i','run'} for f=1,n,8 do local b={} b[k[math.random(#k)]]=true for j=1,8 do q[#q+1]=b end end end
-- battle game: title item 2, then random input through setup, stage select and matches
function battle(n,seed) wait(400) press({run=true}) wait(400) press({down=true}) wait(20) press({run=true}) wait(300)
  for i=1,6 do press({run=true}) wait(150) press({i=true}) wait(150) end mashr(n,seed) softreset() end
function attract(n) wait(n) press({run=true}) wait(600) softreset() end
-- RAM bytes ever written with a value other than 0 (for the unset-flag search): wn_dump() prints them as a bitmap
local WN={} emu.addMemoryCallback(function(a,v) if v~=0 then WN[a]=true end end, emu.callbackType.write, 0x2000, 0x3FFF)
function wn_dump() at(function() local t={} for a=0x2000,0x3FFF do t[#t+1]=WN[a] and '1' or '0' end print('WNZ '..table.concat(t)) end) end
-- maps.py: when the stage loader (02:8066) reads a stage record ($D1, Special Version $D8) not seen yet in this run,
-- dump work RAM (the cell grid at $2FD7) and VRAM / palette / SAT 240 frames later, as s<record>.*
local MS={}
on_exec(0x8066,2,function() local id=r(VER=='sp' and 0x20D8 or 0x20D1) if MS[id] then return end MS[id]=true
  print('STAGE record',id,'world',r(0x3895+OFF),'stage',r(0x3896+OFF)) after(240,function() dump('s'..id) vdump('s'..id) end) end)
-- battle runs: each time the stage loader starts (02:8010) in the Battle Game (world 8), the battle stage ($3896)
-- is set to the next one, so successive matches cycle through all of them
local bcount=0
on_exec(0x8010,2,function() if r(0x3895+OFF)==8 then wr(0x3896+OFF,bcount%9) print('battle stage forced',bcount%9) bcount=bcount+1 end end)
