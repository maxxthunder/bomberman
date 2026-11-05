-- Check the demo's Game Genie codes in BizHawk's cheat system (client.addcheat): boot with each code on, start the
-- battle, log player 1's record (+$20 bombs, +$22 fire, +$24 kick, +$28 line bomb) and count the hidden items the
-- way itemmap.lua does (cell +$C83 bit 3 = brick with an item, +$C81 = item).
local CODES={"","CN4T-AADC","PNLA-BE0E","PNLA-BE0N","BALA-AAHC","BALA-AAHJ"}
local P=0x1A4
for _,c in ipairs(CODES) do
  client.reboot_core() if c~="" then client.addcheat(c) end
  wait(200) tap("Start") wait(60)
  local n={}
  for x=0,24 do for y=0,16 do local a=0x522+x*0x40+y*4
    local f,k=memory.read_u8(a+0xC83,DOMAIN),memory.read_u8(a+0xC81,DOMAIN)
    if f&8~=0 and k~=0 then n[k]=(n[k] or 0)+1 end end end
  local s={} for k,v in pairs(n) do s[#s+1]=string.format("$%X x%d",k,v) end table.sort(s)
  log(string.format("%-10s bombs %d fire %d kick %d line %d item26 %d | items %s",c=="" and "(none)" or c,
    r16(P+0x20),r16(P+0x22),r16(P+0x24),r16(P+0x28),r16(P+0x26),table.concat(s," ")))
  if c~="" then client.removecheat(c) end
end
