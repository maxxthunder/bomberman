-- quest helpers, prepended to test scripts by run.sh (after tools/emu/mesen_gb.py's prelude; VER = "us" or "jp")
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- exec callback on a banked address: fn() runs when pc = addr and the ROM bank is bk (addr < $4000: any bank)
function on_exec(bk, addr, fn) emu.addMemoryCallback(function() if addr<0x4000 or bank()==bk then fn() end end,
  emu.callbackType.exec, addr, addr, emu.cpuType.gameboy, BUS) end
SR=emu.memType.gbCartRam
-- the save's game block in WRAM: US $CE81, Japan $CE80 (the Japanese copy loop starts one byte lower, $00:0B3A)
BLOCK = VER == 'jp' and 0xCE80 or 0xCE81
-- 16 KB VRAM (both CGB banks) then SCY, SCX, as DUMP <name>.ram
function vram16(name) local t={} for a=0,0x3FFF do t[#t+1]=string.format('%02x',emu.read(a,VR)) end
  t[#t+1]=string.format('%02x',rd(0xFF42)) t[#t+1]=string.format('%02x',rd(0xFF43)) print('DUMP '..name..' '..table.concat(t)) end
function sdump(name) local t={} for a=0,0x1FFF do t[#t+1]=string.format('%02x',emu.read(a,SR)) end print('DUMP '..name..' '..table.concat(t)) end
-- Hudson logo, title, Start -> menu (New Game / Battle; Continue with a save). debug: $C234 bit 0 forced on (the flag
-- the boot screen sets for one frame, $00:194A) and New Game chosen with Down + Select + A, the debug start ($08:42BB).
-- (KEEP0 = true: not forced, for the Game Genie code / patch that keeps the flag.)
-- Then the intro text is pressed through and the shuttle scene skipped with Start: control in front of the shuttle.
function new_game(debug)
  wait(1500) press({start=true}) wait(120)
  if debug then if not KEEP0 then at(function() wr(0xC234, rd(0xC234) | 1) end) end
    hold({down=true},20) hold({down=true,up=true},20) hold({down=true},30) hold({down=true,select=true,a=true},12) hold({},30)
  else press({a=true}) end
  wait(200) for k=1,60 do press({a=true}) wait(20) end wait(300)
  press({start=true},8) wait(200)
end
-- from the shuttle: down to the path, west along it out of Peace Town (A closes the signpost text), then two screens
-- further west to the first screen with a monster
function to_field() hold({down=true},40) for k=1,4 do hold({left=true},120) end
  for k=1,6 do press({b=true},8) wait(20) end
  for k=1,4 do for j=1,3 do hold({left=true},50) press({a=true},6) press({a=true},6) end end end
-- the A weapon: Normal Bomb (id 8); a new game has none on A or B until the menu assigns one
function arm() wr(BLOCK+4, 8) wr(0xC394, 8) end
-- random-input bot: a direction for 10 frames, A (the A weapon) a third of the time, B a quarter
local dirs={'up','down','left','right'}
function bot(frames, seed) math.randomseed(seed or 1)
  for k=1,frames//10 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end
    if math.random(4)==1 then b.b=true end hold(b,10) end end
-- menu page (0 weapons, 1 equipment, 2 items): Start, A on the bag, Right x page, A (weapons: A again picks the slot)
function open_page(p) press({start=true},8) wait(60) press({a=true},8) wait(40)
  for i=1,p do press({right=true},8) wait(20) end press({a=true},8) wait(60) if p==0 then press({a=true},8) wait(40) end end
function close_page() for k=1,5 do press({b=true},8) wait(30) end end
