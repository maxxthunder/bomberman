-- Type each code with real button presses (Up x digit, A to move on; the 4th A submits) from a savestate
-- on the password screen, then read the stage the game set up. Codes come from CODES (set by the caller).
local st, want = nil, false
to_password()
at(function()
  emu.addMemoryCallback(function()
    if not st then st=emu.createSavestate() end
    if want then emu.loadSavestate(st) want=false end
  end, emu.callbackType.exec, 0x00FF8C, 0x00FF8C)
end)
wait(2)
for _,c in ipairs(CODES) do
  at(function() want=true end) wait(2)
  for i=1,4 do local d=tonumber(c:sub(i,i)) for k=1,d do press({up=true},2) end press({a=true},2) end
  at(function() print(string.format('T %s a4=%02x c90=%d', c, emu.read(0xA4,W), emu.read(0xC90,W))) end)
  wait(420)
  at(function() print(string.format('G %s a4=%02x stage=%02x lives=%d', c, emu.read(0xA4,W), emu.read(0xD17,W), emu.read(0xD7D,W))) end)
  if SHOT then S('typed_'..c) end
end
