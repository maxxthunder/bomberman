-- Prepend to a coverage run (tools/sb1/coverage.lua, tools/sb2/coverage2.lua): counts the CPU writes to each
-- address in WATCH (24-bit; low-RAM addresses are also watched in their $00/$7E/$80 mirrors) and prints
-- 'WATCH <addr> <writes> <last value> <first writer pc>' every 5000 frames and at the end of the queue.
WATCH=WATCH or {}
local cnt,val,pcw={},{},{}
for _,a in ipairs(WATCH) do
  cnt[a]=0
  local m={a} if a<0x2000 then m={a,0x7E0000+a,0x800000+a} end
  for _,x in ipairs(m) do
    emu.addMemoryCallback(function(_,v) cnt[a]=cnt[a]+1 val[a]=v
      if not pcw[a] then local s=emu.getState() pcw[a]=string.format('%02X%04X',s['cpu.k'],s['cpu.pc']) end end,
      emu.callbackType.write, x, x)
  end
end
local fw=0
function watch_report() for _,a in ipairs(WATCH) do print(string.format('WATCH %06X %d %s %s',a,cnt[a],val[a] and string.format('%02X',val[a]) or '-',pcw[a] or '-')) end end
emu.addEventCallback(function() fw=fw+1 if fw%5000==0 then watch_report() end end, emu.eventType.endFrame)
