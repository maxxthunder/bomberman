-- Password screen after a game over: types PW, loses N lives, says NO on CONTINUE, reopens the password screen (does it hold the last code?).
PW='6052' N=5
local function dig(tag) at(function() print(tag, emu.read(0x1030,W),emu.read(0x1031,W),emu.read(0x1032,W),emu.read(0x1033,W), 'C7F', emu.read(0xC7F,W),emu.read(0xC80,W),emu.read(0xC81,W),emu.read(0xC82,W), 'A4', string.format('%02x',emu.read(0xA4,W))) end) end
function typepw(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for k=1,d do press({up=true},2) end press({a=true},2) end end
to_password() typepw(PW)
wait(400) at(function() emu.write(0xD7D,0,W) end)
for i=1,N do press({b=true},4) press({y=true},4) press({a=true},4) wait(250) end
wait(600) dig('continue screen') S('cont')
press({right=true},4) wait(20) press({start=true},4) wait(400) dig('after NO') S('afterno')
for k=1,6 do wait(150) S('t'..k) end press({down=true},4) wait(30) press({down=true},4) wait(30) press({start=true},4) wait(120) dig('password screen') S('pw')
