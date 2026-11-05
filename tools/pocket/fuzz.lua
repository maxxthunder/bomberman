-- Decoder fuzz: every 4-digit code 0000-9999 through the game's own check. On the password screen A is pressed once;
-- at the check's entry ($01:6565, from $01:6536) a savestate is taken, then each code is written to $C1C4-$C1C7, the
-- state reloaded and the result read when $01:6549 returns ($01:6539): $C1BD (1 = rejected), $C35A (table index),
-- $C1DC world, $C1DD stage, $C352-$C356.
local st, i, out = nil, 0, {}
local function nextcode()
  if i > 9999 then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  local c = string.format('%04d', i)
  for k = 0, 3 do emu.write(0xC1C4 + k, tonumber(c:sub(k + 1, k + 1)), BUS) end
end
to_password()
at(function()
  on_exec(1, 0x6565, function() if not st then st = emu.createSavestate() nextcode() end end)
  on_exec(1, 0x6539, function()
    if not st then return end
    out[#out + 1] = rd(0xC1BD) == 1 and 'X' or string.format('%d,%d,%d,%d,%d,%d,%d,%d', rd(0xC35A), rd(0xC1DC), rd(0xC1DD),
      rd(0xC352), rd(0xC353), rd(0xC354), rd(0xC355), rd(0xC356))
    i = i + 1 nextcode() end)
end)
press({a=true})
for f = 1, 600 do q[#q + 1] = {} end
