-- Put each item id ($10-$14, and $13 which the game never places) on the floor next to player 1 the way the game
-- does ($1C3E: cell flags $C83 = $41, item $C81, the 4 tile bytes), walk player 1 onto it and log its counters
-- (+$20 bombs, +$22 fire, +$24 kick, +$26 item $13, +$28 line bomb).
local P=0x1A4
local function cnt() local t={} for o=0x20,0x28,2 do t[#t+1]=r16(P+o) end return table.concat(t," ") end
for _,k in ipairs({0x10,0x11,0x12,0x13,0x14}) do
  savestate.load(STATES.."battle_tap.state")
  local c=0x522+2*0x40+1*4           -- cell x=2, y=1 (right of player 1)
  w8(c+0xC83,0x41) w8(c+0xC81,k) w8(c+1,k) w8(c+3,0x80+k) w8(c+0x641,0x40+k) w8(c+0x643,0xC0+k)
  wait(2) shot(string.format("item%X",k))
  local b=cnt() press({Right=true},20) log(string.format("item $%X: %s -> %s",k,b,cnt()))
end
