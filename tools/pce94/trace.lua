-- Code coverage for huc6280.py: records every executed instruction as (ROM offset, 8 KB page it ran in).
-- Prepend to a play script and call trace_dump() at the end; prints "E <phys hex> <page>" lines (entries.txt format).
TR={} local PRG=emu.memType.pcePrgRom
emu.addMemoryCallback(function(a)
  local r=emu.convertAddress(a, emu.memType.pceMemory)
  if r.memType==PRG then TR[r.address*8+(a>>13)]=true end
end, emu.callbackType.exec, 0x0000, 0xFFFF)
function trace_dump() local n=0 for k in pairs(TR) do print(string.format('E %05X %d', k>>3, k&7)) n=n+1 end print('traced '..n) end
