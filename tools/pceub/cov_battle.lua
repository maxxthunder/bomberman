-- Users Battle coverage on the TurboTap copy: UB (1/2), NP players, random play on all five pads
math.randomseed(SEED or 5)
local dirs={'up','down','left','right'}
local rnd=false local f=0 local tap=nil
emu.addEventCallback(function() f=f+1
  if rnd then for p=0,4 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.i=true end emu.setInput(b,0,0,p) end end
  if tap and f>=tap and f<tap+5 then emu.setInput({run=true},0,0,1) end end, emu.eventType.inputPolled)
wait(300) at(function() tap=f+1 end) press({run=true}) wait(120) S('u1')
for k=2,(UB or 1) do press({down=true}) end press({run=true}) wait(150) S('u2')
for k=1,(NP or 2)-2 do press({down=true}) end press({run=true}) wait(120) S('u3')
press({run=true}) wait(120) S('u4')
press({run=true}) wait(120) S('u5')
press({run=true}) wait(200) S('u6')
at(function() rnd=true end)
for k=1,(NSHOT or 14) do wait(600) S('p'..k) end
at(function() rnd=false end) wait(300) S('pend')
for k=1,4 do press({run=true}) wait(200) S('q'..k) end
maps_dump()
