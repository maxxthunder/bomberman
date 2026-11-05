-- Write watch for flag candidates (SB3 and SB4): set WATCH = {WRAM offsets}; rnd(n) = n frames of random d-pad/buttons.
-- WATCH = {wram offsets}; logs each distinct (addr, pc) write and whether a nonzero value was seen
local seen = {}
for _, a in ipairs(WATCH) do
  emu.addMemoryCallback(function(x, v) local s = emu.getState() local k = string.format('%05x %02x:%04x %s', a, s['cpu.k'], s['cpu.pc'], v ~= 0 and 'nz' or 'z')
    if not seen[k] then seen[k] = 1 print('WW ' .. k .. string.format(' v=%02x', v)) end end, emu.callbackType.write, a, a, emu.cpuType.snes, emu.memType.snesWorkRam)
end
math.randomseed(3)
local B = {{up=true},{down=true},{left=true},{right=true},{a=true},{b=true},{x=true},{y=true}}
function rnd(n) for i = 1, n // 8 do local b = B[math.random(#B)] for k = 1, 6 do q[#q+1] = b end q[#q+1] = {} q[#q+1] = {} end end
