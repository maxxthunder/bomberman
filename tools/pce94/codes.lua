-- Type passwords for real on the PASSWORD screen and start the area. CODES = space-separated list.
-- Up/Down change the digit under the cursor, Right moves on, I submits. Logs $20B2/$20B3/$20B5 after the check and
-- shoots the area map (<code>_map) and the hub after pressing Run 8-10 times (<code>_go8-10), then logs
-- "S code b3 b4 b5" ($20B4 = the stage the hub starts, 0-based).
function pw_type(s)
  for i=1,4 do local d=tonumber(s:sub(i,i))
    if d<=5 then for k=1,d do press({up=true},3) end else for k=d,9 do press({down=true},3) end end
    if i<4 then press({right=true},3) end end
  wait(4) at(function() print(string.format('T %s typed %d%d%d%d', s, r8(0x2FBE), r8(0x2FBF), r8(0x2FC0), r8(0x2FC1))) end)
  press({i=true})
end
for c in CODES:gmatch('%d+') do
  loadfile('pw.mst') wait(4)
  pw_type(c) wait(30)
  at(function() print(string.format('R %s b2=%02x b3=%02x b5=%02x', c, r8(0x20B2), r8(0x20B3), r8(0x20B5))) shot(c..'_pw') end)
  wait(400) at(function() shot(c..'_map') end)
  for k=1,10 do press({run=true}) wait(24) if k>=8 then at(function() shot(c..'_go'..k) end) end end
  at(function() print(string.format('S %s b3=%02x b4=%02x b5=%02x', c, r8(0x20B3), r8(0x20B4), r8(0x20B5))) end)
  if DUMP then at(function() dump(c, emu.memType.pceWorkRam) end) end
end
