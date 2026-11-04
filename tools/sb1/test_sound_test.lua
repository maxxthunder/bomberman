-- injects pad-5 R (+ multitap ID) at the title check $C5:4F52 -> sound test ($A4=$3C)
wait(600)
at(function() emu.addMemoryCallback(function() emu.write(0xCEF,1,W) emu.write(0xCE9,0x10,W) end, emu.callbackType.exec, 0xC54F52, 0xC54F52) end)
wait(100) S('s') at(function() print('A4',string.format('%02x',emu.read(0xA4,W))) end) wait(200) S('s2')
