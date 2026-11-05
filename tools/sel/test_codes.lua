-- tools/emu/run.sh sel tools/sel/test_codes.lua: one code per run (CODE=...); prints what it loads.
-- 8 characters: Bomber Boy ($C0E9 islands, $C0E0/$C0E1 gold); 20 letters: Bomber Man mode ($C40B stage, $C402 bombs,
-- $C403 fire, $C404 speed, $C406-$C408 wall pass, flame pass, detonator); 4 digits: Bomberman (screenshot only).
if #CODE==8 then pwscreen() pokepw(CODE) press({a=true}) wait(200)
  at(function() print(string.format('%s islands=%02X gold=%d', CODE, rd(0xC0E9), rd(0xC0E0)+256*rd(0xC0E1))) end)
elseif #CODE==20 then bmcode() typecode(CODE) wait(200)
  at(function() print(string.format('%s stage=%d bombs=%d fire=%d speed=%d wall=%d flame=%d det=%d', CODE, rd(0xC40B), rd(0xC402), rd(0xC403), rd(0xC404), rd(0xC406), rd(0xC407), rd(0xC408))) end)
else gbtitle() type_pw(CODE) wait(200) at(function() shot(CODE) end) end
