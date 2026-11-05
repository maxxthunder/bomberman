-- Decoder fuzz (prepend CODES = "<8 nibbles per code, hex>"; see fuzz.mjs). A code is typed once; when the decoder
-- starts ($05:9623, after the submit flag) a savestate is taken, then for each code the 8 nibbles are written to
-- $03E4-$03EB, the state reloaded and the result read at the exits: $05:963D accepted (area-1, stage-1, bombs-1,
-- fire-1, bomb timer $03ED, detonator $03EE and the three secret flags), $05:9650 rejected (X).
local A = REG=='jp' and {0x3D,0x3E,0x82,0x85,0x3ED,0x3EE,0x54C,0x54D,0x54E} or {0x4B,0x4C,0x90,0x93,0x3ED,0x3EE,0x54E,0x54F,0x550}
local st, i, n, out, base = nil, 0, #CODES // 8, {}, nil
local function nextcode()
  if i >= n then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  for _, a in ipairs(A) do emu.write(a, base[_], R) end
  for k = 0, 7 do emu.write(0x3E4 + k, tonumber(CODES:sub(i * 8 + k + 1, i * 8 + k + 1), 16), R) end
end
local function rec(v) out[#out + 1] = v i = i + 1 nextcode() end
emu.addMemoryCallback(function() if not st then base = {} for _, a in ipairs(A) do base[_] = 0 end st = emu.createSavestate() nextcode() end end, emu.callbackType.exec, 0x9623, 0x9623)
emu.addMemoryCallback(function() local t = {} for _, a in ipairs(A) do t[#t + 1] = string.format('%x', rd(a)) end rec(table.concat(t, ',')) end, emu.callbackType.exec, 0x963D, 0x963D)
emu.addMemoryCallback(function() rec('X') end, emu.callbackType.exec, 0x9650, 0x9650)
to_password()
type_pw(ALPHA:sub(1,1):rep(8))
for f = 1, 600 do q[#q + 1] = {} end
