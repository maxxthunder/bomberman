-- Item icon dumps for items.py: NORMAL MODE 1-1, invincible ($04E6/$04E8 held), random bot; the PPU is dumped
-- (vdump_now) the first frame a whole bomb-up ($60 61 70 71) or fire-up ($62 63 72 73) icon is in a nametable with the palette lit. Prepend ../nes1/vdump.lua.
local done, f = {}, 0
emu.addEventCallback(function() emu.write(0x4E6, 1, R) emu.write(0x4E8, 9, R) f = f + 1
  if f % 10 == 0 then for a = 0x2000, 0x27BF do local t = emu.read(a, emu.memType.nesPpuMemory)
    local P = function(x) return emu.read(x, emu.memType.nesPpuMemory) end
    local lit = emu.read(1, emu.memType.nesPaletteRam) ~= emu.read(0, emu.memType.nesPaletteRam) and emu.getState()['ppu.mask.backgroundEnabled']  -- shown, not faded out
    if (t == 0x60 or t == 0x62) and lit and not done[t] and a % 0x400 < 0x3C0 and P(a + 1) == t + 1 and P(a + 32) == t + 16 and P(a + 33) == t + 17 then done[t] = true print('ITEM', t, string.format('%04X', a)) vdump_now('item'..t) shot('item'..t) break end end end
end, emu.eventType.endFrame)
to_menu() press({start=true}) wait(300) bot(FR or 20000, SEED or 4)
