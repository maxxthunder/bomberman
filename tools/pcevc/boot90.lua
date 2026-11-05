-- Bomberman (1990): what the reset code reads from the I/O port ($1000, A at $E009) and where the CPU is after 10 s.
-- run.sh pce90 <rom> boot90.lua. For a Japanese PC Engine, use a second portable Mesen whose settings.json has
-- PcEngine.ConsoleType = "PcEngine" (default "Auto" = TurboGrafx-16 for this card).
local done=false
emu.addMemoryCallback(function() if not done then done=true
  local s=emu.getState() print(string.format('reset check: A after LDA $1000 = %02x', s['cpu.a'])) end end, emu.callbackType.exec, 0xE009, 0xE009)
wait(600) at(function() local s=emu.getState() print(string.format('frame 600: PC=%04x MPR2=%02x', s['cpu.pc'], s['memoryManager.mpr[2]'])) shot('boot') end)
