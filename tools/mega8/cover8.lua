-- Routine coverage of the demo (prepend tools/mega/cover.lua; see docs/mega8.md, Dead code):
-- power-on and splash, Start, then all 8 pads on random input until everyone is dead or FRAMES run out.
cov_load(STATES.."cand.txt", STATES.."cov_hits_"..MODE..".txt") cov_on()
math.randomseed(SEED or 3)
wait(200) tap("Start") wait(60)
local B={"Up","Down","Left","Right"} local d={}
for f=1,FRAMES or 6000 do
  local t={}
  for p=1,8 do
    if f%24==p then d[p]=B[math.random(5)] end
    if d[p] then t["P"..p.." "..d[p]]=true end
    if math.random(20)==1 then t["P"..p.." "..({"A","B","C"})[math.random(3)]]=true end
  end
  joypad.set(t) emu.frameadvance()
  if f%1500==0 then shot("f"..f) end
end
cov_off() log("cov done")
