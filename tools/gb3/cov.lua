-- Coverage run for the dead-code sweep: prepend SCEN; tools/gb3/cov.sh runs them all and keeps each CDL.
-- idle: intro + title for 6000 frames. story: STORY from the start with the bot. champ: the 3rd title line + bot.
-- boss: DEB1F7F + bot. all<g>: a stage code of area group g (Wood 1, Sand 1, Evil 1), invincible ($C1BC = 1) and
-- every stage ended ($C480 = $FF) for 60000 frames of bot. over: Wood 1 without cheats until the game overs.
if SCEN == 'idle' then wait(6000)
elseif SCEN == 'story' then wait(200) press({start=true}) wait(200) press({a=true}) bot(12000, 4)
elseif SCEN == 'champ' then wait(200) press({start=true}) wait(200) press({down=true}) press({down=true}) press({a=true}) wait(200) bot(12000, 6)
elseif SCEN == 'boss' then
  at(function() emu.addCheat(emu.cheatType.gbGameShark, '0101BCC1') end)
  start_game('DEB1F7F') bot(20000, 8)
elseif SCEN:sub(1, 3) == 'all' then
  at(function() emu.addCheat(emu.cheatType.gbGameShark, '0101BCC1') emu.addCheat(emu.cheatType.gbGameShark, '01FF80C4') end)
  start_game(({all0='0986400', all1='4AA6460', all2='F775818'})[SCEN])
  for k = 1, 100 do bot(600, k) end
elseif SCEN == 'over' then start_game('0986400') bot(8000, 9)
end
at(function() shot('end_'..SCEN) cdl_dump('cov_'..SCEN) end)
