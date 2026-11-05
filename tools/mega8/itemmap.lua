-- The arena and its hidden items are the same on every boot (fixed RNG seed $27DE, $434). Draw every hidden
-- item over its brick (tile bytes only, like the reveal at $2742) and log the counts per item.
savestate.load(STATES.."battle_tap.state")
local n={} local pos={}
for x=0,24 do for y=0,16 do local c=0x522+x*0x40+y*4
  local f,k=memory.read_u8(c+0xC83,DOMAIN),memory.read_u8(c+0xC81,DOMAIN)
  if f&8~=0 and k~=0 then n[k]=(n[k] or 0)+1 pos[#pos+1]=string.format("%X@%d,%d",k,x,y)
    w8(c+1,k) w8(c+3,0x80+k) w8(c+0x641,0x40+k) w8(c+0x643,0xC0+k) end
end end
for k,v in pairs(n) do log(string.format("item $%X x%d",k,v)) end
log(table.concat(pos," "))
wait(2) shot("itemmap")
