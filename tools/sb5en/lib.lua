-- SB5 helpers, prepended to test scripts (cat lib.lua test.lua > t.lua; run.sh t.lua).
-- Mesen keeps the cartridge SRAM between runs, so every run starts by wiping it and resetting
-- (set KEEPSRAM=true before including this to skip).
A="0123456789ABCDEFGHJKLMNPQRTUVWXY"   -- character-password symbol values
function rd(a) return emu.read(a,emu.memType.snesWorkRam) end
function wr(a,v) emu.write(a,v,emu.memType.snesWorkRam) end
function srd(a) return emu.read(a,emu.memType.snesSaveRam) end
function swr(a,v) emu.write(a,v,emu.memType.snesSaveRam) end
function inj(s) for i=1,6 do wr(0x62F1+i, A:find(s:sub(i,i),1,true)-1) end end   -- character password buffer $62F2
function injopt(s) for i=1,4 do wr(0x6240+i, tonumber(s:sub(i,i))) end end      -- option password digits $6241
-- savestates must be made inside an exec callback: run queued work at the NMI handler ($00:F3BA)
pend=nil
emu.addMemoryCallback(function() if pend then local f=pend pend=nil f() end end, emu.callbackType.exec, 0xF3BA,0xF3BA, emu.cpuType.snes, emu.memType.snesMemory)
function nmi(f) at(function() pend=f end) wait(2) end
function save() nmi(function() st=emu.createSavestate() end) end
function load(f) nmi(function() emu.loadSavestate(st) if f then f() end end) end
seen={}
function watch(lo,hi,kind) emu.addMemoryCallback(function(a,v) local s=emu.getState() local k=string.format('%02X:%04X %X',s['cpu.k'],s['cpu.pc'],a) if not seen[k] then seen[k]=1 print(kind and 'WR' or 'RD',k,v) end end, kind or emu.callbackType.read, lo, hi, emu.cpuType.snes, emu.memType.snesMemory) end
if not KEEPSRAM then wait(2) at(function() for a=0,0x1FFF do swr(a,0) end emu.reset() end) wait(2) end
-- boot paths (frame counts measured on the retail ROM; Caravan is the same)
function to_title() wait(300) for i=1,7 do press({start=true}) wait(60) end end
function to_options_pw() to_title() press({down=true}) wait(20) press({down=true}) wait(20) press({start=true}) wait(200) press({start=true}) wait(200) end
function to_battle_menu() to_title() press({down=true}) wait(20) press({start=true}) wait(400) end
function to_config_pw()   -- ends with the cursor on the confirm key (OK key)
  to_battle_menu() press({down=true}) wait(20) press({down=true}) wait(20) press({start=true}) wait(300)
  press({start=true}) wait(300) press({down=true}) wait(30) press({start=true}) wait(200)
  press({down=true}) wait(10) press({down=true}) wait(10) for i=1,11 do press({right=true},2) wait(6) end
end
