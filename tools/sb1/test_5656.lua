-- types 5656 for real, then starts a Normal Game
function typepw(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for k=1,d do press({up=true},2) end press({a=true},2) end end
to_password() typepw('5656') wait(10) S('p') at(function() print('A4',emu.read(0xA4,W),'C90',emu.read(0xC90,W)) end)
wait(400) S('t') press({start=true},4) wait(60) press({start=true},4) wait(900) S('g1') wait(300) S('g2')
at(function() print('A4',emu.read(0xA4,W),'C90',emu.read(0xC90,W),'lives',emu.read(0xD7D,W),'stage',string.format('%02x',emu.read(0xD17,W))) end)
