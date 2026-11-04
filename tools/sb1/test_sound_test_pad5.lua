-- Sound test from a real pad-5 press (no RAM writes): R held on multitap port D from frame 600 on the title.
-- Run: MESEN_ARGS=--snes.port2.type=Multitap tools/sb1/run.sh tools/sb1/test_sound_test_pad5.lua us|eu|jp|beta
-- Mesen 2's Lua setInput reads its numbers from the end: setInput(input, 0, port, subport); port 1 = SNES port 2, subport 3 = pad D (game pad 5).
wait(600)
for i=1,240 do q[#q+1]=function() emu.setInput({r=true},0,1,3) end end
at(function() local u={} for a=0xCE0,0xCEF do u[#u+1]=string.format('%02x',emu.read(a,W)) end print('pads',table.concat(u,' '),'A4',string.format('%02x',emu.read(0xA4,W))) end)
wait(200) S('snd') at(function() print('A4',string.format('%02x',emu.read(0xA4,W))) end)
