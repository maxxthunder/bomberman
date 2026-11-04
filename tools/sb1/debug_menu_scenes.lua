-- STAGE NO. entries past the 48 stages: warp to each scene and screenshot (patched ROM).
VALS={0x30,0x31,0x32,0x33,0x37,0x38,0x39,0x3a,0x3b,0x3c,0x3d,0x48,0x4b,0x4c,0x4d}
local st, want = nil, false
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(700)
at(function() emu.addMemoryCallback(function()
  if not st then st=emu.createSavestate() end
  if want then emu.loadSavestate(st) want=false end
end, emu.callbackType.exec, 0xC60000, 0xC60000) end)
wait(2)
for _,v in ipairs(VALS) do
  at(function() want=true end) wait(2)
  press({select=true},2) wait(4)
  if v<=39 then for k=1,v do press({right=true},1) end else for k=1,78-v do press({left=true},1) end end
  wait(2) S(string.format('st%02x_menu',v)) press({select=true},2) wait(400) S(string.format('st%02x',v))
  at(function() print(string.format('val %02x A4=%02x 0D10=%02x', v, emu.read(0xA4,W), emu.read(0xD10,W))) end)
end
