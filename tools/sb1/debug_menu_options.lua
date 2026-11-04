-- Debug-menu write-back: each option set from the menu, then the player struct (/usr/bin/bashD40) read after closing.
OPTS={{0,0,nil,10},{1,1},{3,9},{4,9},{5,7},{6,1},{7,1},{8,1},{9,1},{10,1},{11,1},{12,1},{13,1},{14,1},{3,12}}
local st, want = nil, false
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(700)
at(function() emu.addMemoryCallback(function()
  if not st then st=emu.createSavestate() end
  if want then emu.loadSavestate(st) want=false end
end, emu.callbackType.exec, 0xC60000, 0xC60000) end)
wait(2)
local P=0x0D40
local function pl(tag) at(function()
  local t={} for _,o in ipairs({0x2E,0x30,0x31,0x32,0x33,0x36,0x37,0x38,0x39,0x3C,0x3D}) do t[#t+1]=string.format('+%02X=%02x',o,emu.read(P+o,W)) end
  print(tag, table.concat(t,' '), string.format('13A=%04x 13C=%04x A4=%02x scene0D10=%02x 0D16=%02x', emu.read16(P+0x13A,W), emu.read16(P+0x13C,W), emu.read(0xA4,W), emu.read(0xD10,W), emu.read(0xD16,W))) end) end
function menu(i, n, btn)
  at(function() want=true end) wait(2)
  press({select=true},2) wait(4)
  for k=1,i do press({down=true},2) end
  for k=1,n do press({[btn or 'right']=true},2) end
  wait(4)
end
function close() press({select=true},2) wait(4) end
for _,c in ipairs(OPTS) do
  menu(c[1], c[2], c[3]) if c[5] then S(c[5]..'_open') end close() wait(c[4] or 10) pl(string.format('opt %d x%d', c[1], c[2])) if c[5] then S(c[5]) end
end
