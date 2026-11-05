-- Cheat check (Mesen pceRaw). Set TEST ('inv','room','snd','lives','none'), V ('us'/'jp') and INV (the two invincibility codes) first; run with tools/pce90/run.sh.
-- verify Mesen pceRaw cheats. TEST = inv | room | snd | lives | none; INV = the two ROM cheat codes for the version
local function add(c) local ok,e=pcall(emu.addCheat,emu.cheatType.pceRaw,c) print('cheat',c,ok,e) end
math.randomseed(11)
local dirs={'up','down','left','right'}
local function bot() local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.i=true end return b end
local deaths, last = 0, 0
local over = false
emu.addEventCallback(function() local d=emu.read(0x43A,W)&7 if d~=0 and last==0 then deaths=deaths+1 end last=d
  if emu.read(0x146A,W)==1 then over=true end end, emu.eventType.endFrame)
if TEST=='inv' then for _,c in ipairs(INV) do add(c) end end
if TEST=='room' then add('00200B:80') add('00200C:0B') end
if TEST=='snd' then add('1F1451:FF') end
if TEST=='lives' then add('1F0438:02') end
if TEST=='room' then
  local hit=0 emu.addMemoryCallback(function() hit=hit+1 end, emu.callbackType.exec, 0xA063, 0xA063, emu.cpuType.pce, emu.memType.pceMemory)
  wait(600) press({run=true}) for k=1,12 do wait(200) press({run=true}) end wait(300) S('room_'..V) at(function() print('room entered (exec $01:A063)', hit>0) end)
elseif TEST=='snd' then
  to_password() type_pw('MUVWLNPC') wait(300) S('snd_'..V) at(function() print('sound test number $3440', emu.read(0x1440,W)) end)
else
  to_password() type_pw('MUVWLNPC') wait(700)
  for k=1,(FR or 6000)//6 do local b=bot() for j=1,6 do q[#q+1]=b end end
  S(TEST..'_'..V) at(function() print(TEST, 'deaths', deaths, 'game over', over, 'lives', emu.read(0x438,W)) end)
end
