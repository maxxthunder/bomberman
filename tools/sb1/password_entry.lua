-- Password screen: start digits, Up/Down wrap, which buttons move the cursor, Start submits, state after reopening.
local function dig(tag) at(function() print(tag, emu.read(0x1030,W),emu.read(0x1031,W),emu.read(0x1032,W),emu.read(0x1033,W), 'cursor', emu.read(0x1020,W)) end) end
function typepw(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for k=1,d do press({up=true},2) end press({a=true},2) end end
to_password() dig('poweron')
press({down=true},2) dig('down from 0')
press({up=true},2) dig('up back')
for i=1,7 do press({up=true},2) end dig('up x7')
press({up=true},2) dig('up from 7')
press({b=true},2) press({left=true},2) press({y=true},2) dig('B/left/Y')
press({right=true},2) dig('right')
press({a=true},2) dig('A')
-- invalid code 0000-ish: start now
press({start=true},2) wait(200) at(function() print('A4', string.format('%02x',emu.read(0xA4,W))) end)
wait(200) press({down=true},4) wait(30) press({down=true},4) wait(30) press({start=true},4) wait(120) dig('reopened after invalid')
S('reopen')
