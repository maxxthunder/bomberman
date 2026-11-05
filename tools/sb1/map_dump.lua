-- Dump the stage map buffer $0916-$0C55 (32 x 13 cells of 2 bytes, cell = row*64 + col*2) of every scene in
-- LIST (default: stages $00-$2F and battle stages $3D-$48) right after it loads, plus a screenshot.
-- tools/sb1/run.sh tools/sb1/map_dump.lua us > out; python tools/sb1/maps.py out docs/img/sb1/maps
LIST=LIST or nil
local l={} if LIST then l=LIST else for v=0,0x2F do l[#l+1]=v end for v=0x3D,0x48 do l[#l+1]=v end end
local pcs={}  -- which code writes the buffer while a stage loads
local function cb() local s=emu.getState() local k=string.format('%02x%04x',s['cpu.k'],s['cpu.pc']) pcs[k]=(pcs[k] or 0)+1 end
wait(900)
for _,v in ipairs(l) do
  at(function() emu.write(0x0314,emu.read(0x0314,W)&0xBF,W) emu.write(0xA4,v,W) pcs={}
    if not CBS then CBS=true for _,b in ipairs({0x000000,0x7E0000,0x800000}) do emu.addMemoryCallback(cb, emu.callbackType.write, b+0x0916, b+0x0C55) end end end)
  wait(WAITF or 240)
  at(function()
    local t={} for a=0x0916,0x0C55 do t[#t+1]=string.format('%02x',emu.read(a,W)) end
    print(string.format('MAP %02x %02x ',v,emu.read(0xD10,W))..table.concat(t))
    local p={} for k,n in pairs(pcs) do p[#p+1]=k..'x'..n end print(string.format('PCS %02x ',v)..table.concat(p,' '))
  end)
  S(string.format('map_%02x',v))
end
