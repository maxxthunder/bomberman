-- Coverage run for the dead-code sweep: prepend SCEN; tools/max/cov.sh runs them all and keeps each CDL.
-- idle: boot, intro and title for 8000 frames. sound: the sound-test code, then every music / effect number.
-- battle: BattleGame, A through the setup, bot. pitch: Pitch Area send and receive (no partner). play: a new game,
-- invincible (C32-EBA-C41), lives held (0103F7C2), every Charabom owned (8001xxA1), 60000 frames of bot.
-- over: a new game without cheats until the game over, then Continue.
local function cb(c) emu.addCheat(emu.cheatType.gbGameShark, c) end
if SCEN == 'idle' then wait(8000)
elseif SCEN == 'sound' then to_title()
  for _, d in ipairs({'right','left','right','right','left','left','right','left','right','left','left','right'}) do local b = {} b[d] = true press(b, 3) end
  press({a=true}) wait(60)
  for k = 1, 60 do press({a=true}) wait(40) press({right=true}) end press({down=true})
  for k = 1, 60 do press({a=true}) wait(20) press({right=true}) end press({b=true}) wait(200)
elseif SCEN == 'battle' then to_title() press({down=true}) press({a=true}) wait(100)
  for k = 1, 12 do press({a=true}) wait(60) end bot(12000, 5)
  for k = 1, 12 do press({start=true}) wait(60) press({a=true}) wait(60) end bot(6000, 6)
elseif SCEN == 'pitch' then to_title() press({down=true}) press({down=true}) press({a=true}) wait(60)
  press({a=true}) wait(60) press({a=true}) wait(600) press({b=true}) wait(120)
  press({down=true}) press({a=true}) wait(60) press({a=true}) wait(60) press({a=true}) wait(600) press({b=true}) wait(120)
elseif SCEN == 'play' then
  at(function() emu.addCheat(emu.cheatType.gbGameGenie, 'C32-EBA-C41') cb('0103F7C2')
    for n = 0, 29 do local a = 0x10 + 8 * n cb(string.format('8001%02X%02X', a & 0xFF, 0xA1 + (a >> 8))) end end)
  start_new() for k = 1, 20 do bot(3000, k) end
elseif SCEN == 'over' then start_new() bot(9000, 9) for k = 1, 6 do press({a=true}) wait(120) end bot(3000, 10)
end
at(function() shot('end_'..SCEN) cdl_dump('cov_'..SCEN) end)
