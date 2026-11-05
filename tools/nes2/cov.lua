-- Coverage runs for the CDL (set MODE first; run with run.sh, the CDL lands in cov_<MODE>.cdlhex):
--   all    : password CODE1, invincible ($04E6/$04E8 held), a random bot for 1,000 frames a stage, then the
--            stage-clear counter $B7 = $F0, for NST stages (cov.sh: one area per run; the run from 6-1 reaches the ending)
--   over   : the attract demo, then NORMAL MODE and the bot without help until game over and the password screen,
--            then CONTINUE with that password
--   vs, battle : VS MODE / BATTLE MODE, START and A mashed through the setup, then random input on all three pads
--   secret : every secret code (CODES), each from a saved password screen, 1,200 frames each
local P, inv = {}, false
local INV, CLR = 0x4E6, REG == 'jp' and 0xA9 or 0xB7   -- JP zero page sits $0E lower
emu.addEventCallback(function() if inv then emu.write(INV, 1, R) emu.write(INV + 2, 9, R) end end, emu.eventType.startFrame)
if MODE == 'all' then
  to_password() type_pw(CODE1) at(function() inv = true end) wait(400)
  for s = 1, NST do bot(1000, s) at(function() emu.write(CLR, 0xF0, R) end) wait(1000) end
  wait(1500) S('end_'..NST) press({start=true}) wait(1500) S('end2_'..NST)
elseif MODE == 'over' then
  wait(300) press({start=true}) wait(3000) S('demo') press({start=true}) wait(400) press({start=true}) wait(150)
  press({start=true}) wait(200) bot(30000, 3) S('over')
elseif MODE == 'vs' or MODE == 'battle' then
  MULTI = true
  to_menu() for k = 1, MODE == 'battle' and 2 or 1 do press({down=true},6) wait(10) end S('vs0') press({start=true}) wait(100) S('vs1')
  press({start=true}) wait(60) press({start=true}) wait(60) press({a=true}) wait(60) press({start=true}) wait(200) S('vs2')
  bot(12000, 5) S('vs3')
else
  to_password() at(function() in_cpu(function() P.st = emu.createSavestate() end) end) wait(2)
  for k, c in ipairs(CODES) do
    at(function() in_cpu(function() emu.loadSavestate(P.st) end) end) wait(2) cur = {0, 0}
    type_pw(c) wait(300) S('s'..k) press({start=true}) wait(300) S('t'..k) bot(900, k)
  end
end
cdl_dump('cov_'..MODE)
