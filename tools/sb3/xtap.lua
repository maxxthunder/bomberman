-- Title-screen X tapping (hidden battle stages 11-12). PER = frames between X presses (globals PER, N presses).
-- Logs every write to $7E542D (stage count: 10, or 12 once unlocked by $C1:6EC3).
emu.addMemoryCallback(function(a,v) local s=emu.getState() print(string.format('WR %02x:%04x frame=%d 542D=%02x',s['cpu.k'],s['cpu.pc'],s['ppu.frameCount'],v)) end, emu.callbackType.write, 0x7E542D, 0x7E542D)
wait(200)
for i=1,N do q[#q+1]={x=true} for j=2,PER do q[#q+1]={} end end
wait(60) at(function() print('END 542D='..r8(0x542D)) end)
