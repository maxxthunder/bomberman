-- Decoder fuzz (prepend CODES = "<8-letter codes concatenated>"; see fuzz.py). From the password screen, END is
-- selected once; at the decoder entry ($CBAE) a savestate is taken, then each code is written to $3446-$344D,
-- the state reloaded and the result read at the decoder's exits: $CCD0 valid ($345A-$345E), $CCD6 invalid.
local A0, OK, BAD = 0xCBAE, 0xCCD0, 0xCCD6
local st, i, n, out = nil, 0, #CODES // 8, {}
local function nextcode()
  if i >= n then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  for k = 0, 7 do emu.write(0x1446 + k, CODES:byte(i * 8 + k + 1), W) end
end
local function rec(v) out[#out + 1] = v i = i + 1 nextcode() end
to_password()
at(function() emu.write(0x1444, 8, W) emu.write(0x1445, 2, W) end) -- cursor on END
at(function()
  emu.addMemoryCallback(function() if not st then st = emu.createSavestate() nextcode() end end, emu.callbackType.exec, A0, A0)
  emu.addMemoryCallback(function() local t = {} for k = 0, 4 do t[#t + 1] = string.format('%x', emu.read(0x145A + k, W)) end rec(table.concat(t, ',')) end, emu.callbackType.exec, OK, OK)
  emu.addMemoryCallback(function() rec('X') end, emu.callbackType.exec, BAD, BAD)
end)
press({i = true})
for f = 1, 600 do q[#q + 1] = {} end
