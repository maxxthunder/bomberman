-- JP config screen used with real presses: STAGE +2, SCENE +4, BOMB +3, STOCK +5, then Run. Prints the RAM it edits.
local function use()
  q={} wait(120) S('cfg_before')
  press({right=true}) wait(8) press({right=true}) wait(8) press({down=true}) wait(8)
  for i=1,4 do press({right=true}) wait(8) end press({down=true}) wait(8) for i=1,3 do press({right=true}) wait(8) end
  for i=1,10 do press({down=true}) wait(8) end for i=1,5 do press({right=true}) wait(8) end
  S('cfg_set') at(function() print(string.format('before Run: world %d stage %d bombs %d lives %d', r(0x3895), r(0x3896), r(0x3897), r(0x389f))) end)
  press({run=true}) wait(500) for i=1,3 do press({run=true}) wait(300) end S('cfg_after')
  at(function() print(string.format('after: world %d stage %d bombs %d lives %d state %d', r(0x3895), r(0x3896), r(0x3897), r(0x389f), r(0x38a1))) end)
end
at(function() on_exec(0x8628,8,function() print('CONFIG at',FRAME) use() end) end)
wait(300) at(function() wr(0x3ffb,1) end) press({select=true,run=true},4) wait(300)
press({run=true}) wait(400) press({run=true}) for i=1,30 do wait(100) if i%3==0 then press({run=true}) end end
