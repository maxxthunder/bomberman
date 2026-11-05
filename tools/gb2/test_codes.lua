-- Type CODE (prepend CODE = "..."; see test_codes.py) with real pad presses on the password screen, A, then read
-- $C1BD (the table value the check found), whether the check's reject exit ran (rej), $C100 (world << 4 | stage),
-- $C11A (battle), $C125/$C126 (power-up code) and take a screenshot SHOTAT frames later.
local A = ({us=0x3602, jp=0x362F})[VER]
local rej = 0
at(function() on_exec(0, A, function() rej = 1 end) end)
to_password()
type_pw(CODE)
wait(SHOTAT or 300)
at(function() shot('shot') print(string.format('CODE %s C1BD=%02X rej=%d C100=%02X C11A=%02X C125=%02X C126=%02X', CODE, rd(0xC1BD), rej, rd(0xC100), rd(0xC11A), rd(0xC125), rd(0xC126))) end)
