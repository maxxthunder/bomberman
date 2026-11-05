-- gb1 helpers, prepended to test scripts by run.sh (after tools/emu/mesen_gb.py's prelude)
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- random-input bot: one direction held for 6 frames, A (bomb) a third of the time
local dirs={'up','down','left','right'}
function bot(frames, seed) math.randomseed(seed or 1)
  for k=1,frames//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end hold(b,6) end end
-- exec callback on a banked address: fn() runs when pc = addr and the ROM bank is bk (addr < $4000: any bank)
function on_exec(bk, addr, fn) emu.addMemoryCallback(function() if addr<0x4000 or bank()==bk then fn() end end,
  emu.callbackType.exec, addr, addr, emu.cpuType.gameboy, BUS) end
-- title -> password digits (PASSWORD is the 2nd title line; Start opens the first digit at 0)
function to_password() wait(400) press({down=true}) press({start=true}) wait(30) end
-- type a 4-digit code: Up/Down step the digit ($FFD1), A stores it and moves right ($0A:41BC), Start stores the
-- 4th and checks the code ($0A:420F -> $0A:4272)
function type_pw(code)
  for k=1,4 do local d=code:byte(k)-48
    if d<=5 then for i=1,d do press({up=true},2) end else for i=1,10-d do press({down=true},2) end end
    if k<4 then press({a=true}) end end
  press({start=true})
end
