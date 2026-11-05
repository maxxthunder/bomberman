-- From the battle state: idle 70 s (HUD clock and win counters should change if they were live), then all 8
-- players bomb themselves and the game is left running 30 s to see whether a round ever ends.
savestate.load(STATES.."battle_tap.state") shot("t0")
wait(70*60) shot("t70")
local t={} for p=1,8 do t["P"..p.." A"]=true end joypad.set(t) wait(200) shot("dead")
wait(30*60) shot("dead30")
local alive=0 for n=0,7 do if memory.read_u32_be(0x1A4+42*n+8,DOMAIN)==0x152E then alive=alive+1 end end
log("alive "..alive.." frame "..emu.framecount())
