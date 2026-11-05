-- Does stage STAGE (prepend STAGE = n, CODE = its password) finish building? Counts soft-block placer tries
-- ($CACF) and NMIs for WAIT frames after the code; a hung build has NMIs off (no new NMIs) and the tries keep rising.
local tries, nmis = 0, 0
emu.addMemoryCallback(function() tries = tries + 1 end, emu.callbackType.exec, 0xCACF, 0xCACF)
local nmi = emu.read(0xFFFA, emu.memType.nesMemory) | emu.read(0xFFFB, emu.memType.nesMemory) << 8
emu.addMemoryCallback(function() nmis = nmis + 1 end, emu.callbackType.exec, nmi, nmi)
local f = 0
emu.addEventCallback(function() f = f + 1
  if f == START + (WAIT or 3000) then print(string.format('STAGE %d tries=%d nmis_last=%d stage=%d', STAGE, tries, nmis, rd(0x58))) emu.stop(0) end
  if f == START then nmis = 0 end end, emu.eventType.endFrame)
to_password() type_pw(CODE) for k = 1, 100000 do q[#q+1] = {} end
