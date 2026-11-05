-- Type each code of CODES (prepend CODES = {...}, REJ = the decoder's reject exit; see test_codes.mjs) with real pad
-- presses on ENTER SECRET CODE. The screen is saved once and reloaded before each code. After END the script reads
-- $58 (stage), $61-$67 (score digits), $73 (fire << 4), $74 (bombs - 1), $75-$79 (speed, wall pass, detonator,
-- bomb pass, flame pass) and $94 (reveal); ok=0 means the reject exit ran. A screenshot <n>.png is taken SHOTAT
-- frames later.
local bad, st = 0, nil
emu.addMemoryCallback(function() bad=bad+1 end, emu.callbackType.exec, REJ, REJ)
to_password()
at(function() in_cpu(function() st = emu.createSavestate() end) end) wait(2)
for n, code in ipairs(CODES) do
  at(function() in_cpu(function() emu.loadSavestate(st) bad = 0 end) end) wait(2)
  type_pw(code)
  wait(30)
  at(function()
    local t = {} for _,a in ipairs({0x58,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x73,0x74,0x75,0x76,0x77,0x78,0x79,0x94}) do t[#t+1] = rd(a) end
    print(string.format('CODE %s ok=%d ram=%s', code, bad==0 and 1 or 0, table.concat(t, ',')))
  end)
  wait(SHOTAT or 200)
  S(code)
end
