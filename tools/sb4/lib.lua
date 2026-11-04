-- Prepended to SB4 test scripts (cat lib.lua x.lua > t.lua). Helpers on top of tools/emu/mesen.py.
W=emu.memType.snesWorkRam
function rd(a) return emu.read(a,W) end
function wr(a,v) emu.write(a,v,W) end
-- code/data log as hex for cdl2entries_hirom.py
function cdl_dump() at(function()
  local c=emu.getCdlData(emu.memType.snesPrgRom) local t={}
  for i=1,#c do t[#t+1]=string.format('%02x',c[i]) end print('CDLHEX '..table.concat(t)) end) end
-- power-on -> title menu (cursor on NORMAL GAME)
function to_title() wait(800) press({start=true}) wait(120) press({start=true}) wait(60) end
-- title -> PASSWORD screen, cursor on digit 1
function to_pw() to_title() press({down=true}) wait(10) press({down=true}) wait(10) press({start=true}) wait(200) end
-- type 4 digits with Up (Up adds 1 to the digit under the cursor)
function typepw(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for j=1,d do press({up=true},2) wait(4) end if i<4 then press({right=true},2) wait(4) end end end
-- battle menus -> stage select; 2P is switched to COM (pad 2 is connected in the portable Mesen, so it defaults to MAN)
function battle_menus() for i=1,3 do press({start=true}) wait(90) end press({down=true}) wait(20) press({right=true}) wait(20) for i=1,7 do press({start=true}) wait(90) end end
-- pad 2: emu.setInput(t,0,1) is controller 2 (port 1 lands in pad 1's slot); press2 is press() for pad 2
P2={} emu.addEventCallback(function() emu.setInput(P2,0,1) end, emu.eventType.inputPolled)
function press2(b,n) at(function() P2=b end) wait(n or 4) at(function() P2={} end) wait(6) end
-- title -> BATTLE GAME -> battle royale, single, 1P man + 4 COM, default rules, default characters -> stage select
function to_stage() to_title() press({down=true}) wait(10) press({start=true}) wait(100) battle_menus() end
-- the same after a battle password (back at the PUSH START title, cursor still on PASSWORD)
function title_to_stage() press({start=true}) wait(120) press({up=true}) wait(10) press({start=true}) wait(100) battle_menus() end
-- dump VRAM/CGRAM/OAM as MEM lines (job.sh writes <dir>/<prefix>vram.bin, cgram.bin, oam.bin)
function vdump(p) at(function() p=p or '' local function dm(n,mt,sz) local t={} for a=0,sz-1 do t[#t+1]=string.format('%02x',emu.read(a,mt)) end print('MEM '..p..n..' '..table.concat(t)) end
  dm('vram',emu.memType.snesVideoRam,0x10000) dm('cgram',emu.memType.snesCgRam,512) dm('oam',emu.memType.snesSpriteRam,544) end) end
