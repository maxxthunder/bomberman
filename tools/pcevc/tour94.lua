-- Bomberman '94: screenshots of a fixed input sequence, for comparing JP and World screen by screen.
-- MODE='attract': no input, a shot every 90 frames for 6000 frames (title, intro, demo).
-- MODE='story': title -> Run -> NORMAL GAME, a shot every 45 frames for 3000 frames, then Run every 100 frames.
-- run.sh pce94 <rom> tour94.lua MODE='"story"'
local n=0
local function burst(frames, step) for f=1,frames,step do wait(step) n=n+1 local k=n at(function() shot(string.format('%s_%03d', MODE, k)) end) end end
if MODE=='attract' then burst(6000, 90)
else
  wait(700) press({run=true}) wait(120) press({run=true}) burst(3000, 45)
  for i=1,20 do press({run=true}) wait(100) n=n+1 local k=n at(function() shot(string.format('%s_%03d', MODE, k)) end) end
end
