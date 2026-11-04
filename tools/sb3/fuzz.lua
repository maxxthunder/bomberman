-- Fuzz the game's own password decoder. From a savestate on the PASSWORD screen: poke each code into $7E5429-542C,
-- press Start, and log what the decoder at $C2:67DB left behind (exec hook on its RTL at $C2:67FC):
-- "F code $0FF1 $0346 $5430 $2901 $2902", or "none" if it never ran. Needs FROM/TO globals; RTL=0xC267F4 for the beta.
-- Savestates can only be made inside an exec callback, so the main loop ($C0:0024) does it on request.
res=nil want=nil
emu.addMemoryCallback(function() if want=='save' then st=emu.createSavestate() elseif want=='load' then emu.loadSavestate(st) end want=nil end,
  emu.callbackType.exec, 0xC00024, 0xC00024)
emu.addMemoryCallback(function() res=string.format('%02x %02x %02x %02x %02x', r8(0x0FF1), r8(0x0346), r8(0x5430), r8(0x2901), r8(0x2902)) end,
  emu.callbackType.exec, RTL or 0xC267FC, RTL or 0xC267FC)
to_password() wait(30)
at(function() want='save' end) wait(1)
for n=FROM,TO do
  local code=string.format('%04d',n)
  at(function() want='load' end)
  at(function() res=nil for i=1,4 do w8(0x5428+i, tonumber(code:sub(i,i))) end end)
  for i=1,3 do q[#q+1]={start=true} end
  wait(3)
  at(function() print('F '..code..' '..(res or 'none')) end)
end
