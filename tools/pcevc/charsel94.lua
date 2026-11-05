-- Bomberman '94: Battle Game character select; dumps VRAM / VCE palette / SAT (cs_vram.bin, cs_pal.bin, cs_spr.bin)
-- and a shot (cs.png), for vramdiff.py. run.sh pce94 <rom> charsel94.lua
wait(700) press({run=true}) wait(120) press({run=true}) wait(120)
press({down=true},8) wait(20) press({run=true},8) wait(200)
press({run=true},6) wait(110) press({run=true},6) wait(110) press({run=true},6) wait(250)
at(function() dump('cs_vram', emu.memType.pceVideoRam) dump('cs_pal', emu.memType.pcePaletteRam) dump('cs_spr', emu.memType.pceSpriteRam) shot('cs') end)
