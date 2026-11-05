-- game over -> continue screen -> SAVE, then game over -> CONTINUE, then END, then LOAD from the title
math.randomseed(7)
local dirs={'up','down','left','right'}
local function bot() local b={} b[dirs[math.random(4)]]=true if math.random(4)==1 then b.i=true end return b end
local function gameover()
  local t=0
  local function f() t=t+1 if emu.read(0x146A,W)==1 or t>12000 then return {} end table.insert(q,1,f) local b=bot() return b end
  q[#q+1]=f
end
at(function() print('lives',emu.read(0x438,W)) end)
to_password() type_pw('MUVWLNPC') wait(700)
gameover() wait(200) S('go1') at(function() print('go', emu.read(0x146A,W), emu.read(0x1469,W)) end)
press({down=true}) press({down=true}) S('go1_save') press({run=true}) wait(200) S('save1') press({run=true}) wait(200) S('save2') press({i=true}) wait(200) S('save3')
press({run=true}) wait(200) S('save4') press({i=true}) wait(300) S('save5')
for k=1,4 do press({run=true}) wait(150) S('after'..k) end
at(function() emu.write(0x146A,0,W) print('state', emu.read(0x84A,W), emu.read(0x84B,W), emu.read(0x1469,W)) end)
gameover() wait(200) S('go2') press({run=true}) wait(400) S('cont')
at(function() emu.write(0x146A,0,W) end)
gameover() wait(200) S('go3') press({down=true}) press({run=true}) wait(600) S('end_title')
wait(300) press({up=true}) wait(30) S('title_load') press({run=true}) wait(300) S('load1') press({run=true}) wait(300) S('load2') press({i=true}) wait(300) S('load3')
maps_dump() cdl_dump('cdl')
