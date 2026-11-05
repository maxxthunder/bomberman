-- Coverage runs for the CDL (set MODE first; run with run.sh, the CDL lands in cov_<MODE>.cdlhex):
--   all   : password CODE1 (a stage with every power-up), invincible ($7A held at $FF), a random bot for 1,000 frames
--           a stage, then the stage-clear flag $5E = 1, for NST stages (the run past stage 50 reaches the ending).
--           The test runner stops scripts after ~590 s, so cov.sh runs this in chunks of 8 stages.
--   over  : the title left alone through the attract demo, then START and the bot without help until game over and
--           the GAME OVER password screen; then CONTINUE with a bad and a good code
--   glitch: stages 0, 51-53, 59, 74, 131, 243, 255 by password (bot 600 frames each)
local P = {}
local inv = false
emu.addEventCallback(function() if inv then emu.write(0x7A, 0xFF, R) end end, emu.eventType.startFrame)
if MODE == 'all' then
  to_password() type_pw(CODE1) at(function() inv = true end) wait(300)
  for s = 1, NST do bot(1000, s) at(function() if rd(0x5C) == 0 then emu.write(0x5E, 1, R) end end) wait(500) end
  wait(1500) S('end_'..NST)
elseif MODE == 'over' then
  wait(2500) S('demo') press({start=true}) wait(30) press({start=true}) wait(200) bot(30000, 3) S('over')
  press({start=true}) wait(300) press({select=true}) press({start=true}) wait(60) type_pw('BABABABABABABABABABB') wait(60) type_pw('BABABABABABABABABABA') wait(300)
else
  to_password() at(function() in_cpu(function() P.st = emu.createSavestate() end) end) wait(2)
  for k, c in ipairs(GLITCH) do
    at(function() in_cpu(function() emu.loadSavestate(P.st) end) end) wait(2)
    type_pw(c) wait(300) S('g'..k) bot(600, k)
  end
end
cdl_dump('cov_'..MODE)
