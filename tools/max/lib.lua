-- max helpers, prepended to test scripts by run.sh (after tools/emu/mesen_gb.py's prelude)
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- exec callback on a banked address: fn() runs when pc = addr and the ROM bank is bk (addr < $4000: any bank)
function on_exec(bk, addr, fn) emu.addMemoryCallback(function() if addr<0x4000 or bank()==bk then fn() end end,
  emu.callbackType.exec, addr, addr, emu.cpuType.gameboy, BUS) end
SR=emu.memType.gbCartRam
-- cart RAM dump (8 KB, $A000-$BFFF bank 0), printed as DUMP <name>.ram via mesen_gb.py
function sdump(name) local t={} for a=0,0x1FFF do t[#t+1]=string.format('%02x',emu.read(a,SR)) end print('DUMP '..name..' '..table.concat(t)) end
-- random-input bot: one direction held for 6 frames, A (bomb) a third of the time, B a fifth
local dirs={'up','down','left','right'}
function bot(frames, seed) math.randomseed(seed or 1)
  for k=1,frames//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end
    if math.random(5)==1 then b.b=true end hold(b,6) end end
-- boot -> title menu (US: NormalGame / BattleGame / Pitch Area; JP the same in kana)
-- Start presses through the logos and intro; the timing that lands on the menu differs per version (found by shots)
local TT = {blue={300,4,80,60}, red={300,4,80,60}, hikari={200,4,61,60}, yami={200,4,61,60}, ain={200,4,61,420}}
function to_title() local t = TT[VER] wait(t[1]) for k=1,t[2] do press({start=true}) wait(t[3]) end wait(t[4]) end
-- title -> NormalGame -> Start (a new game; JP: the first line) -> area 1-01 intro
function start_new() to_title() press({a=true}) wait(60) press({a=true}) wait(400) press({a=true}) wait(300) end
