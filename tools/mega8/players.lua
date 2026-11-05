-- Boot, start the battle, save a state, then drive each player 1-8 with its own pad and log who moved.
-- Player records: $1A4 + 42n (+$10 x, +$12 y in 1/3 pixels, 48 per cell; +$20 bombs, +$22 fire).
wait(120) tap("Start") wait(60)
savestate.save(STATES.."battle_"..MODE..".state") shot("battle")
local function pos(n) local b=0x1A4+42*n return r16(b+0x10)..","..r16(b+0x12) end
local function all() local t={} for n=0,7 do t[#t+1]=pos(n) end return table.concat(t," ") end
log("start "..all())
local moved=0
for p=1,8 do
  for _,d in ipairs({"Right","Left","Down","Up"}) do
    savestate.load(STATES.."battle_"..MODE..".state")
    local before=all() PFX="P"..p.." " press({[d]=true},24) PFX=nil
    local after=all()
    if after~=before then
      local who={} for n=0,7 do if pos(n)~=before:match(("%S+ "):rep(n).."(%S+)") then who[#who+1]=n+1 end end
      log("P"..p.." "..d.." moves player "..table.concat(who,"+")) moved=moved+1 shot("p"..p) break
    end
  end
end
log("pads that moved someone: "..moved)
-- bombs: every player presses A at once
savestate.load(STATES.."battle_"..MODE..".state")
local t={} for p=1,8 do t["P"..p.." A"]=true end joypad.set(t) wait(2) wait(20) shot("bombs") wait(150) shot("boom")
for n=0,7 do log("player "..(n+1).." handler "..string.format("%X",memory.read_u32_be(0x1A4+42*n+8,DOMAIN))) end
