-- Decoder fuzz (prepend CODES = "<20-letter codes as nibble hex, 20 chars each>", A0/OK/BAD = decoder entry,
-- accept exit and reject exit for the version; see fuzz.mjs). 20 letters are typed once; at the decoder entry a
-- savestate is taken, then for each code the 20 letter nibbles are written to $7F-$92, the state reloaded and the
-- result read at the decoder's exits: OK (its RTS) -> the RAM it set, BAD (JMP back to the entry screen) -> X.
local RAMS = {0x58,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x73,0x74,0x75,0x76,0x77,0x79,0x94}
local st, i, n, out = nil, 0, #CODES // 20, {}
local function nextcode()
  if i >= n then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  for k = 0, 19 do emu.write(0x7F + k, tonumber(CODES:sub(i * 20 + k + 1, i * 20 + k + 1), 16), R) end
end
local function rec(v) out[#out + 1] = v i = i + 1 nextcode() end
emu.addMemoryCallback(function() if not st then st = emu.createSavestate() nextcode() end end, emu.callbackType.exec, A0, A0)
emu.addMemoryCallback(function() local t = {} for _, a in ipairs(RAMS) do t[#t + 1] = string.format('%x', rd(a)) end rec(table.concat(t, ',')) end, emu.callbackType.exec, OK, OK)
emu.addMemoryCallback(function() rec('X') end, emu.callbackType.exec, BAD, BAD)
to_password()
type_pw('AAAAAAAAAAAAAAAAAAAA')
for f = 1, 600 do q[#q + 1] = {} end
