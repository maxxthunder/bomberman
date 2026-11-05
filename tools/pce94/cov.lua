-- Coverage segments for the dead-code sweep (cov.py appends the segment calls and cdl_dump('cov')).
-- cdl_dump(name) prints the Mesen code/data log of the HuCard (or, on the demo, of the System Card + CD RAM as
-- Mesen logs them: pcePrgRom is the HuCard / System Card image) as DUMP <name>.bin.
function cdl_dump(n) at(function() local c=emu.getCdlData(emu.memType.pcePrgRom) local t={}
  for i=(c[0] and 0 or 1),#c do t[#t+1]=string.format('%02x',c[i]) end print('DUMP '..n..' '..table.concat(t)) end) end
function pw_type(s)
  for i=1,4 do local d=tonumber(s:sub(i,i))
    if d<=5 then for k=1,d do press({up=true},3) end else for k=d,9 do press({down=true},3) end end
    if i<4 then press({right=true},3) end end
  press({i=true})
end
local keep=false local fr=0
emu.addEventCallback(function() fr=fr+1 if keep and fr%30==0 then w8(0x3704,3) end end, emu.eventType.endFrame)
-- random input; Run only when withrun (it pauses in a stage)
function mash(n,seed,withrun) math.randomseed(seed) local k={'up','down','left','right','i','ii','i'} if withrun then k[#k+1]='run' end
  for f=1,n,8 do local b={} b[k[math.random(#k)]]=true for j=1,8 do q[#q+1]=b end end end
-- password -> area map -> stage, random play for n frames with lives kept at 3
function play(code,n,seed) loadfile('pw.mst') wait(4) pw_type(code) wait(430) for k=1,14 do press({run=true}) wait(24) end
  at(function() keep=true shot('p'..code) end) mash(n,seed) at(function() keep=false end) end
function gameover(code,seed) loadfile('pw.mst') wait(4) pw_type(code) wait(430) for k=1,14 do press({run=true}) wait(24) end
  wait(300) at(function() w8(0x3704,0) end) mash(2500,seed) for i=1,6 do press({run=true}) wait(60) end mash(1500,seed+1,true) end
function title(n) wait(n) press({run=true}) wait(120) mash(1500,5,true) end
function battle(n,seed) wait(700) press({run=true}) wait(120) press({run=true}) wait(120) press({down=true},8) wait(20) press({run=true},8) wait(200) mash(n,seed,true) end
-- the title code (Sound Room, or with DEBUG the debug menu), then random input
function soundroom(n,seed) if DEBUG then local p={0x29,0x85,0x67,0xA9,0x98} for i=1,5 do emu.write(0x3F5A+i,p[i],emu.memType.pcePrgRom) end end
  wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
  for _,b in ipairs({{right=true},{left=true},{left=true,down=true},{down=true},{down=true,right=true},{down=true,right=true,ii=true}}) do for i=1,8 do q[#q+1]=b end end
  wait(200) at(function() shot('sr') end) mash(n,seed,true) end
-- debug menu item k (0 stage select, 1 boss battle, 2 impressive ending, 3 sound mode), then random input
function debugitem(k,n,seed) DEBUG=1 soundroom(0,1) for i=1,k do press({down=true},4) wait(10) end press({run=true}) wait(200)
  at(function() keep=true shot('d'..k) end) mash(n,seed,k~=1 and k~=0) end
-- RAM bytes ever written with a value other than 0 (for the unset-flag search): wn_dump() prints them as a bitmap
local WN={} emu.addMemoryCallback(function(a,v) if v~=0 then WN[a]=true end end, emu.callbackType.write, 0x2000, 0x3FFF)
function wn_dump() at(function() local t={} for a=0x2000,0x3FFF do t[#t+1]=WN[a] and '1' or '0' end print('WNZ '..table.concat(t)) end) end
-- demo: the CD program runs from RAM, which the code/data log does not cover. ramtrace() records every executed
-- byte of a RAM type (CD RAM / ADPCM / work RAM ...) and ramtrace_dump() prints one bitmap per type as 'RX <type> 0101...' (log.txt).
local RX={}
function ramtrace() emu.addMemoryCallback(function(a)
  local r=emu.convertAddress(a, emu.memType.pceMemory) if r.memType~=emu.memType.pcePrgRom then
    local t=RX[r.memType] if not t then t={} RX[r.memType]=t end t[r.address]=true end end, emu.callbackType.exec, 0x0000, 0xFFFF) end
function ramtrace_dump() at(function() for mt,t in pairs(RX) do local n=0 for k in pairs(t) do if k>n then n=k end end
  local s={} for i=0,n do s[#s+1]=t[i] and '1' or '0' end print('RX '..mt..' '..table.concat(s)) end end) end
-- map graphics for maps.py: when the stage loader ($F022) runs for a map id ($B7) not seen yet in this run, log the
-- cell-graphics table pointer ($95/$96, bank $341B) and, 120 frames later, dump VRAM and the palette.
local MSEEN={} local mfr=0
emu.addEventCallback(function() mfr=mfr+1 end, emu.eventType.endFrame)
emu.addMemoryCallback(function()
  if GAME~="card" then return end local id=r8(0xB7) if MSEEN[id] then return end MSEEN[id]=true local t=mfr+120
  local function chk() if mfr>=t then print(string.format('MAPGFX %d %02X%02X %02X B2=%d B4=%d B6=%d', id, r8(0x96), r8(0x95), r8(0x341B), r8(0xB2), r8(0xB4), r8(0xB6)))
    dump('vram_'..id, emu.memType.pceVideoRam) dump('pal_'..id, emu.memType.pcePaletteRam) return true end end
  local ref ref=emu.addEventCallback(function() if chk() then emu.removeEventCallback(ref, emu.eventType.endFrame) end end, emu.eventType.endFrame)
end, emu.callbackType.exec, 0xF022, 0xF022)
