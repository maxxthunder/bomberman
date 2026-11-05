-- battle coverage on the TurboTap copy: MODE (0 normal / 1 skull), NP players (2-5), random play on all pads
math.randomseed(SEED or 3)
local dirs={'up','down','left','right'}
local rnd=false
local f=0
emu.addEventCallback(function() f=f+1 if rnd then for p=0,4 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.i=true end emu.setInput(b,0,0,p) end end end, emu.eventType.inputPolled)
-- the tap check compares the five ports on the frame a battle mode is chosen: press Run on pad 2 too
emu.addEventCallback(function() if TAPRUN and f>=TAPRUN and f<TAPRUN+5 then emu.setInput({run=true},0,0,1) end end, emu.eventType.inputPolled)
wait(600) press({down=true}) at(function() TAPRUN=f+1 end) press({run=true}) wait(120) S('b1')
for k=1,(MODE or 0) do press({down=true}) end press({run=true}) wait(120) S('b2')
for k=1,(NP or 2)-2 do press({down=true}) end press({run=true}) wait(120) S('b3')
press({run=true}) wait(120) S('b4')
press({run=true}) wait(120) S('b5')
press({run=true}) wait(200) S('b6')
at(function() rnd=true end)
for k=1,(NSHOT or 12) do wait(600) S('p'..k) end
at(function() rnd=false end) wait(300) S('pend')
for k=1,4 do press({run=true}) wait(200) S('q'..k) end
maps_dump()
