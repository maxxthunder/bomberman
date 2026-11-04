-- Debug-menu effects in play (run on a ROM patched by make_debug_ips.py: run.sh this.lua us patched.sfc).
-- Savestate in 1-1 after the start invincibility; each test opens the menu (Select), presses keys, closes it, acts.
TESTS={
 {name='nd_off', keys={'down','right','right'}, act={'a',60,'pl',140,'pl',300,'pl'}},
 {name='base', act={'a',60,'pl',140,'shot','pl',300,'pl'}},
 {name='nodeath', keys={'down','right'}, act={'a',60,'pl',140,'shot','pl',300,'pl'}},
 {name='firepass', keys={'down','down','down','down','down','down','down','down','down','right'}, act={'pl','a',200,'shot','pl',300,'pl'}},
 {name='firefull', keys={'down','right','down','down','down','right','right','right','down','down','down','down','down','down','right'}, shot=true, act={'a',115,'shot',10,'shot'}},
 {name='stage', keys={'right','right','right','right','right','right','right','right','right'}, shot=true, act={'a',600,'pl',300,'pl','shot'}},
 {name='skull', keys={'up','up','up','up','up','right'}, act={'pl','down',30,'shot',60,'shot','pl'}},
 {name='bgm', keys={'up','up','right','right','right','a'}, shot=true, act={60,'pl'}},
 {name='se', keys={'up','right','right','right','a'}, act={60,'pl'}},
}
local st, want = nil, false
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(1500)
at(function() emu.addMemoryCallback(function()
  if not st then st=emu.createSavestate() end
  if want then emu.loadSavestate(st) want=false end
end, emu.callbackType.exec, 0xC60000, 0xC60000)
emu.addMemoryCallback(function() local s=emu.getState() print('  music call C3:002C Y='..string.format('%02x',s['cpu.y'] & 0xFF)) end, emu.callbackType.exec, 0xC3002C, 0xC3002C)
emu.addMemoryCallback(function() local s=emu.getState() print('  sound call C3:0042 Y='..string.format('%02x',s['cpu.y'] & 0xFF)) end, emu.callbackType.exec, 0xC30042, 0xC30042) end)
wait(2)
local P=0x0D40
local function pl(tag) at(function()
  print(tag, string.format('lives=%d state=%06x 2E=%02x 31=%02x 36=%04x 39=%02x 13A=%04x A4=%02x 0D16=%02x 0D17=%02x', emu.read(P+0x3D,W), emu.read16(P,W)|emu.read(P+2,W)<<16, emu.read(P+0x2E,W), emu.read(P+0x31,W), emu.read16(P+0x36,W), emu.read(P+0x39,W), emu.read16(P+0x13A,W), emu.read(0xA4,W), emu.read(0xD16,W), emu.read(0xD17,W))) end) end
for _,t in ipairs(TESTS) do
  at(function() want=true print('== '..t.name) end) wait(2)
  if t.keys then press({select=true},2) wait(4) for _,k in ipairs(t.keys) do press({[k]=true},2) end wait(4) if t.shot then S(t.name..'_menu') end press({select=true},2) wait(4) end
  pl(' after menu')
  for _,a in ipairs(t.act or {}) do if type(a)=='number' then wait(a) elseif a=='shot' then S(t.name..'_'..#q) elseif a=='pl' then pl(' ') else press({[a]=true},2) end end
  pl(' end')
end
