-- Hearts code check: prepend CODES (password.mjs encode({hearts: n})); a new game with them in the cheat engine, west
-- to the field, then the in-play max HP $C38E and HP $C390 are printed, a bomb is taken (one heart off), and printed again.
new_game(false)
at(function() for _, c in ipairs(CODES) do print('cheat', c, pcall(emu.addCheat, emu.cheatType.gbGameShark, c)) end end)
to_field()
at(function() print('HEARTS', VER, 'max', rd(0xC38E), 'hp', rd(0xC390)) shot('hearts_'..VER) arm() end)
press({a=true},8) wait(200)
at(function() print('HIT', VER, 'max', rd(0xC38E), 'hp', rd(0xC390), 'block', rd(BLOCK), rd(BLOCK + 1)) shot('hearts_hit_'..VER) end)
