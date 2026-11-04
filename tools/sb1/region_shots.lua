-- region screens: Normal Game, then write the next-scene byte $00A4 for each scene; shots at +120/+400 frames
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(700) S('n11')
local L={0x10,0x08,0x28,0x2F,0x3D,0x44,0x3A,0x3B,0x37,0x38,0x39,0x32,0x33,0x30,0x31,0x3C}
for _,v in ipairs(L) do at(function() emu.write(0xA4,v,W) end) wait(120) S(string.format('s%02x_a',v)) wait(280) S(string.format('s%02x_b',v)) end
