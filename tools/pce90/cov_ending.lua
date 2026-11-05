-- ending: 8-8 by password, then the stage-clear test at $00:EC5F forced true (LDA $2437 -> LDA #$01 / NOP)
local P=emu.memType.pcePrgRom
emu.write(0x12AB3,0x60,P) emu.write(0x14485,0x60,P)
local seen={}
for _,a in ipairs({0xEB09,0xABCF,0x7C55}) do emu.addMemoryCallback(function() if not seen[a] then seen[a]=1 print(string.format('exec %04X',a)) end end, emu.callbackType.exec, a, a, emu.cpuType.pce, emu.memType.pceMemory) end
to_password() type_pw('MUOEPHLA') wait(700)
at(function() emu.write(0x0C5F,0xA9,P) emu.write(0x0C60,0x01,P) emu.write(0x0C61,0xEA,P) end)
for k=1,40 do wait(400) S('g'..k) end
maps_dump() cdl_dump('cdl')
