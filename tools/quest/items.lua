-- Bag pages for tools/quest/items.py: the debug start (every weapon, equipment and item), then each page shot with a
-- 16 KB VRAM dump (vram16) the same frame: page0 (weapons; the cursor still on the A / B boxes), page1, page2
-- (and page1b, page2b).
new_game(true)
press({start=true},8) wait(60) press({a=true},8) wait(40) press({a=true},8) wait(60)
at(function() shot('page0') vram16('page0') end) close_page()
-- pages 1 and 2 open with the cursor on an icon, drawn highlighted: a second dump (page<n>b) after Right has it plain
for p = 1, 2 do open_page(p) at(function() shot('page'..p) vram16('page'..p) end)
  press({right=true},8) wait(30) at(function() shot('page'..p..'b') vram16('page'..p..'b') end) close_page() end
