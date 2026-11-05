-- Charabom Select with every Charabom owned (GameShark 8001xxA1, ids 0-29): new game, Start, A, then Down 31 times,
-- a shot each (c1..c31). tools/max/run.sh tools/max/cards.lua VER; items.py rips the art.
at(function() for n=0,29 do local a=0x10+8*n emu.addCheat(emu.cheatType.gbGameShark, string.format('8001%02X%02X',a&0xFF,0xA1+(a>>8))) end end)
start_new() wait(10)
press({start=true}) wait(120) press({a=true}) wait(150)
for k=1,31 do at(function() shot('c'..k) end) press({down=true}) wait(30) end
