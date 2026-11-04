-- VS CHECK on 1-5 (patched ROM): marks left by the blue enemy's path search, off vs on
local st, want = nil, false
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(700)
press({select=true},2) wait(4) for k=1,4 do press({right=true},1) end press({select=true},2) wait(400)
at(function() emu.addMemoryCallback(function()
  if not st then st=emu.createSavestate() end
  if want then emu.loadSavestate(st) want=false end
end, emu.callbackType.exec, 0xC60000, 0xC60000) end)
wait(2)
for _,on in ipairs({false,true}) do
  at(function() want=true end) wait(2)
  if on then press({select=true},2) wait(4) for k=1,3 do press({up=true},2) end press({right=true},2) wait(2) S('vs_menu') press({select=true},2) end
  wait(60) S(on and 'vs_on1' or 'vs_off1') wait(120) S(on and 'vs_on2' or 'vs_off2')
  at(function() local n=0 for a=0x4F5,0x8F3,2 do if emu.read(a,W)&2~=0 then n=n+1 end end print('on',on,'marked cells',n, 'B4', emu.read(0xB4,W)) end)
end
