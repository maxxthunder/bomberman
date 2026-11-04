-- pce90 helpers, prepended to test scripts by run.sh
W=emu.memType.pceWorkRam
function S(n) at(function() shot(n) end) end
function D(n) at(function() dump(n) end) end
function cdl_dump(n) at(function()
  local c=emu.getCdlData(emu.memType.pcePrgRom) local t={}
  for i=0,#c do t[#t+1]=string.format("%02x",c[i] or 0) end print('CDLHEX '..(n or 'cdl')..' '..table.concat(t)) end) end
-- MPR sampler: remember which logical page each ROM bank was mapped at (for CDL -> entries)
MAPS={}
function sample_mpr() local s=emu.getState() for p=2,7 do local b=s['memoryManager.mpr['..p..']'] MAPS[b]=MAPS[b] or {} MAPS[b][p]=true end end
function maps_dump() at(function() local t={} for b,ps in pairs(MAPS) do for p in pairs(ps) do t[#t+1]=string.format('%02x:%d',b,p) end end table.sort(t) print('MAPS '..table.concat(t,' ')) end) end
emu.addEventCallback(sample_mpr, emu.eventType.endFrame)
-- boot to the title menu (cursor on 1P START)
function to_title() wait(600) end
-- title -> PASSWORD screen, ready for input
function to_password() cur={0,0} to_title() press({down=true}) press({down=true}) press({down=true}) press({run=true}) wait(240) end
-- type a code with the pad: cursor moves on the letter grid (rows of 10/10/9: index 26 '<', 27 '>', 28 END), I enters.
-- Columns wrap mod 10 on rows 0-1 and mod 9 on row 2; Down/Up from column 9 onto row 2 lands on column 8 ($C825).
-- The cursor position is kept across type_pw calls (after END it stays on END); to_password() resets it.
cur={0,0}
local function horiz(c, w) while cur[2]~=c do if (c-cur[2])%w<=w//2 then press({right=true}) cur[2]=(cur[2]+1)%w else press({left=true}) cur[2]=(cur[2]-1)%w end end end
local function vert(r) while cur[1]~=r do press({down=true}) cur[1]=(cur[1]+1)%3 end end
local function moveto(r,c)
  if cur[2]==9 then horiz(c, 10) vert(r) else vert(r) horiz(c, r==2 and 9 or 10) end
end
function type_pw(code)
  for k=1,#code do local i=code:byte(k)-65 moveto(i//10,i%10) press({i=true}) end
  moveto(2,8) press({i=true})
end
-- hold input b each frame until cond() is true
function wait_until(cond, b)
  local function f() if not cond() then table.insert(q, 1, f) end return b end
  q[#q+1]=f
end
