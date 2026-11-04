-- The title-screen code ($1AC64 checks the held-button history against $1ACCA): Right, Left, Left+Down, Down,
-- Down+Right, Down+Right+II, each held a few frames. DEBUG=1 first applies TCRF's patch in memory (ROM $3F5B:
-- 89 85 67 A9 9D -> 29 85 67 A9 98, the launcher at $3F54 then jumps to bank $12:$9829 instead of $9D89).
if DEBUG then
  local p={0x29,0x85,0x67,0xA9,0x98}
  for i=1,5 do emu.write(0x3F5A+i, p[i], emu.memType.pcePrgRom) end
end
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
at(function() shot('menu') end)
for _,b in ipairs({{right=true},{left=true},{left=true,down=true},{down=true},{down=true,right=true},{down=true,right=true,ii=true}}) do
  for i=1,8 do q[#q+1]=b end
end
wait(120) at(function() shot('st1') end) wait(120) at(function() shot('st2') end)
for i=1,(MOVES or 0) do press({down=true},4) wait(10) end
if MOVES then press({run=true}) wait(150) at(function() shot('st3') end) end
