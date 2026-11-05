-- The stage-intro button code ($02:48D5, table $02:4983): CODE (a stage password, default 1354 = Ocean 3), then on the
-- "Area n" screen (straight after the password for areas 2-5) Left Right Left Right Up Down Up Down B Left B Right B Up B Down, A. Invincible ($C2CC); then A
-- (bomb) every 40 frames. Printed: the armed flag $C35B / target $C35C after the code, each bomb counted ($C35D at
-- $02:5F5E), and the frame the flower is spawned ($02:680C).
local seq = {'left','right','left','right','up','down','up','down','b','left','b','right','b','up','b','down'}
at(function() emu.addCheat(emu.cheatType.gbGameShark, '0101CCC2')
  on_exec(2, 0x680C, function() print('FLOWER', FRAME, 'bombs', rd(0xC35D)) shot('flower') end) end)
to_password() type_pw(CODE or '1354') wait(WAIT or 300)
at(function() shot('intro') end)
for _, b in ipairs(seq) do press({[b]=true}) end
press({a=true}) wait(2)
at(function() print('armed', rd(0xC35B), 'target', rd(0xC35C), 'world', rd(0xC1DC), 'stage', rd(0xC1DD) + 1) end)
wait(300)
for k = 1, N or 120 do press({a=true}) wait(GAP or 80) end
wait(120) at(function() shot('after') print('end bombs', rd(0xC35D), 'C1EE', rd(0xC1EE), 'C1EF', rd(0xC1EF)) end)
