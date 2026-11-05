-- Cheat check (Mesen gbGameGenie / gbGameShark). Prepend TEST ('inv', 'clear', 'none') and CODE (stage password);
-- run with tools/gb1/run.sh. A random-input bot plays FR frames; counted: player hits (exec of the dying-state
-- store $01:4861, same address in both), sets won ($C590 = 2 at the set end) and lost, and the stage reached ($C3F0).
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
local INV = ({jp={'C98-37B-D5D'}, wario={'C98-37B-D5D'}})[VER]
local HIT = ({jp=0x4861, wario=0x4861})[VER]
local hits, won, lost = 0, 0, 0
at(function()
  if TEST == 'inv' then for _, c in ipairs(INV) do add(emu.cheatType.gbGameGenie, c) end end
  if TEST == 'clear' then for _, c in ipairs({'010000C1', '010000C2', '010000C3'}) do add(emu.cheatType.gbGameShark, c) end end
  on_exec(1, HIT, function() hits = hits + 1 end)
  emu.addMemoryCallback(function(a, v) if v == 2 then won = won + 1 elseif v == 1 then lost = lost + 1 end end,
    emu.callbackType.write, 0xC590, 0xC590, emu.cpuType.gameboy, BUS)
end)
to_password() type_pw(CODE or '4696') wait(600)
bot(FR or 6000, 11)
at(function() shot(TEST..'_'..VER) print(TEST, VER, 'hits', hits, 'sets won', won, 'lost', lost, 'stage $C3F0', rd(0xC3F0)) end)
