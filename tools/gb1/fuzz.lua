-- Decoder fuzz: every code 0000-9999 through the game's own check. From the password screen Start is pressed once;
-- at the check's entry (A0) a savestate is taken, then each code is written to $C597-$C59A, the state reloaded and
-- the result read at the check's exits: MATCH (DE -> 4th digit of the record, value at DE+1) or FAIL.
local A = ({jp={0x4272,0x42BD,0x42B3}, wario={0x4255,0x42A0,0x4296}})[VER]
local st, i, out = nil, 0, {}
local function nextcode()
  if i > 9999 then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  local s = string.format('%04d', i)
  for k = 0, 3 do emu.write(0xC597 + k, s:byte(k + 1) - 48, BUS) end
end
local function rec(v) out[#out + 1] = v i = i + 1 nextcode() end
to_password()
at(function()
  on_exec(0x0A, A[1], function() if not st then st = emu.createSavestate() nextcode() end end)
  on_exec(0x0A, A[2], function() local s = emu.getState() rec(string.format('%x', rd(((s['cpu.d'] << 8) | s['cpu.e']) + 1))) end)
  on_exec(0x0A, A[3], function() rec('X') end)
end)
press({start=true})
for f = 1, 600 do q[#q + 1] = {} end
