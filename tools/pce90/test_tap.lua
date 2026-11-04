-- TurboTap check ($E371, $08:601E): needs a Mesen copy whose settings put a PceTurboTap in port 1 with
-- PceController in Port1A-E (run with MESEN pointing at it). Cursor to 2-5P BATTLE with pad 1, then Run on
-- the pads listed in PADS (subports 0-4) on the same frame. ALL5=1 presses Run on all five at once.
local f = 0
emu.addEventCallback(function() f = f + 1 end, emu.eventType.endFrame)
emu.addEventCallback(function()
  if f > 640 and f < 646 then for _, p in ipairs(PADS) do emu.setInput({run = true}, 0, 0, p)  -- this Mesen build: (input, port, 0, subport) end end
  if f > 600 and f < 606 then emu.setInput({down = true}, 0, 0) end
end, emu.eventType.inputPolled)
for k = 1, 900 do q[#q + 1] = {} end
at(function() print('tap flag $33 =', emu.read(0x33, W), 'mode', emu.read(0x13B6, W)) end)
S(SHOT)
