-- Tile-copy log for the text dump: prepend to a gb1 scenario (after lib.lua). Every $00:087F call (queued VRAM copy, A
-- = bank, DE = source, B x C tiles, HL = VRAM) prints 'TX frame bank src w h dst bytes code=tile16,...' once per
-- source/tile-data combination, with the VRAM tile data of each code 2 frames later (the font on screen then).
local seen, pend = {}, {}
local function src_byte(bk, a) if a < 0x4000 then return emu.read(a, ROM) elseif a < 0x8000 then return emu.read(bk*0x4000 + a - 0x4000, ROM) else return rd(a) end end
emu.addMemoryCallback(function()
  local s = emu.getState()
  local a, b, c, de = s['cpu.a'], s['cpu.b'], s['cpu.c'], s['cpu.d']*256 + s['cpu.e']
  if a & 0xE0 ~= 0 then return end
  local bk = a & 0x0F
  local by = {}
  for i = 0, b*c - 1 do by[#by+1] = src_byte(bk, de + i) end
  pend[#pend+1] = {f = FRAME + 2, bk = bk, de = de, b = b, c = c, hl = s['cpu.h']*256 + s['cpu.l'], by = by}
end, emu.callbackType.exec, TXADDR or 0x087F, TXADDR or 0x087F, emu.cpuType.gameboy, BUS)
emu.addEventCallback(function()
  local keep = {}
  for _, p in ipairs(pend) do
    if FRAME < p.f then keep[#keep+1] = p else
      local lcdc = rd(0xFF40)
      local hx, tl, u = {}, {}, {}
      for _, v in ipairs(p.by) do hx[#hx+1] = string.format('%02x', v)
        if not u[v] then u[v] = true
          local base = (lcdc & 0x10) ~= 0 and v*16 or 0x1000 + ((v ~ 0x80) - 0x80)*16
          local t = {} for k = 0, 15 do t[#t+1] = string.format('%02x', emu.read(base + k, VR)) end
          tl[#tl+1] = string.format('%02x', v) .. '=' .. table.concat(t) end end
      local key = string.format('%x %x %d %d %x ', p.bk, p.de, p.b, p.c, p.hl) .. table.concat(tl, ',')
      if not seen[key] then seen[key] = true
        print(string.format('TX %d %02x %04x %d %d %04x %s %s', FRAME, p.bk, p.de, p.b, p.c, p.hl, table.concat(hx), table.concat(tl, ','))) end
    end
  end
  pend = keep
end, emu.eventType.endFrame)
