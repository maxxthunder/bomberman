-- Cheat check (Mesen gbGameShark / gbGameGenie). Prepend TEST ('inv', 'invgg', 'lives', 'none'); run with tools/pocket/run.sh.
-- Forest 1 by password 7693 (CODE), then a random-input bot for FR frames (SEED). Counted: deaths (the lives decrement
-- $02:536A); printed with lives $C1F1, world $C1DC, stage $C1DD. 'ips': no cheat, run with ROM set to a patched copy.
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
local deaths = 0
at(function()
  if TEST == 'inv' then add(emu.cheatType.gbGameShark, '0101CCC2') end
  if TEST == 'invgg' then add(emu.cheatType.gbGameGenie, 'C33-6FB-E61') add(emu.cheatType.gbGameGenie, '18D-C7B-6EA') end
  if TEST == 'lives' then add(emu.cheatType.gbGameShark, '0103F1C1') end
  on_exec(2, 0x536A, function() deaths = deaths + 1 end)
end)
start_game(CODE or '7693')
bot(FR or 6000, SEED or 11)
at(function() shot(TEST..'_'..VER) print(TEST, VER, 'deaths', deaths, 'lives', rd(0xC1F1), 'world', rd(0xC1DC), 'stage', rd(0xC1DD), 'frame', FRAME) cdl_dump('ch_'..TEST) end)
