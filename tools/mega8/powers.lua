-- Line bomb ($28) and kick ($24) in play. Player 1 starts at cell (1,1); the cells right of it are floor.
local P=0x1A4
savestate.load(STATES.."battle_tap.state")
w16(P+0x20,4) w16(P+0x28,1)
press({Right=true},2)                          -- face right without leaving the cell
tap("A") wait(4) tap("A") wait(4)
log("line bomb: bombs left "..r16(P+0x20)) shot("linebomb")
savestate.load(STATES.."battle_tap.state")
w16(P+0x24,1)
press({Right=true},48) tap("A") press({Left=true},48) local b=r16(P+0x10)
press({Right=true},30) wait(30) shot("kick")
local n=0 for i=0,38 do local o=0x1EF2+0x22*i if memory.read_u32_be(o+8,DOMAIN)==0x2250 or memory.read_u32_be(o+8,DOMAIN)==0x22D2 then n=n+1 log(string.format("bomb object x=%d y=%d handler %X",r16(o+0xC),r16(o+0xE),memory.read_u32_be(o+8,DOMAIN))) end end
-- the same walk without the kick item, for comparison
savestate.load(STATES.."battle_tap.state")
press({Right=true},48) tap("A") press({Left=true},48) press({Right=true},30) wait(30) shot("nokick")
for i=0,38 do local o=0x1EF2+0x22*i local h=memory.read_u32_be(o+8,DOMAIN) if h==0x2250 or h==0x22D2 then log(string.format("no kick: bomb object x=%d y=%d",r16(o+0xC),r16(o+0xE))) end end
log("player 1 x after walk "..r16(P+0x10))
