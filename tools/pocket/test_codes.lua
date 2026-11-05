-- Type CODE (prepend CODE = "..."; see test_codes.py) with real pad presses on the password screen, A, then read
-- what the check wrote when $01:6549 returns ($01:6539): $C1BD (1 = rejected), $C35A index, $C1DC world, $C1DD stage,
-- $C352-$C356, and take screenshots: 'pw' (the screen's answer), 'go' SHOTAT frames later.
local r = 'none'
at(function() on_exec(1, 0x6539, function() r = string.format('rej=%d idx=%d world=%d stage=%d mode=%d p=%d,%d,%d,%d', rd(0xC1BD), rd(0xC35A),
  rd(0xC1DC), rd(0xC1DD), rd(0xC352), rd(0xC353), rd(0xC354), rd(0xC355), rd(0xC356)) end) end)
to_password()
type_pw(CODE)
wait(40) at(function() shot('pw') end)
wait(SHOTAT or 900)
at(function() shot('go') print('CODE '..CODE..' '..r) end)
