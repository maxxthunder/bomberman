-- Bomberman '93: pick title item 3 (VS / COM-LINK) and screenshot what follows. Run with run.sh pce93 <rom> link93.lua
wait(400) press({run=true}) wait(400) S('title')
press({down=true}) wait(20) press({down=true}) wait(20) S('item3')
at(function() print('menu index $3C72 = '..r(0x3c72)) end)
press({run=true}) wait(300) S('after') at(function() print('$3895 = '..r(0x3895)) end)
