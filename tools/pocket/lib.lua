-- pocket helpers, prepended to test scripts by run.sh (after tools/emu/mesen_gb.py's prelude)
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- exec callback on a banked address: fn() runs when pc = addr and the ROM bank is bk (addr < $4000: any bank)
function on_exec(bk, addr, fn) emu.addMemoryCallback(function() if addr<0x4000 or bank()==bk then fn() end end,
  emu.callbackType.exec, addr, addr, emu.cpuType.gameboy, BUS) end
-- random-input bot: one direction held for 6 frames, A (jump) a third of the time, B (bomb) a quarter
local dirs={'up','down','left','right'}
function bot(frames, seed) math.randomseed(seed or 1)
  for k=1,frames//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end
    if math.random(4)==1 then b.b=true end hold(b,6) end end
-- Hudson logo + intro -> title (Start) -> Normal Game (A) -> Password (Down, A): 4 digits, cursor on the first
function to_password() wait(1200) press({start=true}) wait(150) press({a=true}) wait(60) press({a=true}) wait(60)
  press({down=true}) wait(30) press({a=true}) wait(120) end
-- type a 4-digit code: Up/Down step the digit under the cursor ($C1C4 + $C1B9, 0-9 wrapping, $01:6734),
-- Right moves the cursor; A checks ($01:6525 -> $01:6565). Down from 0 reaches 6-9 faster.
function type_pw(code)
  for k=1,4 do local d=tonumber(code:sub(k,k))
    if d<=5 then for i=1,d do press({up=true},2) end else for i=1,10-d do press({down=true},2) end end
    if k<4 then press({right=true}) end end
  press({a=true})
end
-- password -> world select -> stage intro -> play (presses Start/A through the screens)
function start_game(code) to_password() type_pw(code) wait(600) press({start=true}) wait(150) press({a=true}) wait(300) end
