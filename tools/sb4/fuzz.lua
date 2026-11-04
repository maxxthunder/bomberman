-- Exhaustive check of the password decoder: every code 0000-9999 is written into the entry digits
-- ($7F:70A9-70AC, stored as (10 - digit) % 10) and confirmed with START from one savestate.
-- The game's own compare loop decides: exec at $C2A9C9 = table hit ($92 = index), $C2A926 = miss.
-- Prints "HIT <code> <index>" for each hit and a total. Run: job.sh <dir> "$(cat fuzz.lua)"
local n, S, hits, cur = 0, nil, 0, nil
local function put(c) for i = 0, 3 do wr(0x170A9 + i, (10 - (c // 10 ^ (3 - i) % 10)) % 10) end end
local function nextcode()
  cur = n; n = n + 1
  if cur > 9999 then print('TOTAL', hits, 'of', cur) emu.stop(0) return end
  emu.loadSavestate(S); put(cur)
end
emu.addMemoryCallback(function() hits = hits + 1 print('HIT', string.format('%04d', cur), emu.read16(0x92, W)) nextcode() end,
  emu.callbackType.exec, 0xC2A9C9, 0xC2A9C9)
emu.addMemoryCallback(function() nextcode() end, emu.callbackType.exec, 0xC2A926, 0xC2A926)
emu.addMemoryCallback(function() if not S and go then S = emu.createSavestate() nextcode() end end,
  emu.callbackType.exec, 0xC2A8C3, 0xC2A8C3)
to_pw()
at(function() go = true end) wait(2)
for i = 1, 200000 do q[#q + 1] = {start = true} end
