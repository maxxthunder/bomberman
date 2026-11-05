-- Coverage run for the dead-code sweep: prepend SCEN; tools/gb1/cov.sh runs them all and keeps each CDL.
-- idle: title + attract story for 6000 frames. pw: bad codes, then 4622 and play. battle: 5656 and play.
-- all: 4696 (Wario: 6964 with P='w'), invincible + every set won (GameShark $C100/$C200/$C300 = 0) through the ending.
local function bad() to_password() type_pw('0000') wait(60) type_pw('1234') wait(60) end
if SCEN == 'idle' then wait(6000)
elseif SCEN == 'pw' then bad() for k = 1, 4 do press({b=true}) end wait(30) press({start=true}) wait(30) type_pw('4622') wait(700) bot(5000, 2)
elseif SCEN == 'battle' then to_password() type_pw(P == 'w' and '6565' or '5656') wait(700) bot(8000, 3)
elseif SCEN == 'all' then
  at(function() emu.addCheat(emu.cheatType.gbGameGenie, 'C98-37B-D5D')
    for _, c in ipairs({'010000C1', '010000C2', '010000C3'}) do emu.addCheat(emu.cheatType.gbGameShark, c) end end)
  to_password() type_pw(P == 'w' and '6964' or '4696') wait(700)
  for k = 1, 150 do bot(600, k) end
end
at(function() shot('end_'..SCEN) cdl_dump('cov_'..SCEN) end)
