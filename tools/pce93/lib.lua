-- pce93 helpers, prepended to every test (see run.sh)
function mprs() local s=emu.getState() local t={} for i=0,7 do t[#t+1]=string.format('%02x',s['memoryManager.mpr['..i..']']) end return table.concat(t,' ') end
function pc() return emu.getState()['cpu.pc'] end
-- log each distinct PC that touches logical [a,b] (kind = emu.callbackType.read/write/exec)
function watch(a,b,kind,tag) local seen={} emu.addMemoryCallback(function(addr,v)
  local k=string.format('%04x',pc()) if not seen[k] then seen[k]=1 print(string.format('%s pc=%s addr=%04x v=%02x mpr=%s',tag or 'W',k,addr,v or 0,mprs())) end end, kind, a, b) end
-- US title -> password screen
function to_password() wait(400) press({run=true}) wait(400) for i=1,3 do press({down=true}) wait(20) end press({run=true}) wait(220) end
-- print the Mesen code/data log of the HuCard ROM as 'CDL <name> <hex>' (see cdl2entries.py)
function cdl_dump(n) at(function() local c=emu.getCdlData(emu.memType.pcePrgRom) local t={}
  for i=1,#c do t[#t+1]=string.format('%02x',c[i]) end print('CDLHEX '..(n or 'cdl')..' '..table.concat(t)) end) end
-- random pad input for n frames (seeded), for coverage runs
function mash(n,seed) math.randomseed(seed or 1) local k={'up','down','left','right','i','ii'} for f=1,n,8 do local b={} b[k[math.random(#k)]]=true if math.random(4)==1 then b.i=true end for j=1,8 do q[#q+1]=b end end end
-- type a password with real presses on the entry grid (cursor starts on the first letter, 8 per row, END = 22).
-- idx: list of 8 grid indices. Cursor position is tracked here, not read from RAM.
local cur=0
-- The last grid row is short (US 7 entries, JP 5): leave it vertically first, enter it horizontally first.
local function vmove(dr) for i=1,math.abs(dr) do press({[dr>0 and 'down' or 'up']=true},4) wait(8) end end
local function hmove(dc) for i=1,math.abs(dc) do press({[dc>0 and 'right' or 'left']=true},4) wait(8) end end
function grid_to(t) local dr=(t//8)-(cur//8) local dc=(t%8)-(cur%8)
  if dr<0 then vmove(dr) hmove(dc) else hmove(dc) vmove(dr) end cur=t end
function type_pw(idx) cur=0 for k=1,8 do grid_to(idx[k]) press({i=true},4) wait(10) end end
function submit(e) grid_to(e or 22) press({i=true},4) end  -- END: 22 on the US grid, 28 on the JP grid
function pwbuf() local t={} for k=0,7 do t[#t+1]=r(0x3c62+k) end return table.concat(t,',') end
-- frame counter and "do fn n frames after now" (independent of the input queue)
FRAME=0 local later={}
emu.addEventCallback(function() FRAME=FRAME+1 for i=#later,1,-1 do if later[i][1]<=FRAME then local f=later[i][2] table.remove(later,i) f() end end end, emu.eventType.endFrame)
function after(n,fn) later[#later+1]={FRAME+n,fn} end
-- run fn when PC = a with MPR slot (a>>13) holding bank b
function on_exec(a,b,fn) emu.addMemoryCallback(function() if b==nil or emu.getState()['memoryManager.mpr['..(a>>13)..']']==b then fn() end end, emu.callbackType.exec, a, a) end
-- Special Version: the title's menu table (bank 6 $984C, all five entries $A34E = battle) gets entry 0 pointed
-- at the leftover password screen $94A0, so Run on the title opens it (ROM patch in memory only)
function sp_password() at(function() emu.write(0xC000+0x184C,0xA0,emu.memType.pcePrgRom) emu.write(0xC000+0x184D,0x94,emu.memType.pcePrgRom) end)
  wait(400) press({run=true}) wait(400) press({run=true}) wait(220) end
