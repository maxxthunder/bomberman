-- nes2 helpers, prepended to test scripts by run.sh
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
-- boot -> title -> game-mode menu (cursor on NORMAL MODE)
function to_menu() wait(300) press({start=true}) wait(400) press({start=true}) wait(150) end
-- menu -> CONTINUE -> INPUT PASSWORD, cursor on the first key ("1" / "P")
function to_password() to_menu() for k=1,3 do press({down=true},6) wait(10) end press({start=true}) wait(150) end
-- random walker that drops bombs: n frames
function bot(n, seed)
  math.randomseed(seed or 7) local dirs={'up','down','left','right'}
  for k=1,n//6 do local b={} b[dirs[math.random(4)]]=true if math.random(3)==1 then b.a=true end for j=1,6 do q[#q+1]=b end end
end
-- password grid ($05:94BE): rows of 8 cells; row 0 = nibbles B A 1 C 9 4 8 6, row 1 = 7 D 2 E F 3 5 0,
-- row 2 = <- <- -> -> DEL DEL END END. D-pad moves (columns wrap mod 8, rows mod 3), A enters; the 8th character submits.
ALPHA = REG=='jp' and 'PCKNFOHIGEBADJLM' or 'K3DH6J8B75214CFG'
local GRID = {0xb,0xa,1,0xc,9,4,8,6,7,0xd,2,0xe,0xf,3,5,0}
cur={0,0}
function type_pw(code)
  for k=1,#code do
    local n=ALPHA:find(code:sub(k,k),1,true)-1 local idx for i=1,16 do if GRID[i]==n then idx=i-1 end end
    local r,c=idx//8,idx%8
    while cur[1]~=r do if (r-cur[1])%3==1 then press({down=true}) cur[1]=(cur[1]+1)%3 else press({up=true}) cur[1]=(cur[1]-1)%3 end end
    while cur[2]~=c do if (c-cur[2])%8<=4 then press({right=true}) cur[2]=(cur[2]+1)%8 else press({left=true}) cur[2]=(cur[2]-1)%8 end end
    press({a=true})
  end
end
-- random input on pads 2 and 3 too (battle coverage): set MULTI = true
emu.addEventCallback(function()
  if MULTI then local d = {'up','down','left','right'}
    for p = 1, 2 do local b = {} b[d[math.random(4)]] = true if math.random(3) == 1 then b.a = true end if math.random(40) == 1 then b.start = true end emu.setInput(b, p) end
  end end, emu.eventType.inputPolled)
