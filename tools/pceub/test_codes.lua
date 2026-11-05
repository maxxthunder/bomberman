-- Type CODE (prepend CODE = "..."; see test_codes.py) with real pad presses on the password screen, END with I,
-- then read $2849-$284D (round-1, stage-1, bombs, fire, speed), $341B (sound-test flag) and $342F (1 valid,
-- 2 invalid) and take a screenshot SHOTAT frames later. "BOMSOUND+CODE" types BOMSOUND, END, then CODE.
to_password()
for c in CODE:gmatch('[^+]+') do type_pw(c) wait(30) end
at(function()
  local t = {} for a = 0x849, 0x84D do t[#t + 1] = emu.read(a, W) end
  print(string.format('CODE %s valid=%d snd=%02x ram=%s', CODE, emu.read(0x142F, W), emu.read(0x141B, W), table.concat(t, ',')))
end)
wait(SHOTAT or 250)
S('shot')
