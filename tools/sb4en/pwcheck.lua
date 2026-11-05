-- Type each password with real button presses from one savestate of the PASSWORD screen, press START,
-- and report what the game did. Codes come from the global CODES (set before this file).
-- The savestate is made/loaded from an exec callback on the NMI handler ($00:F001), the only place Mesen allows it.
local S, want = nil, nil
emu.addMemoryCallback(function()
  if want == 'save' then S = emu.createSavestate() elseif want == 'load' then emu.loadSavestate(S) end
  want = nil end, emu.callbackType.exec, 0x00F001, 0x00F001)
local function report(c)
  local w = function(a) return emu.read16(a, W) end
  print(string.format('PW %s stage92=%d powerset70B5=%d nofatigue70B7=%d items70BD=%d battleset24A=%d gold1F48=%d mode1A4=%04X pad2_1EF2=%d',
    c, w(0x92), rd(0x170B5), rd(0x170B7), rd(0x170BD), rd(0x24A), rd(0x1F48), w(0x1A4), rd(0x1EF2)))
  local t = {} for a = 0x340, 0x34F do t[#t + 1] = string.format('%02x', rd(a)) end
  print('   P1 $0340-$034F', table.concat(t, ' '), '$03D8', rd(0x3D8))
  shot('pw' .. c)
end
to_pw()
at(function() want = 'save' end) wait(2)
for _, c in ipairs(CODES) do
  at(function() want = 'load' end) wait(2)
  typepw(c) press({start = true}) wait(WAIT or 700)
  at(function() report(c) end)
end
