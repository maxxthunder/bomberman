-- Forced-win coverage (prepend PW, optional HOOK/TARGET for Wario = 0x537C/0x5393): invincible; every 400 frames the
-- next pass through the enemy cell check $01:536D jumps to the boss-defeated path $01:5384 (set won), so the run
-- goes through every stage and the staff roll. BOSS=1 with a boss code (5141 3569 2828 0874 1726 ...): one forced win
-- and no input, so the boss-clear text isn't paged away (the bot run skips texts 1-4). tools/gb1/run.sh cov_win.lua [jp|wario]
if VER == 'wario' then HOOK, TARGET = HOOK or 0x537C, TARGET or 0x5393 end
WIN=false
at(function() emu.addCheat(emu.cheatType.gbGameGenie, 'C98-37B-D5D') end)
on_exec(1, HOOK or 0x536D, function() if WIN then WIN=false local s=emu.getState() s['cpu.pc']=TARGET or 0x5384 emu.setState(s) print('jump',FRAME,rd(0xC3F0)) end end)
to_password() type_pw(PW or '4696') wait(700)
if BOSS then at(function() WIN=true end) wait(1200) for k=1,20 do press({a=true}) wait(150) end
else for k=1,110 do at(function() WIN=true end) bot(400,k) if k%4==0 then at(function() shot('s'..k) end) end end end
at(function() shot('end') cdl_dump('cov_win') end)
