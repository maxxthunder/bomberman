-- Cheat check (Mesen gbGameGenie / gbGameShark). Prepend TEST ('inv', 'lives', 'clear', 'none'); run with
-- tools/gb2/run.sh [jp|us]. World 1 MODE-A by password 8566, then a random-input bot for FR frames. Counted: deaths
-- (exec of $01:531E, which sets the dead flag $C104), stage clears (writes to $C100 that raise it), lives $C106.
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
local deaths, clears, over = 0, 0, 0
at(function()
  if TEST == 'inv' then for _, c in ipairs({'C92-96A-6EB', 'C92-ACA-6EB', 'C93-03A-6EB'}) do add(emu.cheatType.gbGameGenie, c) end end
  if TEST == 'lives' then add(emu.cheatType.gbGameShark, '010306C1') end
  if TEST == 'clear' then add(emu.cheatType.gbGameShark, '010103C1') add(emu.cheatType.gbGameShark, '010004C1') end
  on_exec(1, 0x531E, function() deaths = deaths + 1 end)
  on_exec(0, 0x255F, function() over = over + 1 end)
  local last = rd(0xC100)
  emu.addMemoryCallback(function(a, v) if v > last then clears = clears + 1 end if v ~= last then print('C100', FRAME, string.format('%02X', v)) end last = v end,
    emu.callbackType.write, 0xC100, 0xC100, emu.cpuType.gameboy, BUS)
end)
start_game('8566', 'A')
bot(FR or 6000, 11)
at(function() shot(TEST..'_'..VER) print(TEST, VER, 'deaths', deaths, 'game overs', over, 'stage clears', clears, 'C100', string.format('%02X', rd(0xC100)), 'lives', rd(0xC106)) end)
