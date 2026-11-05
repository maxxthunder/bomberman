-- Bomberman '94: title -> BATTLE GAME, then Run through every menu (a shot after each) into the match.
-- On the character select (after the 2nd Run) player 1 first presses PICK (e.g. PICK='down right right right' =
-- the 9th character). BTN = the button pressed for each step (default 'run'). Shots b00-b16, then b99 600 frames
-- into the match (b98 at 200 frames). With the defaults the shots b03-b16 are the character select; PICK/BTN
-- did not get past it (how the select confirms is not worked out).
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
press({down=true},8) wait(20) press({run=true},8) wait(200) at(function() shot('b00') end)
for k=1,16 do
  if k==3 and PICK then for m in PICK:gmatch('%a+') do press({[m]=true},6) wait(10) end at(function() shot('pick') end) end
  press({[(k>=3 and BTN) or 'run']=true},6) wait(110) at(function() shot(string.format('b%02d',k)) end)
end
wait(200) at(function() shot('b98') end) wait(400) at(function() shot('b99') end)
