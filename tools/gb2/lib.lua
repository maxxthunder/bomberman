-- gb2 helpers, prepended to test scripts by run.sh (after tools/emu/mesen_gb.py's prelude)
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- random-input bot: one direction held for 6 frames, A (bomb) a third of the time
local dirs={'up','down','left','right'}
function bot(frames, seed) math.randomseed(seed or 1)
  for k=1,frames//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end hold(b,6) end end
-- exec callback on a banked address: fn() runs when pc = addr and the ROM bank is bk (addr < $4000: any bank)
function on_exec(bk, addr, fn) emu.addMemoryCallback(function() if addr<0x4000 or bank()==bk then fn() end end,
  emu.callbackType.exec, addr, addr, emu.cpuType.gameboy, BUS) end
-- intro -> title (Start) -> PASSWORD (3rd line) -> 4 digits, cursor on the first
function to_password() wait(300) press({start=true}) wait(120) press({down=true}) press({down=true}) press({a=true}) wait(120) end
-- type a 4-digit code: Up/Down step the digit under the cursor ($C1BE + $C1BC, wraps 0-9, $00:0339), Right moves
-- the cursor ($00:0309, no wrap), A or Start checks ($00:3583 -> $00:35CC US / $00:35F9 JP)
function type_pw(code)
  for k=1,4 do local d=code:byte(k)-48
    if d<=5 then for i=1,d do press({up=true},2) end else for i=1,10-d do press({down=true},2) end end
    if k<4 then press({right=true}) end end
  press({a=true})
end
-- password -> world map (A) -> mode door (MODE-A left, MODE-B right; Up enters) -> rules text (A) -> AREA screen
-- (A) -> play.
function start_game(code, mode)
  to_password() type_pw(code) wait(450) press({a=true}) wait(150)
  hold(mode == 'B' and {right=true} or {left=true}, 60) press({up=true}) wait(60) press({a=true}) wait(300) press({a=true}) wait(300) press({a=true}) wait(200)
end
