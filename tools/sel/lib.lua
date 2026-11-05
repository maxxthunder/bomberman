-- Bomberman Selection helpers (tools/emu/run.sh sel script.lua): menu paths, password entry and RAM reads.
function pc() return emu.getState()['cpu.pc'] end
function bank() return emu.getState()['cart.prgBank'] end
-- cart menu -> Bomber Boy title -> BOMBER BOY mode menu (NEW GAME / CONTINUE / MENU)
function boy() wait(300) press({start=true}) wait(120) press({start=true}) wait(400) press({start=true}) wait(120) end
function pwscreen() boy() press({start=true}) wait(60) press({down=true}) wait(20) press({start=true}) wait(90) end
-- Bomber Boy grid symbols; the entry buffer is $C480-$C487 (0-31). pokepw fills it and puts the cursor on END.
SYM="12345678ABCDEFGHJKLMNOPQRSTUWXYZ"
function pokepw(p) at(function() for i=1,8 do wr(0xC47F+i, SYM:find(p:sub(i,i),1,true)-1) end end)
  for i=1,4 do press({down=true}) end press({right=true}) press({right=true}) end
-- Bomber Man mode -> ENTER SECRET CODE; typecode steps each letter with Up from blank ($10) and stores it with A,
-- the 20th letter submits
function bmcode() wait(300) press({start=true}) wait(120) press({start=true}) wait(400) press({start=true}) wait(120)
  press({b=true}) wait(60) press({down=true}) wait(30) press({start=true}) wait(150) press({down=true}) wait(20) press({start=true}) wait(120) end
function typecode(p) for i=1,#p do for k=1,16-(p:byte(i)-65) do hold({up=true},2) wait(3) end press({a=true},3) end end
-- cart menu -> Bomberman title; type_pw as in tools/gb1 (Up/Down step a digit, A stores it, Start checks)
function gbtitle() wait(300) press({start=true}) wait(150) press({up=true}) wait(30) press({a=true}) wait(300) press({down=true}) press({start=true}) wait(30) end
function type_pw(code)
  for k=1,4 do local d=code:byte(k)-48
    if d<=5 then for i=1,d do press({up=true},2) end else for i=1,10-d do press({down=true},2) end end
    if k<4 then press({a=true}) end end
  press({start=true})
end
