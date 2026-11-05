-- The debug flag $C234 bit 0 kept on (prepend TEST = 'gg': Game Genie FF9-BCE (US) / FF9-D0E (Japan); 'gs': GameShark
-- 010134C2; 'ips': ROM= the patched ROM; 'none': retail). SCEN = 'menu': Select on the title menu (-> state $18, the debug menu, $08:4328);
-- 'start': Down + Select + A on New Game (-> the debug start template $3E:4324, $08:42BB), then the bag pages.
KEEP0 = true
local function add(t, c) local ok, e = pcall(emu.addCheat, t, c) print('cheat', c, ok, e) end
if TEST == 'gg' then at(function() add(emu.cheatType.gbGameGenie, VER == 'jp' and 'FF9-D0E' or 'FF9-BCE') end) end
if TEST == 'gs' then at(function() add(emu.cheatType.gbGameShark, '010134C2') end) end
if SCEN == 'menu' then
  wait(1500) press({start=true}) wait(120) at(function() print('C234', rd(0xC234)) end) press({select=true},8) wait(120)
  at(function() shot('dbg_'..TEST..'_'..VER) print(TEST, VER, 'state', rd(0xC3E1)) end)
  press({start=true},8) wait(200) at(function() shot('dbg2_'..TEST..'_'..VER) print('after Start, state', rd(0xC3E1)) end)
else
  new_game(true)
  at(function() print(TEST, VER, 'C234', rd(0xC234), 'max HP', rd(BLOCK), 'HP', rd(BLOCK + 1)) shot('start_'..TEST..'_'..VER) end)
  for p = 0, 2 do open_page(p) at(function() shot('page'..p..'_'..TEST..'_'..VER) end) close_page() end
end
