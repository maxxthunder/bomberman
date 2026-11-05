-- Decoder fuzz (prepend CODES = "<7-digit codes concatenated>"; see fuzz.py). On the password screen A is pressed
-- once; at the check's entry ($0D:68EC) a savestate is taken, then each code is written to $D200-$D206, the state
-- reloaded and the result read at the exits: $0D:6871 accepted ($C1B8, $C362, $C365, $C38E, $C383-$C389, $C38D,
-- $C38C), $0D:689C rejected.
local st, i, n, out = nil, 0, #CODES // 7, {}
local function nextcode()
  if i >= n then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  for k = 0, 6 do emu.write(0xD200 + k, tonumber(CODES:sub(i * 7 + k + 1, i * 7 + k + 1), 16), BUS) end
end
local function rec(v) out[#out + 1] = v i = i + 1 nextcode() end
to_password()
at(function()
  on_exec(0x0D, 0x68EC, function() if not st then st = emu.createSavestate() nextcode() end end)
  on_exec(0x0D, 0x6871, function()
    if rd(0xC1B8) == 1 then rec('boss') return end
    local t = {} for a = 0xC383, 0xC389 do t[#t + 1] = rd(a) end
    rec(string.format('%d,%d,%d,%s,%d,%d', rd(0xC362), rd(0xC365) + 1, rd(0xC38E), table.concat(t), rd(0xC38D), rd(0xC38C))) end)
  on_exec(0x0D, 0x689C, function() rec('X') end)
end)
press({a=true})
for f = 1, 600 do q[#q + 1] = {} end
