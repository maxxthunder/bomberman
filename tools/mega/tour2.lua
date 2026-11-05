-- Everything but the areas (tour.lua): power-on and attract mode, title menu, Normal Game start, password screen
-- (typing, wrong code), game over and its continue screen, pause, and a Battle Game on each of the 10 stages
-- (4 combatants, single and tag, random input for P1, then the clock run down to force the time-up end).
-- USA addresses.
math.randomseed(SEED or 2)
local B={"Up","Down","Left","Right"}
local function rnd(n,pads)
  local d={}
  for f=1,n do
    local t={}
    for p=1,pads or 1 do
      if f%20==1 then d[p]=B[math.random(5)] end
      if d[p] then t["P"..p.." "..d[p]]=true end
      if math.random(30)==1 then t["P"..p.." "..({"A","B","C"})[math.random(3)]]=true end
    end
    joypad.set(t) emu.frameadvance()
  end
end
-- power-on: logos, title, attract demo (title times out after $4B0 frames, $1A690)
wait(1200) shot("boot") wait(1300) shot("attract1") wait(900) shot("attract2")
tap("Start") wait(400) tap("Start") wait(300) shot("title")
-- Normal Game from the title
tap("Start") wait(900) shot("normal1") tap("Start") wait(900) shot("normal2") tap("Start") wait(600) shot("normal3")
tap("A") wait(400) shot("normal_stage")
tap("Start") wait(60) shot("pause") tap("Start") wait(60)
rnd(600)
-- game over: lives 0, bombs at the feet until the continue screen shows the password ($AED6), then both choices
for k=1,3000 do w8(0x9543,0) if k%40<3 then joypad.set({["P1 A"]=true}) end emu.frameadvance()
  if k%30==0 and r8(0xAED6)+r8(0xAED7)+r8(0xAED8)+r8(0xAED9)>0 then break end end
wait(200) shot("gameover") tap("Down") wait(60) tap("Up") wait(60) tap("Start") wait(800) shot("continue")
-- password screen: type, move, wrong code, back out with B
savestate.load(STATES.."password_"..REG..".state") wait(60)
for _,b in ipairs({"Up","Up","Right","Down","Left","Left","Up"}) do tap(b) end
tap("Start") wait(120) shot("pw_wrong") tap("B") wait(300) shot("pw_back")
-- battle: each stage
local C=cov_off and COVER
for st=0,9 do
  if C and st>=2 then cov_off() end   -- menus and the time-up ending are covered by the first two
  savestate.load(STATES.."title_"..REG..".state") wait(30)
  tap("Down") tap("Start") wait(300)
  tap("Down") tap("Down") if st%2==1 then tap("Right") end tap("Start") wait(200)   -- 4 combatants, tag on odd stages
  if st==0 then tap("Down") tap("Up") tap("Up") end tap("Start") wait(200)          -- games
  for p=1,4 do tap(({"Right","Down","Left","Up"})[p]) tap("Start") wait(30) end wait(170) -- characters
  w8(0xAD3F,st) tap("Right") tap("Left") tap("Start") wait(200) shot("bstage"..st)
  tap("Start") wait(400) shot("battle"..st)
  if C then cov_on() end
  rnd((st<2 and 900) or BPLAY or 900,2)
  if st<2 or FULL then
    for k=1,5 do w8(0xA429,0) w8(0xA428,3) emu.frameadvance() end wait(1200) shot("timeup"..st)
    for k=1,6 do tap("Start") wait(200) end shot("after"..st)
    rnd(600,2)
  end
end
