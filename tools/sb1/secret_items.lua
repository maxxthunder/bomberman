-- Secret-item check for one stage. Set PW (password), INJECT (function run once after the stage starts, or nil),
-- EXTRA (function queuing inputs after INJECT, or nil), HOLD (input table held for the wait, or nil) and WAITF (frames) first; see secret_items.py.
-- Prints SPAWN when the stage's secret object ($C6:2B03) calls the item spawner $C4:2483, then teleports
-- player 1 onto the item and prints score/lives before and after the pickup.
local P=0x0D40
local spawned=nil
function typepw(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for k=1,d do press({up=true},2) end press({a=true},2) end end
local function score() return string.format('%04x%04x', emu.read16(P+0x1A,W), emu.read16(P+0x1C,W)) end
to_password() typepw(PW) wait(450)
at(function()
  emu.addMemoryCallback(function() local s=emu.getState() local sp=s['cpu.sp']
    local lo=emu.read(sp+1,emu.memType.snesMemory) local hi=emu.read(sp+2,emu.memType.snesMemory)
    if spawned==nil and (hi*256+lo)-3==0x2B4C then spawned={item=s['cpu.a']&0x1f, cell=s['cpu.y'], from=(hi*256+lo)-3}
      print(string.format('SPAWN item=%02x cell=%03x from=c6%04x f=%d', spawned.item, spawned.cell, spawned.from, s['ppu.frameCount'])) end
  end, emu.callbackType.exec, 0xC42483, 0xC42483)
  print('START lives='..emu.read(P+0x3D,W)..' score='..score())
  if INJECT then INJECT() end
end)
if EXTRA then EXTRA() end
for i=1,WAITF do if HOLD then q[#q+1]=HOLD else q[#q+1]={} end end
if HOLD then wait(2) press({start=true},2) wait(20) end
at(function()
  if not spawned then print('NOSPAWN') return end
  print('BEFORE lives='..emu.read(P+0x3D,W)..' score='..score()..string.format(' state=%04x flags39=%02x ext=%04x%04x', emu.read16(P,W), emu.read(P+0x39,W), emu.read16(P+0x11A,W), emu.read16(P+0x11C,W)))
  if HOLD then HOLD=nil end
  local c=emu.read16(0x0916+spawned.cell,W)
  local y=spawned.cell; emu.write16(P+0x11,((y%64)//2)*16+8,W) emu.write16(P+0x14,(y//64)*16+8,W)
  print(string.format('CELL %04x', c))
end)
wait(40)
at(function() if spawned then print('AFTER lives='..emu.read(P+0x3D,W)..' score='..score()..string.format(' cell=%04x flags39=%02x', emu.read16(0x0916+spawned.cell,W), emu.read(P+0x39,W))) end end)
S('item_'..PW)
