-- Coverage run for the dead-code sweep: prepend SCEN; tools/gb2/cov.sh runs them all and keeps each CDL.
-- idle: intro + title for 6000 frames. lesson: LESSON with the bot. snd: 2145, every MUSIC and EFFECT number played.
-- battle: 5656 + bot. power: 4622 + bot. allA / allB: 8566, MODE-A / MODE-B, invincible + stage end forced
-- ($C103 = 1, $C104 = 0) for 60000 frames of bot. over: 8566 without cheats until the game overs.
local INV = {'C92-96A-6EB', 'C92-ACA-6EB', 'C93-03A-6EB'}
if SCEN == 'idle' then wait(6000)
elseif SCEN == 'lesson' then wait(300) press({start=true}) wait(120) press({down=true}) press({a=true}) wait(300) bot(8000, 4)
elseif SCEN == 'snd' then
  to_password() type_pw('2145') wait(300)
  press({down=true})
  for n = 0, 0x40 do press({a=true}) wait(150) press({right=true}) end
  press({down=true})
  for n = 0, 0x60 do press({a=true}) wait(40) press({right=true}) end
  press({down=true}) press({a=true}) wait(200)
elseif SCEN == 'battle' then to_password() type_pw('5656') wait(300) bot(12000, 3)
elseif SCEN == 'power' then start_game('4622', 'A') bot(6000, 5)
elseif SCEN == 'allA' or SCEN == 'allB' then
  at(function() for _, c in ipairs(INV) do emu.addCheat(emu.cheatType.gbGameGenie, c) end
    emu.addCheat(emu.cheatType.gbGameShark, '010103C1') emu.addCheat(emu.cheatType.gbGameShark, '010004C1') end)
  start_game('8566', SCEN == 'allA' and 'A' or 'B')
  for k = 1, 100 do bot(600, k) end
elseif SCEN == 'over' then start_game('8566', 'A') bot(12000, 9)
end
at(function() shot('end_'..SCEN) cdl_dump('cov_'..SCEN) end)
