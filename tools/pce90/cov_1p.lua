-- coverage: password start, random play each stage, force clear ($2437), NST stages, then the ending
-- deaths patched out in PRG (fire $09:8AB3, enemies $0A:A485 -> RTS) so the bot survives; other runs cover deaths
math.randomseed(SEED or 1)
local P=emu.memType.pcePrgRom
if NODIE then emu.write(BANKFIRE or 0x12AB3,0x60,P) emu.write(BANKENEMY or 0x14485,0x60,P) end
local dirs={'up','down','left','right'}
local function bot() local b={} b[dirs[math.random(4)]]=true if math.random(5)==1 then b.i=true end if math.random(40)==1 then b.ii=true end return b end
local function play(n) for k=1,n//6 do local b=bot() for j=1,6 do q[#q+1]=b end end end
to_password() type_pw(START or 'MUVWLNPC') wait(700)
for st=1,(NST or 32) do
  play(PLAY or 300)
  local cur, t = nil, 0
  at(function() cur=emu.read(0x84A,W)*8+emu.read(0x84B,W) print('clear', cur//8+1, cur%8+1) if st%8==0 then shot('st'..st) end emu.write(0x437,1,W) end)
  wait_until(function() t=t+1 local v=emu.read(0x84A,W)*8+emu.read(0x84B,W) return v~=cur or t>1500 end, {})
  wait(200)
end
for k=1,(NEND or 0) do wait(400) S('end'..k) end
maps_dump() cdl_dump('cdl')
