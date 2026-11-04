-- needs a Mesen copy with Port 2 = SNES controller (MESEN=... portable dir with its own settings.json)
-- start a Normal Game from controller 2
wait(700)
for i=1,4 do q[#q+1]=function() emu.setInput({start=true},0,1) end end wait(80)
for i=1,4 do q[#q+1]=function() emu.setInput({start=true},0,1) end end wait(900)
S('p2') at(function() print('A4',emu.read(0xA4,W),'D44',emu.read(0xD44,W),'D84',emu.read(0xD84,W),'D7D',emu.read(0xD7D,W),'DBD',emu.read(0xDBD,W)) end)
