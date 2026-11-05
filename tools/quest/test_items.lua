-- GameShark item codes on the menu: prepend CODES = {...} (and DEBUG = true for the debug start); a new game, the
-- codes added to Mesen's cheat engine, then every cursor position of the three bag pages is visited and the item name
-- the page prints (US letters $80-$B3 in the BG map, rows 9-12) is printed as NAME <page> <row> <col> <name>.
-- Grids: weapons 7 x 4, equipment 4 x 4, items 8 x 2 (Right walks a row and wraps, Down the next row).
local GRID = { [0] = {4, 7}, {4, 4}, {2, 8} }
-- slot (r, c) of page p -> top-left BG map cell of its 2 x 2 icon (items: two 4-wide panels, at columns 1 and 10)
local function cell(p, r, c) return 1 + 2 * r, (p == 2 and c >= 4) and 10 + 2 * (c - 4) or 1 + 2 * c end
-- the slot's icon as the hex of its 4 tiles' pixels (an empty slot draws the page's blank square)
local function sig(p, r, c) local y, x = cell(p, r, c) local h = {}
  for dy = 0, 1 do for dx = 0, 1 do local m = 0x1800 + (y + dy) * 32 + x + dx
    local t, a = emu.read(m, VR), emu.read(0x2000 + m, VR)
    local o = (a & 8 ~= 0 and 0x2000 or 0) + (t < 0x80 and 0x1000 + t * 16 or t * 16)   -- LCDC bit 4 clear: $8800 mode
    for i = 0, 15 do h[#h + 1] = string.format('%02x', emu.read(o + i, VR)) end end end
  return table.concat(h) end
local P = {[0x00]=' ', [0xb4]='.', [0xb6]='-', [0xb8]='!', [0xb9]='?', [0xba]="'"}
local function name()
  for row = 9, 12 do local s = ''
    for c = 1, 18 do local x = emu.read(0x1800 + row * 32 + c, VR)
      s = s .. (x >= 0x80 and x <= 0x99 and string.char(65 + x - 0x80) or x >= 0x9a and x <= 0xb3 and string.char(97 + x - 0x9a) or P[x] or '') end
    s = s:gsub('^%s+', ''):gsub('%s+$', '')
    if s:find('%a') or s == '!?' then return s end end
  if VER == 'jp' then local h = ''   -- kana: the text box's tiles as hex ('' = an empty slot)
    for row = 10, 12 do for c = 1, 18 do local x = emu.read(0x1800 + row * 32 + c, VR) if x ~= 0 then h = h .. string.format('%02x', x) end end end
    return h end
  return '' end
new_game(DEBUG)
at(function() for _, c in ipairs(CODES or {}) do local ok, e = pcall(emu.addCheat, emu.cheatType.gbGameShark, c) if not ok then print('cheat', c, e) end end end)
wait(30)
for p = 0, 2 do
  open_page(p)
  if p == 0 then at(function() shot('page0') end) end
  for r = 0, GRID[p][1] - 1 do for c = 0, GRID[p][2] - 1 do
    wait(VER == 'jp' and 60 or 0) at(function() print(string.format('NAME %d %d %d %s %s', p, r, c, sig(p, r, c), name())) end) press({right=true},8) wait(16) end
    press({down=true},8) wait(16) end
  at(function() shot('page'..p) end)
  close_page()
end
at(function() local t={} for a=0,0xE3 do t[#t+1]=string.format('%02x',rd(BLOCK+a)) end print('BLOCK '..table.concat(t)) end)
