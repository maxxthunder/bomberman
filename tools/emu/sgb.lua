-- Super Game Boy packet sniffer for Mesen 2 in plain Game Boy mode (no SGB BIOS needed). Shared by tools/gb1-gb3,
-- built into a script by tools/emu/sgb_dump.py after the game's lib.lua.
-- * Decodes the SGB packets the game sends through $FF00 (reset pulse P14 = P15 = 0, then 128 bits: P14 low = 0,
--   P15 low = 1, stop bit): prints 'SGB <frame> <16 bytes hex>' per packet.
-- * Answers MLT_REQ the way an SGB does, so the game's SGB check passes: with 2 or 4 players on, a read of $FF00 with
--   P14 = P15 = 1 returns $F - joypad id in the low nibble; the id steps when P15 goes low -> high.
-- * For a *_TRN packet (PAL_TRN $0B, ATTR_TRN $15, CHR_TRN $13, PCT_TRN $14) the 4 KB the SGB would take from the
--   next frame's screen is printed as 'TRN <cmd> <arg> <hex>': the BG tiles shown in the 20 x 13 tile top of the
--   screen, in order (SCX/SCY = 0 is assumed, as the transfer protocol requires).
local bits, nbits, inpkt, pkt, last = {}, 0, false, {}, 0x30
local players, id = 1, 0
local trn = nil
local function bytehex(t) local s = {} for i = 1, #t do s[i] = string.format('%02x', t[i]) end return table.concat(s) end
local function done()
  local cmd = pkt[1] >> 3
  print(string.format('SGB %d %s', FRAME or 0, bytehex(pkt)))
  if cmd == 0x11 then players = ({1, 2, 1, 4})[(pkt[2] & 3) + 1] id = 0 end
  if cmd == 0x0B or cmd == 0x15 or cmd == 0x13 or cmd == 0x14 then trn = {cmd, pkt[2], 2} end
end
emu.addMemoryCallback(function(a, v)
  local p14, p15 = v & 0x10, v & 0x20
  if p14 == 0 and p15 == 0 then inpkt = true nbits = 0 pkt = {} bits = {}
  elseif inpkt and (last & 0x30) == 0x30 and (p14 == 0 or p15 == 0) then
    if nbits < 128 then
      local b = p14 == 0 and 0 or 1
      local k = nbits // 8 + 1 pkt[k] = (pkt[k] or 0) | (b << (nbits % 8))
    end
    nbits = nbits + 1
    if nbits == 129 then inpkt = false done() end
  end
  if players > 1 and (last & 0x20) == 0 and p15 ~= 0 then id = (id + 1) % players end
  last = v
end, emu.callbackType.write, 0xFF00, 0xFF00, emu.cpuType.gameboy, emu.memType.gameboyMemory)
emu.addMemoryCallback(function(a, v)
  if players > 1 and (last & 0x30) == 0x30 then return (v & 0xF0) | (0x0F - id) end
end, emu.callbackType.read, 0xFF00, 0xFF00, emu.cpuType.gameboy, emu.memType.gameboyMemory)
emu.addEventCallback(function()
  if not trn then return end
  trn[3] = trn[3] - 1
  if trn[3] > 0 then return end
  local lcdc = emu.read(0xFF40, emu.memType.gameboyMemory)
  local map = (lcdc & 0x08) ~= 0 and 0x1C00 or 0x1800
  local t = {}
  for n = 0, 255 do
    local e = emu.read(map + (n // 20) * 32 + n % 20, emu.memType.gbVideoRam)
    local base = (lcdc & 0x10) ~= 0 and e * 16 or 0x1000 + ((e ~ 0x80) - 0x80) * 16
    for k = 0, 15 do t[#t + 1] = string.format('%02x', emu.read(base + k, emu.memType.gbVideoRam)) end
  end
  print(string.format('TRN %02x %02x %s', trn[1], trn[2], table.concat(t)))
  trn = nil
end, emu.eventType.endFrame)
