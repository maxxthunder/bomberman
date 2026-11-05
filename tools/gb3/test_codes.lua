-- Type CODE (prepend CODE = "..."; see test_codes.py) with real pad presses on the password screen, A, then read
-- what the check wrote ($C1B8 boss attack, $C362 area, $C365 stage-1, $C38E, $C383-$C389, $C38D, $C38C), whether the
-- reject exit ran (rej), and take a screenshot SHOTAT frames later.
local rej = 0
at(function() on_exec(0x0D, 0x689C, function() rej = 1 end) end)
to_password()
type_pw(CODE)
wait(SHOTAT or 300)
at(function() shot('shot') local t = {} for a = 0xC383, 0xC389 do t[#t + 1] = rd(a) end
  print(string.format('CODE %s rej=%d boss=%d area=%d stage=%d extra=%d cleared=%s shop=%d check=%d', CODE, rej, rd(0xC1B8),
    rd(0xC362), rd(0xC365) + 1, rd(0xC38E), table.concat(t), rd(0xC38D), rd(0xC38C))) end)
