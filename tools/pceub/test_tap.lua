-- TurboTap check ($01:A4DD JSR $00:E30A when Run is pressed on PUSH RUN BUTTON; $08:6014 shows the error screen if $32 = 0).
-- Needs a Mesen copy whose settings put a PceTurboTap in port 1 with PceController in Port1A-E. Run is pressed on the
-- pads listed in PADS (subports 0-4) on the same frame; then Run on pad 1 through the menus. Prints $32, screenshot SHOT.
local f = 0
emu.addEventCallback(function() f = f + 1 end, emu.eventType.endFrame)
emu.addEventCallback(function()
  if f > 300 and f < 305 then for _, p in ipairs(PADS) do emu.setInput({run = true}, 0, 0, p) end end
end, emu.eventType.inputPolled)
for k = 1, 420 do q[#q + 1] = {} end
at(function() print('tap flag $32 =', emu.read(0x32, W)) end)
for k = 1, 3 do wait(90) press({run = true}) end
wait(120) S(SHOT)
