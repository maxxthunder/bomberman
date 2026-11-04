-- Title-screen turbo-X trick: tap X every PERIOD frames (held half of it, like a turbo pad) and report
-- when $7F202D (battle stage count) becomes 12. Run: job.sh <dir> "PERIOD=8" "$(cat joycard.lua)"
PERIOD = PERIOD or 8
emu.addMemoryCallback(function(a, v) if v == 12 then print('stage count 12 after', emu.getState().frameCount - T0, 'frames') end end,
  emu.callbackType.write, 0x7F202D, 0x7F202D)
to_title() at(function() T0 = emu.getState().frameCount end)
for i = 1, 120 do
  for k = 1, PERIOD // 2 do q[#q + 1] = {x = true} end
  for k = 1, PERIOD - PERIOD // 2 do q[#q + 1] = {} end
end
at(function() print('period', PERIOD, 'stage count', rd(0x1202D)) end)
