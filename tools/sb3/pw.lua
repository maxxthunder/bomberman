-- Prepend after cdl.lua. Boot to the PASSWORD screen. EU needs 3 Starts before Down; JP and the beta (60 Hz, title
-- menu already up at frame 1250) need 2: set ADV=2 for them.  pw_enter("5358") injects digits and presses Start.
function to_password() wait(1250) for i=1,(ADV or 3) do press({start=true}) wait(60) end
  press({down=true}) wait(20) press({start=true}) wait(200) end
function pw_inject(s) at(function() for i=1,4 do w8(0x5428+i, tonumber(s:sub(i,i))) end end) end
function pw_enter(s) pw_inject(s) wait(2) press({start=true}) end
function state(tag) at(function()
  local t={} for _,a in ipairs({0x0FF1,0x0FF2,0x0346,0x0349,0x5429,0x542A,0x542B,0x542C,0x542D,0x542E,0x542F,0x5430,0x2900,0x2901,0x2902,0x4C0C,0x6C6E,0x6C6F}) do t[#t+1]=string.format('%04x=%02x',a,r8(a)) end
  print('ST '..tag..' '..table.concat(t,' ')) end) end
-- log the PC of every read of WRAM addresses lo..hi (once per PC+addr)
seen={}
function watch(lo,hi) emu.addMemoryCallback(function(a,v) local s=emu.getState() local k=string.format('%02x:%04x %06x',s['cpu.k'],s['cpu.pc'],a)
  if not seen[k] then seen[k]=1 print('RD '..k) end end, emu.callbackType.read, 0x7E0000+lo, 0x7E0000+hi) end
