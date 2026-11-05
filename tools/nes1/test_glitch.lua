-- Out-of-range passwords (prepend CODES = {...}, NAMES = {...}): each typed from a saved ENTER SECRET CODE screen,
-- then 400 frames of play; prints how often the soft-block placer $CACF ran (a hang shows as a huge count and no
-- stage), the stage, fire, bombs and the walk-through-wall result, and takes <name>.png.
local st, n = nil, 0
emu.addMemoryCallback(function() n = n + 1 end, emu.callbackType.exec, PLACER or 0xCACF, PLACER or 0xCACF)
to_password()
at(function() in_cpu(function() st = emu.createSavestate() end) end) wait(2)
for k, c in ipairs(CODES) do
  at(function() in_cpu(function() emu.loadSavestate(st) n = 0 end) end) wait(2)
  type_pw(c) wait(400) S(NAMES[k])
  at(function() print(string.format('%s %s placer=%d stage=%d fire=%d bombs=%d wall=%d reveal=%d', NAMES[k], c, n, rd(0x58), rd(0x73) >> 4, rd(0x74) + 1, rd(0x76), rd(0x94))) end)
end
