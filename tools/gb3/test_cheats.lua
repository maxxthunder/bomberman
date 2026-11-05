-- Cheat check (Mesen gbGameShark / gbGameGenie). Prepend TEST ('inv', 'invgg', 'lives', 'clear', 'freeze', 'none'); run with tools/gb3/run.sh.
-- Wood 1 by password 0986400, then a random-input bot for FR frames. Counted: hits (exec of the dying state
-- $01:4C07), deaths (the death timer start $01:4CD3), stage changes ($C362 area / $C365 stage), lives $C363.
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
local hits, deaths = 0, 0
at(function()
  if TEST == 'inv' then add(emu.cheatType.gbGameShark, '0101BCC1') end
  if TEST == 'invgg' then for _, c in ipairs({'C3B-E6B-081', 'E4B-E7B-198', '4AB-E8B-E6D'}) do add(emu.cheatType.gbGameGenie, c) end end
  if TEST == 'freeze' then add(emu.cheatType.gbGameShark, '0101BDC1') end
  if TEST == 'lives' then add(emu.cheatType.gbGameShark, '010363C3') end
  if TEST == 'clear' then add(emu.cheatType.gbGameShark, CLR or '01FF80C4') end
  on_exec(1, 0x4C07, function() hits = hits + 1 end)
  on_exec(1, 0x4CD3, function() deaths = deaths + 1 end)
  local last = -1
  emu.addMemoryCallback(function(a, v) if v ~= last then print('C365', FRAME, v, 'area', rd(0xC362)) end last = v end,
    emu.callbackType.write, 0xC365, 0xC365, emu.cpuType.gameboy, BUS)
end)
start_game('0986400')
bot(FR or 6000, 11)
at(function() shot(TEST..'_'..VER) print(TEST, VER, 'hits', hits, 'deaths', deaths, 'area', rd(0xC362), 'stage', rd(0xC365) + 1, 'lives', rd(0xC363)) end)
