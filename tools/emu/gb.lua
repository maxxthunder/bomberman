-- Game Boy prelude: mesen.py adds it after its own for a .gb/.gbc ROM. rd/wr on the bus, dump (WRAM $C000-$DFFF then
-- HRAM $FF80-$FFFE -> <name>.ram), vdump (VRAM 8 KB, OAM 160, BGP/OBP0/OBP1, LCDC, SCY, SCX, WY, WX -> <name>.vram),
-- cdl_dump (-> <name>.cdl), hold(buttons, n), FRAME. An at() function may return the input to hold that frame.
WR=emu.memType.gbWorkRam HR=emu.memType.gbHighRam VR=emu.memType.gbVideoRam OAM=emu.memType.gbSpriteRam
ROM=emu.memType.gbPrgRom BUS=emu.memType.gameboyMemory
function rd(a) return emu.read(a, BUS) end
function wr(a,v) emu.write(a, v, BUS) end
function dump(name) local t={} for a=0,0x1FFF do t[#t+1]=string.format('%02x',emu.read(a,WR)) end
  for a=0,0x7E do t[#t+1]=string.format('%02x',emu.read(a,HR)) end print('DUMP '..name..' '..table.concat(t)) end
function vdump(name) local t={} for a=0,0x1FFF do t[#t+1]=string.format('%02x',emu.read(a,VR)) end
  for a=0,159 do t[#t+1]=string.format('%02x',emu.read(a,OAM)) end
  for _,a in ipairs({0xFF47,0xFF48,0xFF49,0xFF40,0xFF42,0xFF43,0xFF4A,0xFF4B}) do t[#t+1]=string.format('%02x',rd(a)) end
  print('VRAM '..name..' '..table.concat(t)) end
function cdl_dump(name) local c=emu.getCdlData(ROM) local t={}
  for i=0,#c do t[#t+1]=string.format("%02x",c[i] or 0) end print('CDLHEX '..(name or 'cdl')..' '..table.concat(t)) end
function hold(b,n) for i=1,n do q[#q+1]=b end end
FRAME=0
function tick()
  FRAME=FRAME+1
  local s=table.remove(q,1)
  if s==nil then emu.stop(0) return end
  if type(s)=="function" then s=s() or {} end
  emu.setInput(s,0)
end
