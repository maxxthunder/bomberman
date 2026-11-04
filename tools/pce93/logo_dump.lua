-- Title screen VRAM / palette / SAT dump for logo.py: tools/pce93/run.sh logo_dump.lua <us|jp|sp>
-- writes title.vram, title.pal, title.spr (and title.png) next to this script's copy
wait(400) press({run=true}) wait(400) S('title') at(function() vdump('title') end)
