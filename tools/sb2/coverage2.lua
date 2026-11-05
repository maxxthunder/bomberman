-- Second code/data-log coverage run for the dead-code sweep (tools/sb1/sweep.py dead), unpatched ROM, multitap in
-- port 2: put e.g. "ROUTE=2 FR2=40000" as the first line of a copy, then MESEN_ARGS=--snes.port2.type=Multitap
-- python tools/sb2/run.py copy.lua rom.sfc > log  (run.py NAME=value would also rewrite the "ROUTE=ROUTE or 1" line)
-- Random presses on all five pads (emu.setInput(input, 0, port, subport)).
-- IDLE=n: power on, leave the attract mode running n frames, dump the log (no menus).
-- ROUTE=1: Normal Game from 4361; every stage $10-$57 and the ending ($60)
--   by the stage-clear path the debug menu uses ($1A = target-1, $7E:8002 |= $4000), FR frames each, hearts kept at
--   $90 (NO DEATH), the kit ($7E:80E0-$80FF) and bomb type randomised every 40 frames.
-- ROUTE=2: random presses on every pad from the title for FR2 frames (menus, battle setup, battles, password).
-- ROUTE=3: Normal Game, no invincibility, random presses: deaths, game over, continue.
ROUTE=ROUTE or 1 IDLE=IDLE or 0 FR=FR or 1400 FR2=FR2 or 60000
local keys={'up','down','left','right','a','b','y','x','l','r','select','start'}
local seed=4321
local function rnd(n) seed=(seed*1103515245+12345)%2147483648 return seed%n end
local function rpad() local t={} for k=1,3 do local b=keys[rnd(#keys)+1] if (b~='start' and b~='select') or rnd(30)==0 then t[b]=true end end return t end
local M=emu.memType.snesMemory
local on=false local inv=false local f=0 local cur={} local last=-1
emu.addEventCallback(function()  -- inputPolled fires on every multitap read: set the pads once per frame
  if not on or f==last then return end
  last=f
  emu.setInput(rpad(),0,0,0) for s=0,3 do emu.setInput(rpad(),0,1,s) end
end, emu.eventType.inputPolled)
emu.addEventCallback(function() if on then f=f+1 end end, emu.eventType.endFrame)
emu.addEventCallback(function()
  if not on then return end
  if inv then emu.write(0x7E80EF,0x90,M) end
  if inv and f%40==0 then
    emu.write(0x7E80E0,1+rnd(3),M) emu.write(0x7E80E1,1+rnd(9),M) emu.write(0x7E80E2,rnd(10),M)
    emu.write(0x7E80F3,({0,1,2,4,8})[rnd(5)+1],M)
    for _,a in ipairs({0x7E80FA,0x7E80FB,0x7E80FE,0x7E80FF}) do emu.write(a,rnd(2),M) end
  end
end, emu.eventType.startFrame)
local function cdl() local c=emu.getCdlData(emu.memType.snesPrgRom) local t={} for i=0,#c do t[#t+1]=string.format('%02x',c[i]) end print('CDLHEX cov '..table.concat(t)) end
local function go()
  title(function()
    if ROUTE==2 then
      at(function() on=true end) wait(FR2)
    else
      wait(60) press({down=true},6) wait(20) press({down=true},6) wait(20) press({a=true},6) wait(200)
      pw('4361') wait(5) press({start=true},6) wait(600)
      if ROUTE==1 then
        local st={} for w=1,5 do for a=0,7 do st[#st+1]=w*16+a end end st[#st+1]=0x60
        for _,v in ipairs(st) do
          at(function() on=false inv=true emu.write16(0x1A,v-1,M) emu.write16(0x7E8002,emu.read16(0x7E8002,M)|0x4000,M) end)
          wait(400)
          at(function() on=true f=0 print(string.format('stage %02x now %02x', v, emu.read(0x1A,M))) end)
          wait(FR)
        end
        at(function() on=false end) wait(9000)
      else
        at(function() on=true end) wait(FR2)
      end
    end
    if watch_report then at(watch_report) end at(cdl) at(stop)
  end)
end
if IDLE>0 then wait(IDLE) at(cdl) at(stop) else go() end  -- IDLE=n: only the attract mode, no presses
