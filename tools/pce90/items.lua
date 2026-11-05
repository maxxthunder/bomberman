-- Reveal the fire, bomb and roller-skate items on 1-1 and dump VRAM/palette after each (for items.py).
-- An item hides in a soft block (cell low bits 3, map $244A) listed in the slot table $2F9B (active $80 | kind),
-- $2FB4 (x), $2FCD (y). Kinds (jump table $09:877A): 0 fire, 1 bomb, 3 skate. Deaths off: fire hit $09:8AB3 -> RTS.
local function hexmem(mt, n) local t = {} for a = 0, n - 1 do t[#t + 1] = string.format('%02x', emu.read(a, mt)) end return table.concat(t) end
local function vd(n) at(function() print('VRAM' .. n .. ' ' .. hexmem(emu.memType.pceVideoRam, 0x10000)) print('PAL' .. n .. ' ' .. hexmem(emu.memType.pcePaletteRam, 0x400)) end) end
local function hide(slot, x, y, kind) emu.write(0x44a + 32 * y + x, 0xc3, W) emu.write(0xf9b + slot, 0xc0 + kind, W) emu.write(0xfb4 + slot, x, W) emu.write(0xfcd + slot, y, W) end
emu.write(0x12AB3, 0x60, emu.memType.pcePrgRom)
wait(300) for i = 1, 6 do press({run = true}) wait(100) end wait(200)   -- through the intro into 1-1; Bomberman on cell (2,1)
at(function() hide(1, 3, 1, 0) hide(2, 2, 2, 1) end) press({i = true}) wait(200) S('items1') vd(1)   -- fire (3,1), bomb (2,2)
at(function() hide(1, 3, 1, 3) end) press({i = true}) wait(200) S('items2') vd(2)                     -- skate (3,1)
