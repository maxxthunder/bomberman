-- CODE=... tools/emu/run.sh bb tools/bb/test_codes.lua us|jp: one code per run; prints what it loads.
-- 8 characters: Game A ($C0E9 islands, $C0E0/$C0E1 gold); 20: Game B ($C40B stage, $C402 bombs, $C403 fire,
-- $C404 speed, $C406-$C408 wall pass, flame pass, detonator).
if #CODE==8 then pwscreen() pokepw(CODE) press({a=true}) wait(200)
  at(function() print(string.format('%s islands=%02X gold=%d', CODE, rd(0xC0E9), rd(0xC0E0)+256*rd(0xC0E1))) end)
else bmcode() typecode(CODE) wait(200)
  at(function() print(string.format('%s stage=%d bombs=%d fire=%d speed=%d wall=%d flame=%d det=%d', CODE, rd(0xC40B), rd(0xC402), rd(0xC403), rd(0xC404), rd(0xC406), rd(0xC407), rd(0xC408))) end) end
