-- Invincibility check: start area 1 (2200), write INV to $3709 (2 = INV_MODE, 0 = normal), drop a bomb and stand
-- on it, then walk back and forth; logs lives ($3704) before and after (INV=2: stays 3, INV=0: 3 -> 2).
function pw_type(s)
  for i=1,4 do local d=tonumber(s:sub(i,i))
    if d<=5 then for k=1,d do press({up=true},3) end else for k=d,9 do press({down=true},3) end end
    if i<4 then press({right=true},3) end end
  press({i=true})
end
loadfile('pw.mst') wait(4) pw_type('2200') wait(430)
for k=1,14 do press({run=true}) wait(24) end
wait(150) at(function() w8(0x3709, INV or 0) end) press({i=true}) wait(240) at(function() shot('b1') print('3704='..r8(0x3704)..' 3709='..r8(0x3709)) end)
for i=1,40 do press({right=true},10) press({left=true},10) end at(function() shot('b2') print('3704='..r8(0x3704)) end)
