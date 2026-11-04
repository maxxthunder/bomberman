-- Prepend after cdl.lua. Logs each graphics stream the game opens ($C0:2595, source in dp $06-$08), each palette request
-- ($C0:1B38: set $0D78, id Y+1) once, as 'S bbaaaa' / 'P set.id'. Map S sources to assets with tools/sb3/assets.py list.
LOG={}
function L(k) if not LOG[k] then LOG[k]=1 print(k) end end
emu.addMemoryCallback(function() L(string.format('S %02x%02x%02x', r8(8), r8(7), r8(6))) end, emu.callbackType.exec, 0xC02595, 0xC02595)
emu.addMemoryCallback(function() local s=emu.getState() L(string.format('P %d.%02d', r8(0x0D78), (s['cpu.y']&0xFF)+1)) end, emu.callbackType.exec, 0xC01B38, 0xC01B38)
