-- Exhaustive decoder fuzz (prepend B0, Y0, Y1; see fuzz_all.py). The game's own decoder ($C8AB) is run on byte 0 = B0
-- and bytes 1-3 = every y in [Y0, Y1) by a small loop patched into free ROM in bank 2 ($D600, $FF fill from $D2AF in the dump):
--   $D600 builds the 8 letters from $3000-$3003 through the $CA88 rows into $3410-$3417, then JMP $C8AB;
--   the decoder's exits are patched: $C9CD (valid) -> $D640 logs y and $3424-$3428 to a 32-entry ring at $3100,
--   $C9D3 (invalid) -> $D690 counts; both then step y and loop, until y = end ($3008 = 1).
-- END on the (unreferenced, patched-in) password screen enters the loop ($C668 JMP $C8AB -> JMP $D600). No per-code Lua, so Mesen runs at full
-- speed; Lua drains the ring once a frame. RAM $3000-$31FF is unused on the password screen.
local P = emu.memType.pcePrgRom
local function rom(a, bytes) local o = 0x4000 + a - 0xC000 for i, v in ipairs(bytes) do emu.write(o + i - 1, v, P) end end
local function hx(s) local t = {} for b in s:gmatch('%x%x') do t[#t + 1] = tonumber(b, 16) end return t end
local CODE = {
  [0xD600] = '82 c2 98 0a 0a 0a 0a 8d 0f 30 b9 00 30 29 0f 18 6d 0f 30 5a a8 b9 88 ca 9d 10 34 7a e8 b9 00 30 4a 4a 4a 4a 18 6d 0f 30 5a a8 b9 88 ca 9d 10 34 7a e8 c8 c0 04 d0 cb 4c ab c8',
  [0xD640] = 'ad 07 30 0a 0a 0a aa ad 01 30 9d 00 31 ad 02 30 9d 01 31 ad 03 30 9d 02 31 ad 24 34 9d 03 31 ad 25 34 9d 04 31 ad 26 34 9d 05 31 ad 27 34 9d 06 31 ad 28 34 9d 07 31 ad 07 30 1a 29 1f 8d 07 30 ee 0c 30 d0 08 ee 0d 30 d0 03 ee 0e 30 80 11',
  [0xD690] = 'ee 09 30 d0 08 ee 0a 30 d0 03 ee 0b 30 ea ea ea ee 03 30 d0 08 ee 02 30 d0 03 ee 01 30 ad 01 30 cd 04 30 d0 15 ad 02 30 cd 05 30 d0 0d ad 03 30 cd 06 30 d0 05 ee 08 30 80 fe 4c 00 d6',
  [0xC668] = '4c 00 d6', [0xC9CD] = '4c 40 d6', [0xC9D3] = '4c 90 d6',
}
local rd, out, done = 0, {}, false
local function r(a) return emu.read(a - 0x2000, W) end
local function drain()
  local wi = r(0x3007)
  while rd ~= wi do
    local b = 0x3100 + rd * 8 local t = {}
    for k = 3, 7 do t[#t + 1] = string.format('%x', r(b + k)) end
    out[#out + 1] = string.format('%x:', r(b) << 16 | r(b + 1) << 8 | r(b + 2)) .. table.concat(t, ',')
    rd = (rd + 1) & 31
  end
end
to_password()
at(function()
  emu.write(0x140E, 8, W) emu.write(0x140F, 2, W) -- cursor on END
  for a = 0x1000, 0x11FF do emu.write(a, 0, W) end
  local p = {B0, Y0 >> 16 & 255, Y0 >> 8 & 255, Y0 & 255, Y1 >> 16 & 255, Y1 >> 8 & 255, Y1 & 255}
  for i, v in ipairs(p) do emu.write(0x1000 + i - 1, v, W) end
  for a, s in pairs(CODE) do rom(a, hx(s)) end
  emu.addEventCallback(function()
    if done then return end
    drain()
    if r(0x3008) ~= 0 then
      done = true
      local rej = r(0x3009) | r(0x300A) << 8 | r(0x300B) << 16
      local acc = r(0x300C) | r(0x300D) << 8 | r(0x300E) << 16
      print('DONE ' .. rej .. ' ' .. acc .. ' ' .. #out) print('ACC ' .. table.concat(out, ' ')) emu.stop(0)
    end
  end, emu.eventType.endFrame)
end)
press({i = true})
for f = 1, 2000000 do q[#q + 1] = {} end
