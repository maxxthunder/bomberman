-- Special Select Room. Set HUND (high-score hundreds digit), THOU (thousands digit, optional), CUT (true = Run
-- during the demo) and NORESET (true = skip the soft reset) first. Prints the round and $10; check sr_result.png.
-- Power on, write the high score ($2000-$2007, ones digit = tens of points), soft reset (hold Select, press Run),
-- hold Down+Select+I+II while the demo runs (so the title menu never sees a new Down/Select press), press Run on the
-- title, keep everything held through the intro.
local hold = {down = true, select = true, i = true, ii = true}
local all = {down = true, select = true, i = true, ii = true, run = true}
wait(200)
at(function() for k = 0, 7 do emu.write(k, 0, W) end emu.write(1, HUND, W) emu.write(2, THOU or 0, W) end)
if not NORESET then press({select = true}, 10) q[#q+1] = {select = true, run = true} q[#q+1] = {select = true, run = true} wait(10) end
at(function() print('after reset: hi', emu.read(1, W), 'demo flag', emu.read(0x10, W)) end)
wait(60)
wait_until(function() return emu.read(0x10, W) == 1 end, hold)   -- held during the demo; $10 = 1 when it ends by itself
if CUT then at(function() emu.write(0x10, 0, W) end) end          -- as if Run had cut the demo short ($0B:CDC2)
for f = 1, 700 do q[#q+1] = hold end   -- held before the menu takes input, so Down does not move the cursor
S('sr_title') at(function() print('cursor', emu.read(0x13B4, W)) end)
for f = 1, 2600 do q[#q+1] = all end
S('sr_result') D('sr_result')
at(function() print('round', emu.read(0x84A, W), '$10', emu.read(0x10, W)) end)
