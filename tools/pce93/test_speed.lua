-- Speed levels 0-3 from the password (US 1-1 codes, typed for real): hold Down 40 frames and print the player
-- sprite's Y every frame (the SAT entry that moves the most). Run: tools/pce93/run.sh test_speed.lua us, with SPEED set.
local codes={[0]={1,0,1,1,0,0,2,0},{1,0,1,1,0,1,3,0},{2,1,1,1,0,2,4,0},{2,1,1,1,0,3,5,0}}
local function ys() local t={} for n=0,63 do t[n]=emu.read(n*8,emu.memType.pceSpriteRam)|(emu.read(n*8+1,emu.memType.pceSpriteRam)<<8) end return t end
to_password() type_pw(codes[SPEED]) submit(22) wait(400) for i=1,6 do press({run=true}) wait(150) end wait(100)
local hist={}
at(function() emu.addEventCallback(function() if #hist<40 then hist[#hist+1]=ys() end end, emu.eventType.endFrame) end)
for i=1,40 do q[#q+1]={down=true} end
at(function() local best,bd=0,0 for k=0,63 do local d=hist[#hist][k]-hist[1][k] if d>bd and d<200 then best,bd=k,d end end
  local t={} for i=1,#hist do t[#t+1]=hist[i][best]-hist[1][best] end
  print(string.format('speed %d ($389A=%d): sprite %d Y offset per frame: %s', SPEED, r(0x389a), best, table.concat(t,' '))) end)
