-- Code/data-log coverage run for the dead-code sweep (tools/sb1/sweep.py dead). Needs a multitap in port 2
-- (MESEN_ARGS=--snes.port2.type=Multitap tools/sb1/run.sh tools/sb1/coverage.lua us). Dumps the log with cdl_dump.
-- IDLE=n: power on and leave the attract mode running n frames first.
-- FROM..TO: scenes written to $00A4, FR frames each, random presses on all five pads. In each scene player 1 and 2
-- keep the invincibility timer (+$36), get random power-ups (+$30-$39) and have an item put under them every
-- 40 frames (items 1-24 in turn, map cell $0916+cell = item|$0200), so the pickup handlers run. At frame CLR the
-- enemy count is zeroed and player 1 put on the exit (stage clear); with DIE=1 the invincibility stops at DIEF
-- and lives go to 1 (game over, continue screen).
IDLE=IDLE or 0 FROM=FROM or 0 TO=TO or 0x4D FR=FR or 1500 CLR=CLR or 1100 DIE=DIE or 0 DIEF=DIEF or 700
local keys={'up','down','left','right','a','b','y','x','l','r','select','start'}
local seed=12345
local function rnd(n) seed=(seed*1103515245+12345)%2147483648 return seed%n end
local f=0 local scene=-1 local item=1 local inv=true
local function pad(i)
  local t={} for k=1,3 do local b=keys[rnd(#keys)+1] if b~='start' or rnd(40)==0 then t[b]=true end end return t end
emu.addEventCallback(function()
  if scene<0 then return end
  f=f+1
  emu.setInput(pad(1),0,0,0) for s=0,3 do emu.setInput(pad(s+2),0,1,s) end
end, emu.eventType.inputPolled)
emu.addEventCallback(function()
  if scene<0 then return end
  for _,P in ipairs({0x0D40,0x0D80}) do
    if inv then emu.write16(P+0x36,0x0160,W) end
    if f%40==0 then
      emu.write(P+0x30,1+rnd(9),W) emu.write(P+0x31,rnd(9),W) emu.write(P+0x32,rnd(5),W)
      emu.write(P+0x39,(emu.read(P+0x39,W)&0x9C)|rnd(4)|(rnd(4)<<5),W) emu.write(P+0x33,rnd(2),W)
      local x,y=emu.read16(P+0x11,W),emu.read16(P+0x14,W)
      local c=(y//16)*64+(x//16)*2
      if c>0 and c<0x340 and P==0x0D40 then emu.write16(0x0916+c,item|0x0200,W) item=item%24+1 end
    end
  end
  if f==CLR then emu.write(0x0D25,0,W)
    local ex=nil for c=0,0x33E,2 do if emu.read(0x0916+c,W)&0x1F==0x10 then ex=c end end
    if ex then emu.write16(0x0D51,((ex%64)//2)*16+8,W) emu.write16(0x0D54,(ex//64)*16+8,W) end end
  if DIE==1 and f==DIEF then inv=false emu.write(0x0D7D,1,W) end
end, emu.eventType.startFrame)
wait(IDLE)
wait(900)
for v=FROM,TO do
  at(function() scene=v f=0 inv=true emu.write(0x0314,emu.read(0x0314,W)&0xBF,W) emu.write(0xA4,v,W) end)  -- unpause first
  wait(FR)
  at(function() print('scene',v,'now',string.format('%02x',emu.read(0xD10,W))) end)
end
if watch_report then at(watch_report) end
cdl_dump('cov')
