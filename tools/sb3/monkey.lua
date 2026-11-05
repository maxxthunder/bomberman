-- Coverage "monkey" for the dead-code sweep (SB3 and SB4): random buttons from power-on for FRAMES frames,
-- then the code/data log as a CDLHEX line. Set before this body: SEED, FRAMES, P2=1 (pad 2 also random),
-- PW="dddd" + PWPOKE=function(s) (poke a password and start, then go random), FORCE={addr=value,...} (WRAM
-- bytes rewritten every frame, e.g. enemy hit points), NOSTART=1 (never press Start/Select after the setup).
math.randomseed(SEED or 1)
local B = {'up', 'down', 'left', 'right', 'a', 'b', 'x', 'y', 'l', 'r', 'start', 'select'}
local W = {8, 8, 8, 8, 7, 7, 3, 3, 2, 2, NOSTART and 0 or 3, NOSTART and 0 or 1}
local tot = 0 for _, w in ipairs(W) do tot = tot + w end
local function pick() local r = math.random() * tot for i, w in ipairs(W) do r = r - w if r <= 0 then return B[i] end end return 'a' end
if P2 then
  local cur, left = {}, 0
  emu.addEventCallback(function()
    if left <= 0 then cur = {} if math.random(3) > 1 then cur[pick()] = true end left = math.random(3, 12) end
    left = left - 1 emu.setInput(cur, 0, 1) end, emu.eventType.inputPolled)
end
if FORCE then emu.addEventCallback(function() for a, v in pairs(FORCE) do emu.write(a, v, emu.memType.snesWorkRam) end end, emu.eventType.endFrame) end
if PWPOKE then PWPOKE(PW) end
for i = 1, (FRAMES or 20000) // 10 do
  local t = {} t[pick()] = true
  if math.random(4) == 1 then t[pick()] = true end
  local n = math.random(2, 8) for k = 1, n do q[#q + 1] = t end
  for k = 1, math.random(1, 4) do q[#q + 1] = {} end
end
at(function()
  local c = emu.getCdlData(emu.memType.snesPrgRom) local t = {}
  for i = 0, #c do t[#t + 1] = string.format('%02x', c[i]) end print('CDLHEX m ' .. table.concat(t)) end)
wait(2)
