-- PPU dump helper (prepended by the scripts that need it): vdump(name) queues, vdump_now(name) prints now,
-- 'VDUMP <name> PPU <hex of $0000-$2FFF> PAL <hex of 32 palette bytes> OAM <hex of 256> CTRL <PPUCTRL>'
-- for logo.py / items.py.
function vdump_now(name)
  local t = {} for a = 0, 0x2FFF do t[#t+1] = string.format('%02x', emu.read(a, emu.memType.nesPpuMemory)) end
  local p = {} for a = 0, 31 do p[#p+1] = string.format('%02x', emu.read(a, emu.memType.nesPaletteRam)) end
  local o = {} for a = 0, 255 do o[#o+1] = string.format('%02x', emu.read(a, emu.memType.nesSpriteRam)) end
  local s = emu.getState()
  local ctrl = (s['ppu.control.backgroundPatternAddr'] or 0) == 0x1000 and 0x10 or 0
  ctrl = ctrl | ((s['ppu.control.spritePatternAddr'] or 0) == 0x1000 and 0x08 or 0) | (s['ppu.control.largeSprites'] and 0x20 or 0)
  print('VDUMP '..name..' PPU '..table.concat(t)..' PAL '..table.concat(p)..' OAM '..table.concat(o)..' CTRL '..string.format('%02x', ctrl))
end
function vdump(name) at(function() vdump_now(name) end) end
