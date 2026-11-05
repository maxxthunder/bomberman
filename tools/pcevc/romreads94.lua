-- Bomberman '94: which 256-byte pages of the ROM areas the World release changed (banks $26-$27, $31) have been
-- read so far, from Mesen's code/data log (getCdlData is 0-based), checked at every shot. Prepend this file to
-- tour94.lua, stages94.lua, ending94.lua or tools/pce94/codes.lua. Prints "R <shot name> <page> <page> ...".
local seen={}
local oshot=shot
function shot(name) oshot(name)
  local c=emu.getCdlData(emu.memType.pcePrgRom) local t={}
  for _,rg in ipairs({{0x4D000,0x4F7FF},{0x62800,0x63BFF}}) do
    for p=rg[1],rg[2],256 do if not seen[p] then for a=p,p+255 do if c[a]~=0 then seen[p]=1 t[#t+1]=string.format('%05x',p) break end end end end
  end
  if #t>0 then print('R '..name..' '..table.concat(t,' ')) end
end
