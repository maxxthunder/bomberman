-- Dump VRAM, palette RAM and SAT plus VDC state at the title screen (for logo.py). LOGO_FRAME = frame to dump at.
local function hexmem(mt, n) local t = {} for a = 0, n - 1 do t[#t + 1] = string.format('%02x', emu.read(a, mt)) end return table.concat(t) end
wait(LOGO_FRAME or 600)
at(function()
  print('VRAM ' .. hexmem(emu.memType.pceVideoRam, 0x10000))
  print('PAL ' .. hexmem(emu.memType.pcePaletteRam, 0x400))
  print('SAT ' .. hexmem(emu.memType.pceSpriteRam, 0x200))
  local s = emu.getState() local ks = {} for k, v in pairs(s) do if k:find('^vdc') or k:find('^vce') then ks[#ks + 1] = k .. '=' .. tostring(v) end end
  table.sort(ks) print('STATE ' .. table.concat(ks, ' '))
end)
S('title')
