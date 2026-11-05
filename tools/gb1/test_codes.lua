-- Type CODE (prepend CODE = "..."; see test_codes.py) with real pad presses on the title's password line, Start,
-- then read $C3F0 (stage), $C3FB (power-up code), $C3D5 (Wario: 1 Bomberman, 0 Wario), whether the check's reject
-- exit ran (rej) and whether the extra-battle entry ran (bat), and take a screenshot SHOTAT frames later.
local A = ({jp={0x42B3,0x34B2}, wario={0x4296,0x3457}})[VER]
local rej, bat = 0, 0
at(function() on_exec(0x0A, A[1], function() rej = 1 end) on_exec(0, A[2], function() bat = 1 end) end)
to_password()
type_pw(CODE)
wait(SHOTAT or 200)
at(function() shot('shot') print(string.format('CODE %s C3F0=%02X C3FB=%02X C3D5=%02X rej=%d bat=%d', CODE, rd(0xC3F0), rd(0xC3FB), rd(0xC3D5), rej, bat)) end)
