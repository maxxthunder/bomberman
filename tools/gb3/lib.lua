-- gb3 helpers, prepended to test scripts by run.sh (after tools/emu/mesen_gb.py's prelude)
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- random-input bot: one direction held for 6 frames, A (bomb) a third of the time
local dirs={'up','down','left','right'}
function bot(frames, seed) math.randomseed(seed or 1)
  for k=1,frames//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end hold(b,6) end end
-- exec callback on a banked address: fn() runs when pc = addr and the ROM bank is bk (addr < $4000: any bank)
function on_exec(bk, addr, fn) emu.addMemoryCallback(function() if addr<0x4000 or bank()==bk then fn() end end,
  emu.callbackType.exec, addr, addr, emu.cpuType.gameboy, BUS) end
-- intro -> title (Start) -> PASSWORD (2nd line) -> 7 hex digits, cursor on the first
function to_password() wait(200) press({start=true}) wait(200) press({down=true}) press({a=true}) wait(120) end
-- type a 7-digit hex code: Up/Down step the digit under the cursor ($D200 + $C621, wraps 0-F, $0D:6B78/$6B8B),
-- Left/Right move the cursor (wraps 0-6, $0D:6B43/$6B51), A checks ($0D:68EC). Down from 0 reaches 9-F faster.
function type_pw(code)
  for k=1,7 do local d=tonumber(code:sub(k,k),16)
    if d<=8 then for i=1,d do press({up=true},2) end else for i=1,16-d do press({down=true},2) end end
    if k<7 then press({right=true}) end end
  press({a=true})
end
-- password -> stage intro (A pages the text) -> play
function start_game(code) to_password() type_pw(code) wait(240) for k = 1, 4 do press({a=true}) wait(150) end wait(150) end
