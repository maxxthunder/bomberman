-- Run the game's own password decoder on many codes (see fuzz.sh, which sets VER, ENTRY, OK, BAD, BUF, ST, BANK, SLOT).
-- Every state the decoder can accept is encoded (encoder below, same rule as password.py) and NRAND random codes
-- (letters 0..NL-1) are added. At the decoder entry the 8 letters are written to BUF and the
-- result read at the decoder's exits (the PC is then put back on the entry; the decoder only reads BUF): 'A' + the six bytes it stores (world, stage, bombs, fire, ST+5, ST+$1A rel.)
-- or 'X' for a rejected code. Output: lines 'F <code hex>:<result> ...'.
local function keys(l6,l7) local v=l6|(l7<<8) local k={} for x=1,6 do v=(v>>1)|((v&1)<<15) k[x]=v&7 end return k end
local function enc(d) local s=0 for x=1,6 do s=s+d[x] end s=s&0xFF local l6,l7=s&15,s>>4 local k=keys(l6,l7) local p={} for x=1,6 do p[x]=d[x]+k[x] end p[7]=l6 p[8]=l7 return p end
local codes={}
local hi=(VER=='sp') and 14 or 15
for d0=0,6 do for d1=0,7 do for d2=1,10 do for d3=1,5 do for d4=0,hi do for d5=0,hi do codes[#codes+1]=enc({d0,d1,d2,d3,d4,d5}) end end end end end end
math.randomseed(93) for i=1,NRAND do local p={} for x=1,8 do p[x]=math.random(0,NL-1) end codes[#codes+1]=p end
if LIMIT then local c2={} for j=1,LIMIT do c2[j]=codes[(j*7919)%#codes+1] end codes=c2 end
print('NCODES', #codes)
local st, i, out = nil, 0, {}
local function hexc(p) local t={} for x=1,8 do t[x]=string.format('%02x',p[x]) end return table.concat(t) end
local function nextcode()
  i=i+1
  if i>#codes then if #out>0 then print('F '..table.concat(out,' ')) end print('DONE') emu.stop(0) return end
  if i>1 then emu.setState({['cpu.pc']=ENTRY}) end   -- the exits sit after PLX: the stack is as it was at the entry
  local p=codes[i] for x=1,8 do wr(BUF+x-1,p[x]) end
end
local function rec(v) out[#out+1]=hexc(codes[i])..':'..v if #out>=2000 then print('F '..table.concat(out,' ')) out={} end nextcode() end
local function inbank() return emu.getState()['memoryManager.mpr['..SLOT..']']==BANK end
function fuzz_arm()
  emu.addMemoryCallback(function() if not st and inbank() then st=true i=0 nextcode() end end, emu.callbackType.exec, ENTRY, ENTRY)
  emu.addMemoryCallback(function() if st and inbank() then
    rec(string.format('A%02x%02x%02x%02x%02x%02x', r(ST), r(ST+1), r(ST+2), r(ST+3), r(ST+5), r(ST+0x1A))) end end, emu.callbackType.exec, OK, OK)
  emu.addMemoryCallback(function() if st and inbank() then rec('X') end end, emu.callbackType.exec, BAD, BAD)
end
-- open the password screen (Special Version: the unused one), enter AAAAAAAA, END (index 28 on the JP grid); the
-- decoder runs with fuzz_arm()'s callbacks in place, about 160 codes per frame
if VER=='sp' then sp_password() else to_password() end
at(fuzz_arm) type_pw({0,0,0,0,0,0,0,0}) if VER=='us' then submit() else submit(28) end wait(15000)
