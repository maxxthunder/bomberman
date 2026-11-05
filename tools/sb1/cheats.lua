-- Pro Action Replay checks on the unpatched ROM, through Mesen's own cheat engine (emu.addCheat), no RAM writes.
-- TEST=name picks the codes (CODES below); every test powers on, starts a Normal Game with Start on the title
-- (or types PW on the password screen), lays a bomb next to player 1 and reads player 1 back.
-- tools/sb1/run.sh tools/sb1/cheats.lua us  (put TEST='inv' etc. in front, see tools/sb1/cheats.sh)
local CODES={
  none={}, inv={'7E0D7660','7E0D7701'}, lives={'7E0D7D09'}, fire={'7E0D7180'},
  kit={'7E0D7009','7E0D7963','7E0D7301'}, small={'7E0C9001'}, nine={'7E0C8F01'},
  snd={'7E00A43C'}, stage={'7E00A42F'}, map1={'C30D63DA','C30D64A1'}, map2={'C30D63A2','C30D64AE'},
}
at(function() for _,c in ipairs(CODES[TEST]) do local ok,e=pcall(emu.addCheat,emu.cheatType.snesProActionReplay,c) print('cheat',c,ok,e) end end)
local P=0x0D40
local function st(tag) at(function() print(string.format('%s scene=%02x lives=%d bombs=%02x fire=%02x spd=%02x flags39=%02x remote=%02x inv=%04x state=%04x small=%d out=%d',
  tag,emu.read(0xD10,W),emu.read(P+0x3D,W),emu.read(P+0x30,W),emu.read(P+0x31,W),emu.read(P+0x32,W),emu.read(P+0x39,W),emu.read(P+0x33,W),emu.read16(P+0x36,W),emu.read16(P,W),emu.read(0x0C90,W),emu.read(P+0x24,W))) end) end
if TEST=='snd' or TEST=='stage' then wait(1200) st('T') S('cheat_'..TEST) return end
wait(700) press({start=true},4) wait(900)
st('start') S('cheat_'..TEST..'_start')
wait(600)  -- the start-of-stage invincibility (+$36 = $020C) runs out first
if TEST=='inv' or TEST=='lives' or TEST=='none' then press({a=true},4)  -- stand on the bomb
else for i=1,4 do press({a=true},4) press({right=true},10) end end
st('bombs') wait(30) S('cheat_'..TEST..'_blast')
wait(400) st('after')
wait(400) st('end') S('cheat_'..TEST..'_end')
