-- helpers for SB3 Mesen scripts (prepend). cdl_dump() prints the PRG code/data log as hex.
function cdl_dump(name) at(function()
  local c=emu.getCdlData(emu.memType.snesPrgRom) local t={}
  for i=1,#c do t[#t+1]=string.format('%02x',c[i]) end print('CDLHEX '..(name or 'c')..' '..table.concat(t)) end) end
function r8(a) return emu.read(a,emu.memType.snesWorkRam) end
function w8(a,v) emu.write(a,v,emu.memType.snesWorkRam) end
