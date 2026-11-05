-- Type each code of CODES (prepend CODES = {...}; see test_codes.mjs) with real pad presses on INPUT PASSWORD. The
-- screen is saved once and reloaded before each code. The 8th character submits; then the decoder's accept exit
-- ($05:963D, also taken by the secret codes) or reject exit ($05:9650) is noted and the RAM it sets is read:
-- area-1, stage-1, bombs-1, fire-1 (US $4B $4C $90 $93, JP $3D $3E $82 $85), bomb timer $03ED, detonator $03EE and
-- the secret flags (US $054E-$0550, JP $054C-$054E). Screenshot <code>.png SHOTAT frames later.
local res, st = '?', nil
local A = REG=='jp' and {0x3D,0x3E,0x82,0x85,0x3ED,0x3EE,0x54C,0x54D,0x54E} or {0x4B,0x4C,0x90,0x93,0x3ED,0x3EE,0x54E,0x54F,0x550}
emu.addMemoryCallback(function() res='ok' end, emu.callbackType.exec, 0x963D, 0x963D)
emu.addMemoryCallback(function() res='bad' end, emu.callbackType.exec, 0x9650, 0x9650)
to_password()
at(function() in_cpu(function() st = emu.createSavestate() end) end) wait(2)
for n, code in ipairs(CODES) do
  at(function() in_cpu(function() emu.loadSavestate(st) res = '?' end) end) wait(2)
  cur = {0, 0}  -- the typing plan is built now, at load time: every code starts from the saved cursor
  type_pw(code)
  wait(20)
  at(function()
    local t = {} for _,a in ipairs(A) do t[#t+1] = rd(a) end
    print(string.format('CODE %s %s ram=%s', code, res, table.concat(t, ',')))
  end)
  wait(SHOTAT or 200)
  S(code)
end
