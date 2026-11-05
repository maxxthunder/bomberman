-- Dump VRAM/CGRAM on the Config Battle ability editor for items.py, with a no-items character
-- (BXJPV5) so the item icons show without the OK marks. The item row shows 4 of the 9; A then Right x4 scrolls it
-- by one past the 4th, B leaves it. Dumps: 0 = items 0-3, 4 = items 1-4, 8 = items 5-8.
-- Prepend KEEPSRAM=true and lib.lua (emu.reset() crashes the test runner).
local function vd(n) at(function()
  local t = {} for a = 0, 0xFFFF do t[#t + 1] = string.format('%02x', emu.read(a, emu.memType.snesVideoRam)) end print('VRAM' .. n .. ' ' .. table.concat(t))
  t = {} for a = 0, 0x1FF do t[#t + 1] = string.format('%02x', emu.read(a, emu.memType.snesCgRam)) end print('CGRAM' .. n .. ' ' .. table.concat(t))
  shot('items' .. n) end) end
to_config_pw() at(function() inj('BXJPV5') end) press({a = true}) wait(200)
press({down = true}) wait(20) press({down = true}) wait(20) press({a = true}) wait(150)   -- body screen: NEXT
press({down = true}) wait(30) press({down = true}) wait(30) vd(0)                         -- cursor on the item row
for n = 4, 8, 4 do press({a = true}) wait(30) for i = 1, 4 do press({right = true}, 10) wait(30) end press({b = true}, 10) wait(30) vd(n) end
