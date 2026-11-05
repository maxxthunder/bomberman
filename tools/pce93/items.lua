-- Reveal the fire, bomb and skate items on US 1-1 and dump VRAM/palette after each (for items.py).
-- Map: one byte per cell at $2FD7 + 16y + x (low nibble 2 soft block, C floor, 0 wall). Items: slot table $3BEB (kind),
-- $3C09 (x), $3C27 (y); kinds $A0 + index of the pickup table 03:A89F: $A0 fire, $A1 bomb, $A3 skate.
-- Fire-proof all along: player $91 bit 3 (the vest, fire check 02:8C9D).
local function hide(slot, x, y, kind) local a = 0x2fd7 + 16 * y + x wr(a, r(a) & 0xF0 | 2) wr(0x3beb + slot, kind) wr(0x3c09 + slot, x) wr(0x3c27 + slot, y) end
to_password() type_pw({1, 0, 1, 1, 0, 0, 2, 0}) submit(22) wait(400) for i = 1, 6 do press({run = true}) wait(150) end wait(100)
at(function() emu.addEventCallback(function() wr(0x2091, r(0x2091) | 8) end, emu.eventType.endFrame) hide(2, 3, 1, 0xa0) hide(3, 2, 2, 0xa1) end)
press({i = true}) wait(250) S('items1') at(function() vdump('items1') end)   -- Bomberman on (2,1): fire (3,1), bomb (2,2)
at(function() hide(2, 3, 1, 0xa3) end) press({i = true}) wait(250) S('items2') at(function() vdump('items2') end)   -- skate (3,1)
