-- Fuzz the game's own password checker ($1B27C, bank $0D at $A000-$BFFF). From a savestate on the PASSWORD screen
-- (pw.mst, made by mkstates.lua): write each code's digits to $2FBE-$2FC1 (leftmost first), press I, and log what
-- the checker left at its exits: accept $B343 -> "F code ok $B2 $B3 $B5", reject $B367 -> "F code bad", or
-- "F code none" if it never ran. Needs FROM/TO globals (run.sh fuzz.lua card FROM=0 TO=6476, then
-- FROM=6477 TO=9999: one test-runner session times out after about 6,400 codes). Check: password.py --fuzz log.txt.
res=nil
local function here() return emu.convertAddress(emu.getState()['cpu.pc'], emu.memType.pceMemory).address end
emu.addMemoryCallback(function() if here()==0x1B343 then res=string.format('ok %02x %02x %02x', r8(0x20B2), r8(0x20B3), r8(0x20B5)) end end,
  emu.callbackType.exec, 0xB343, 0xB343)
emu.addMemoryCallback(function() if here()==0x1B367 then res='bad' end end, emu.callbackType.exec, 0xB367, 0xB367)
loadfile('pw.mst') wait(4) q[#q+1]={i=true} wait(8)   -- warm-up press (the first one after a load is missed)
for n=FROM,TO do
  local code=string.format('%04d',n)
  at(function() want='load' end) wait(1)
  at(function() res=nil for i=1,4 do w8(0x2FBD+i, tonumber(code:sub(i,i))) end end)
  q[#q+1]={i=true} q[#q+1]={i=true} wait(2)
  at(function() print('F '..code..' '..(res or 'none')) end)
end
