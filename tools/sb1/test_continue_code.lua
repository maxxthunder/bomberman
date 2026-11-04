-- set PW and N first. Types PW, zeroes lives, bombs yourself until GAME OVER, reads the CONTINUE code at $0C7F-$0C82
function typepw(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for k=1,d do press({up=true},2) end press({a=true},2) end end
to_password() typepw(PW)
wait(400) at(function() print('lives',emu.read(0xD7D,W),'d17',string.format('%02x',emu.read(0xD17,W))) emu.write(0xD7D,0,W) end)
for i=1,N do press({b=true},4) press({y=true},4) press({a=true},4) wait(250) end
S('g1') wait(300) S('g2') wait(300) S('g3')
at(function() print('d17',string.format('%02x',emu.read(0xD17,W)),'pw',emu.read(0xC7F,W),emu.read(0xC80,W),emu.read(0xC81,W),emu.read(0xC82,W),'a4',string.format('%02x',emu.read(0xA4,W))) end)
