-- Decoder fuzz: every code 0000-9999 through the game's own check. On the password screen A is pressed once; at the
-- check's entry (A0) a savestate is taken, then each code is written to $C1BE-$C1C1, the state reloaded and the
-- result read at the check's exits: MATCH (HL -> 4th digit of the record, value at HL+1) or FAIL.
local A = ({us={0x35CC,0x361B,0x3602}, jp={0x35F9,0x3648,0x362F}})[VER]
local st, i, out = nil, 0, {}
local function nextcode()
  if i > 9999 then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  local s = string.format('%04d', i)
  for k = 0, 3 do emu.write(0xC1BE + k, s:byte(k + 1) - 48, BUS) end
end
local function rec(v) out[#out + 1] = v i = i + 1 nextcode() end
to_password()
at(function()
  on_exec(0, A[1], function() if not st then st = emu.createSavestate() nextcode() end end)
  on_exec(0, A[2], function() local s = emu.getState() rec(string.format('%x', emu.read(((s['cpu.h'] << 8) | s['cpu.l']) + 1, BUS))) end)
  on_exec(0, A[3], function() rec('X') end)
end)
press({a=true})
for f = 1, 600 do q[#q + 1] = {} end
