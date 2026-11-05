-- Check the Game Genie codes through BizHawk's own cheat system (client.addcheat decodes them): each test runs
-- once without and once with the code and logs what changed. Codes per region (Europe's code above $7C4A is 6 bytes
-- lower, so two of them differ).
local G = (REG=="eu") and {timer="HC0A-AYZT", area="HCXT-DJV0"} or {timer="HC0A-AYZ0", area="HCXT-DJV6"}
G.lives="HA3A-AYWC" G.inv="AJ2A-AAB2"
local function stage()   -- area 1 stage 1, in play
  enter("2200") wait(700) tap("Start") wait(600) tap("A") wait(500)
end
local function bombs(n)  -- drop bombs at the feet (A, B, C in turn, as gameover.lua does) for n frames; count lives lost
  local lost,l=0,r8(0x9543)
  for k=1,n do
    local t={} if k%40<3 then t["P1 "..({"A","B","C"})[(k//40)%3+1]]=true end
    joypad.set(t) emu.frameadvance()
    local v=r8(0x9543) if v<l then lost=lost+(l-v) end l=v
  end
  return lost
end
for _,on in ipairs({false,true}) do
  local tag=on and "with" or "without"
  -- lives: stand on own bombs until the game would be over
  stage() if on then client.addcheat(G.lives) end
  local l0=r8(0x9543) local lost=bombs(2400) log(string.format("lives %s %s: start %d, end %d, lost %d, 953C %d",G.lives,tag,l0,r8(0x9543),lost,r8(0x9543)))
  shot("lives_"..tag) if on then client.removecheat(G.lives) end
  -- invincibility: same, count deaths through the player's hit timer and lives
  stage() if on then client.addcheat(G.inv) end
  l0=r8(0x9543) lost=bombs(1200) log(string.format("invincible %s %s: lives %d -> %d (lost %d)",G.inv,tag,l0,r8(0x9543),lost))
  shot("inv_"..tag) if on then client.removecheat(G.inv) end
  -- timer: 600 frames in a stage
  stage() if on then client.addcheat(G.timer) end
  local t0=string.format("%d:%02d",r8(0xA429),r8(0xA428)) wait(600)
  log(string.format("timer %s %s: %s -> %d:%02d",G.timer,tag,t0,r8(0xA429),r8(0xA428))) shot("timer_"..tag)
  if on then client.removecheat(G.timer) end
  -- area select (area 3): Normal Game from the title
  savestate.load(STATES.."title_"..REG..".state") if on then client.addcheat(G.area) end
  wait(30) tap("Start") wait(900) shot("area_"..tag) log(string.format("area %s %s: 953A=%d 953B=%d",G.area,tag,r8(0x953A),r8(0x953B)))
  tap("Start") wait(900) tap("Start") wait(600) shot("area_hub_"..tag) log(string.format("  hub: 953A=%d 953F=%X",r8(0x953A),r8(0x953F)))
  if on then client.removecheat(G.area) end
end
