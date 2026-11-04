-- Set H/OK/INV first (see fuzz.sh). Exhaustive check of the real decoder: every 4-digit code 0000-7777 is written into the entry digits
-- ($1030-$1033) from a savestate taken on the password screen, then Start is held.
local st, i, res, armed = nil, 0, {}, false
local function nextcode()
  if i > 4095 then print('RES '..table.concat(res,' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  for k=0,3 do emu.write(0x1030+k, (i>>(3*(3-k)))&7, W) end
end
local function rec(v) res[#res+1]=string.format('%04o:%s', i, v) i=i+1 nextcode() end
to_password()
at(function()
  emu.addMemoryCallback(function() if not st then st=emu.createSavestate() armed=true nextcode() end end, emu.callbackType.exec, H, H)
  emu.addMemoryCallback(function() rec(string.format('%02x', emu.getState()['cpu.a'] & 0xFF)) end, emu.callbackType.exec, OK, OK)
  emu.addMemoryCallback(function() rec(emu.read(0xC90,W)==1 and 'S' or 'X') end, emu.callbackType.exec, INV, INV)
end)
for f=1,30000 do q[#q+1]={start=true} end
