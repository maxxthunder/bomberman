-- Shared helpers for the 8-player demo (prepended by run.sh after bizhawk8.py's prelude).
-- RAM: the game keeps its variables at $FF0000 + offset (a6 = $FF0000), e.g. $2F4-$302 = the 8 pad words
-- (bit 0 Up, 1 Down, 2 Left, 3 Right, 4 B, 5 C, 6 A, 7 Start, active high; read at $3068).
-- Press another player's buttons with PFX="P3 " press({A=true}) PFX=nil.
DOMAIN="68K RAM"
client.speedmode(6400)
function w8(a,v) memory.write_u8(a,v,DOMAIN) end
function w16(a,v) memory.write_u16_be(a,v,DOMAIN) end
function tap(b,n) press({[b]=true},n or 3) end
