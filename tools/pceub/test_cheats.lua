-- Users Battle cheat / patch check. Set MODE ('cheat', or 'ips' to run on a patched file) and TEST ('pw','snd','room'); run with tools/pceub/run.sh.
-- Users Battle cheats / patches. MODE = cheat | ips ; TEST = pw | snd | room
local function add(c) local ok,e=pcall(emu.addCheat,emu.cheatType.pceRaw,c) print('cheat',c,ok,e) end
if MODE=='cheat' then add('00240A:4C') add('00240B:A5') add('00240C:C3') end
if TEST=='snd' then add('1F141B:FF') end
if TEST=='room' and MODE=='cheat' then add('00200A:80') add('00200B:0B') end
local hit=0 emu.addMemoryCallback(function() hit=hit+1 end, emu.callbackType.exec, 0xA017, 0xA017, emu.cpuType.pce, emu.memType.pceMemory)
cur={0,0} wait(300) S('pw_'..MODE..'_'..TEST) type_pw('MUVWLNPC') wait(300) S('a_'..MODE..'_'..TEST)
if TEST=='room' then for k=1,12 do wait(200) press({run=true}) end wait(300) S('b_'..MODE..'_'..TEST) end
at(function() print(MODE, TEST, 'mode $3380', emu.read(0x1380,W), 'room entered', hit>0, 'snd $340A', emu.read(0x140A,W)) end)
