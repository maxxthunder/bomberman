-- Cheat check (Mesen gbGameShark / gbGameGenie): prepend TEST ('inv' GameShark, 'invgg' Game Genie, 'none'; 'none'
-- with ROM= a patched ROM for the IPS check). A new game, west to the first field screens, the Normal Bomb put on A,
-- then BOMBS times: a bomb dropped at Bomberman's feet and 150 frames standing on it. Counted: HP drops (writes to the
-- in-play HP $C390 that lower it, $09:5938) and hits (the damage routine $09:58B1 entered).
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
local drops, hits = 0, 0
new_game(false)
to_field()
at(function()
  if TEST == 'inv' then add(emu.cheatType.gbGameShark, '018034C2') end
  if TEST == 'invgg' then add(emu.cheatType.gbGameGenie, '189-26A-6EA') end
  emu.addMemoryCallback(function(a, v) if v < rd(0xC390) then drops = drops + 1 end end, emu.callbackType.write, 0xC390, 0xC390, emu.cpuType.gameboy, BUS)
  on_exec(9, 0x58B1, function() hits = hits + 1 end)
  arm()
end)
for k = 1, BOMBS or 10 do press({a=true},8) wait(150) if k == 2 then at(function() shot(TEST..'_'..VER) end) end end
at(function() print(TEST, VER, 'hits', hits, 'drops', drops, 'hp', rd(0xC390), 'max', rd(0xC38E)) end)
