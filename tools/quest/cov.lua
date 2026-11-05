-- Coverage run for the dead-code sweep: prepend SCEN; tools/quest/cov.sh runs them all and keeps each CDL.
-- idle: boot, Hudson logo, title and attract for 8000 frames. battle: Battle on the title menu (no link partner).
-- new: New Game, intro, Peace Town and the fields west of it with the bot (invincible, the Normal Bomb on A).
-- debug: the debug start (flag forced) and every bag page and the monster book. test: the debug menu (Game Genie
-- FF9-BCE / FF9-D0E keeps the flag), its sound test, colour test and character viewer. load: a save made by
-- makeSave-equivalent bytes (the normal start's block) written to cart RAM before boot, then Continue.
local function bots(n) for k = 1, n do bot(500, k) press({a=true}) press({b=true}) end end
if SCEN == 'idle' then wait(8000)
elseif SCEN == 'battle' then wait(1500) press({start=true}) wait(120) press({down=true}) wait(20) for k = 1, 20 do press({a=true}) wait(60) end press({b=true}) wait(300)
elseif SCEN == 'new' then
  new_game(false) at(function() emu.addCheat(emu.cheatType.gbGameShark, '018034C2') arm() end) bots(4)
  to_field() at(arm) bots(20) press({select=true}) wait(120) press({select=true}) wait(60) bots(8)
elseif SCEN == 'debug' then
  new_game(true) for p = 0, 2 do open_page(p) for k = 1, 30 do press({right=true}) press({down=true}) end close_page() end
  press({start=true},8) wait(60) press({right=true},8) wait(20) press({a=true},8) wait(40)
  for z = 0, 3 do press({a=true},8) wait(40) for k = 1, 20 do press({right=true}) press({down=true}) end press({b=true},8) wait(30) press({right=true},8) wait(20) end
  close_page() at(function() emu.addCheat(emu.cheatType.gbGameShark, '018034C2') end) to_field() bots(10)
elseif SCEN == 'test' then
  at(function() emu.addCheat(emu.cheatType.gbGameGenie, VER == 'jp' and 'FF9-D0E' or 'FF9-BCE') end)
  wait(1500) press({start=true}) wait(120) press({select=true},8) wait(120)
  for _, b in ipairs({'select', 'up', 'b', 'down'}) do press({[b]=true},8) wait(200)
    for k = 1, 10 do press({right=true}) press({a=true}) wait(30) press({down=true}) end
    press({b=true},8) wait(100) press({start=true},8) wait(200) press({select=true},8) wait(120) end
end
at(function() shot('end_'..SCEN) cdl_dump('cov_'..SCEN) end)
