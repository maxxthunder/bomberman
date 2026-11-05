-- Coverage run for the dead-code sweep: prepend SCEN; tools/pocket/cov.sh runs them all and keeps each CDL.
-- idle: Hudson logo, intro and title for 8000 frames. new: Normal Game > New Game with the bot. jump: Jump Game with
-- the bot. s<code>: a password (every table code), invincible ($C2CC = 1) and the bot for 4000 frames, Start/A pressed
-- now and then (pause, world select, text). over: Forest 1 without cheats until the game overs. ending: 0278 and A.
local function bots(n) for k = 1, n do bot(500, k) press({a=true}) end end
if SCEN == 'idle' then wait(8000)
elseif SCEN == 'new' then wait(1200) press({start=true}) wait(150) press({a=true}) wait(60) press({a=true}) wait(60) press({a=true}) bots(16)
elseif SCEN == 'jump' then wait(1200) press({start=true}) wait(150) press({down=true}) press({a=true}) wait(60) press({a=true}) bots(16)
elseif SCEN:sub(1, 1) == 's' then
  at(function() emu.addCheat(emu.cheatType.gbGameShark, '0101CCC2') end)
  start_game(SCEN:sub(2)) bots(6) press({start=true}) wait(100) press({down=true}) press({start=true}) bots(2)
elseif SCEN == 'over' then start_game('7693') bots(30)
elseif SCEN == 'ending' then to_password() type_pw('0278') for k = 1, 60 do wait(100) press({a=true}) end
end
at(function() shot('end_'..SCEN) cdl_dump('cov_'..SCEN) end)
