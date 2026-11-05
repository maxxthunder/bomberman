-- Title screen VRAM dump for logo.py: tools/gb2/run.sh tools/gb2/vdump.lua [jp|us] (Start skips the intro)
wait(300) press({start=true}) wait(400) at(function() vdump('title') shot('title') end)
