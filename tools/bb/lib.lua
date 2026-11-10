-- Atomic Punk / Bomber Boy helpers (tools/emu/run.sh bb script.lua us|jp): menu paths, password entry and RAM reads.
-- Game A's grid and Game B's letters differ by cart (VER).
SYM = VER~="jp" and "12345678BCDFGHJKLMNPQRSTVWXZ?!.=" or "12345678ABCDEFGHJKLMNOPQRSTUWXYZ"
LET = VER~="jp" and "0BCD1FGH2JKLMN3P" or "ABCDEFGHIJKLMNOP"
-- title -> Game A (BOMBER BOY) -> CONTINUE -> INPUT PASSWORD
function pwscreen() wait(300) press({start=true}) wait(150) press({start=true}) wait(150) press({down=true}) wait(20) press({start=true}) wait(120) end
-- fill the entry buffer $C480-$C487 (grid places 0-31) and put the cursor on END
function pokepw(p) at(function() for i=1,8 do wr(0xC47F+i, SYM:find(p:sub(i,i),1,true)-1) end end)
  for i=1,4 do press({down=true}) end press({right=true}) press({right=true}) end
-- type a code on the grid: cursor index = row * 8 + column, A stores the symbol under it
function typepw(p) local cur=0
  for i=1,#p do local t=SYM:find(p:sub(i,i),1,true)-1
    local dr=(t>>3)-(cur>>3) local dc=(t&7)-(cur&7)
    for k=1,math.abs(dr) do press(dr>0 and {down=true} or {up=true}) end
    for k=1,math.abs(dc) do press(dc>0 and {right=true} or {left=true}) end
    press({a=true}) cur=t end end
-- title -> Game B (BOMBER MAN) -> CONTINUE -> ENTER SECRET CODE; each letter steps up from blank ($10), A stores it,
-- the 20th submits
function bmcode() wait(300) press({start=true}) wait(150) press({down=true}) wait(30) press({start=true}) wait(150) press({down=true}) wait(20) press({start=true}) wait(120) end
function typecode(p) for i=1,#p do local v=LET:find(p:sub(i,i),1,true)-1 for k=1,16-v do hold({up=true},2) wait(3) end press({a=true},3) end end
