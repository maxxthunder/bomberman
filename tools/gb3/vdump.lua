-- Title screen VRAM dump for logo.py: tools/gb3/run.sh tools/gb3/vdump.lua (Start skips the intro)
wait(200) press({start=true}) wait(300) at(function() vdump('title') shot('title') end)
