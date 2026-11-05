-- Cheat check (Mesen gbGameGenie / gbGameShark): tools/max/run.sh tools/max/test_cheats.lua VER, with TEST
-- ('inv', 'lives', 'none'; 'none' with ROM= a patched ROM for the IPS check) and FR (frames) prepended. New game, area 1-01, a random-input bot. Counted: hits (the
-- player object $C705 set to $3C, the dying state, by $02:5356), lives $C2F7.
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
local hits = 0
at(function()
  if TEST == 'inv' then add(emu.cheatType.gbGameGenie, 'C32-EBA-C41') end
  if TEST == 'lives' then add(emu.cheatType.gbGameShark, '0103F7C2') end
  emu.addMemoryCallback(function(a, v) if v == 0x3C then hits = hits + 1 end end, emu.callbackType.write, 0xC705, 0xC705, emu.cpuType.gameboy, BUS)
end)
start_new()
bot(FR or 6000, 11)
at(function() shot(TEST..'_'..VER) print(TEST, VER, 'hits', hits, 'lives', rd(0xC2F7), 'state', rd(0xC705)) end)
