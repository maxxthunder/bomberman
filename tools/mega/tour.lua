-- Play every area from its stage-1 password: each stage gets PLAY frames of random input, then is finished with the
-- game's own clear entry ($C4FC, via an idle task, see skipthrough.lua); the boss gets PLAY frames, then the hub's
-- area-complete sequence ($18DDC). Lives are kept at 5. With COVER set, routine coverage runs (cover.lua).
-- USA addresses. AREAS = list of area indexes (1-6) to play.
local CODES={"2200","4501","4502","6803","8114","0515"}
PLAY=PLAY or 600
math.randomseed(SEED or 1)
local function task(i) return memory.read_u32_be(0x62E+4*i,"M68K BUS") & 0xFFFF end
local function st(t) log(string.format("%-12s 953A=%d 953B=%d 953C=%d 953D=%02X lives=%d t2=%X tC=%X",t,r8(0x953A),r8(0x953B),r8(0x953C),r8(0x953D),r8(0x9543),memory.read_u32_be(task(2)+4,DOMAIN),memory.read_u32_be(task(0xC)+4,DOMAIN))) end
local B={"Up","Down","Left","Right"}
function rnd(n)
  local d=B[math.random(4)]
  for f=1,n do
    if f%20==0 then d=B[math.random(5)] end
    local t={} if d then t["P1 "..d]=true end
    if math.random(30)==1 then t["P1 "..({"A","B","C"})[math.random(3)]]=true end
    joypad.set(t) w8(0x9543,5) emu.frameadvance()
  end
end
local function idle()  -- a task to run $C4FC in: the idle one ($75A6), else the last live task from 4 up (an enemy or
  -- prop; $C4FC only uses its own task's +$16 and then sets its routine through $53E, like the exit object does)
  for i=3,0x1F do if memory.read_u32_be(task(i)+4,DOMAIN)==0x75A6 then return i end end
  if memory.read_u32_be(task(2)+4,DOMAIN)~=0x1C96 then return end
  for i=0x1F,4,-1 do if memory.read_u32_be(task(i)+4,DOMAIN)~=0 then return i end end
end
function until_(f,n) for k=1,n do if f() then return true end emu.frameadvance() end log("timeout") end
function hub() return memory.read_u32_be(task(2)+4,DOMAIN)==0x18A30 end
for _,ar in ipairs(AREAS or {1,2,3,4,5,6}) do
  if COVER and ar>(COVER_FULL or 1) then cov_off() end
  enter(CODES[ar]) wait(700) shot(ar.."_planet") tap("Start") wait(600) st("hub") shot(ar.."_hub")
  if COVER and ar<=(COVER_FULL or 1) then cov_on() end
  if ar==6 then if COVER then cov_on() end   -- the final area is one big stage; after playing it, start the ending ($15C52, called by $1830C)
    rnd(PLAY*2) shot("6_play") memory.write_u32_be(task(2)+4,0x15C52,DOMAIN)
    for k=1,ENDING or 12 do wait(600) shot("ending"..k) end
    break
  end
  for s=1,5 do
    if r8(0x953D)&0x0F==((ar==1) and 7 or 15) or (ar==6 and s>1) then break end
    tap("A") until_(function() return idle() end,1500) wait(30) st("stage"..s) shot(ar.."_s"..s)
    if COVER then cov_on() end
    rnd(PLAY) shot(ar.."_s"..s.."_play")
    if COVER and ar>(COVER_FULL or 1) then cov_off() end
    local i=idle() if not i then log("no idle task") break end
    memory.write_u32_be(task(i)+4,0xC4FC,DOMAIN) wait(300) until_(function() return hub() or r8(0x953D)&0x0F==((ar==1) and 7 or 15) end,2000) wait(200) st("cleared"..s) shot(ar.."_c"..s)
  end
  wait(400) if COVER then cov_on() end rnd(PLAY) st("boss") shot(ar.."_boss")
  local b=2 if memory.read_u32_be(task(2)+4,DOMAIN)==0 then for k=0x1F,4,-1 do if memory.read_u32_be(task(k)+4,DOMAIN)~=0 then b=k break end end end
  memory.write_u32_be(task(b)+4,0x18DDC,DOMAIN) wait(1400) st("after") shot(ar.."_after")
  tap("Start") wait(800) shot(ar.."_next") st("next")
end
