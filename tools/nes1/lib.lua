-- nes1 helpers, prepended to test scripts by run.sh
R=emu.memType.nesInternalRam
function rd(a) return emu.read(a,R) end
function S(n) at(function() shot(n) end) end
function D(n) at(function() dump(n) end) end
-- PRG CDL -> <n>.cdlhex; CHR CDL (nes1: CHR ROM, bit 0 drawn, bit 1 read) -> <n>_chr.cdlhex. getCdlData is 0-based.
function cdl_dump(n) at(function()
  local c=emu.getCdlData(emu.memType.nesPrgRom) local t={}
  for i=0,#c do t[#t+1]=string.format("%02x",c[i] or 0) end print('CDLHEX '..(n or 'cdl')..' '..table.concat(t))
  local ok, h = pcall(emu.getCdlData, emu.memType.nesChrRom)
  if ok and h and #h > 0 then t={} for i=0,#h do t[#t+1]=string.format("%02x",h[i] or 0) end print('CDLHEX '..(n or 'cdl')..'_chr '..table.concat(t)) end
end) end
-- boot -> CONTINUE (Select on the title) -> ENTER SECRET CODE, ready for the first letter
function to_password() wait(200) press({select=true}) press({start=true}) wait(60) end
-- type a code with the pad: each letter starts blank; Right steps A, B ... P, Left/Up/Down step P, O ... A; A enters it.
local AB='ABCDEFGHIJKLMNOP'
function type_pw(code)
  for k=1,#code do local i=AB:find(code:sub(k,k),1,true)-1
    if i+1 <= 16-i then for j=1,i+1 do press({right=true}) end else for j=1,16-i do press({left=true}) end end
    press({a=true}) end
end
-- hold input b each frame until cond() is true
function wait_until(cond, b)
  local function f() if not cond() then table.insert(q, 1, f) end return b end
  q[#q+1]=f
end
-- run fn at the next NMI (savestate calls must come from an exec callback): at(function() in_cpu(f) end)
local cpu_todo
local nmi = emu.read(0xFFFA, emu.memType.nesMemory) | emu.read(0xFFFB, emu.memType.nesMemory) << 8
emu.addMemoryCallback(function() if cpu_todo then local f = cpu_todo cpu_todo = nil f() end end, emu.callbackType.exec, nmi, nmi)
function in_cpu(fn) cpu_todo = fn end
-- random walker that drops bombs (A) and sometimes fires the detonator (B): n frames
function bot(n, seed)
  math.randomseed(seed or 7) local dirs={'up','down','left','right'}
  for k=1,n//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end if math.random(9)==1 then b.b=true end for j=1,6 do q[#q+1]=b end end
end
