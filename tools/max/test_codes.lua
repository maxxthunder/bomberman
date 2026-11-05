-- Button codes in every version: tools/max/run.sh tools/max/test_codes.lua VER.
-- 1) Title menu: the sound-test sequence ($01:5F7E, table $01:5FCD in Blue), then A: shot snd_<ver>.
-- 2) New game, 1-01: hold A+B+Select+Start ($00:0335): the boot sequence runs again (soft reset); shot rst_<ver>.
local mode = {}
at(function() emu.addMemoryCallback(function(a, v) mode[#mode + 1] = v end, emu.callbackType.write, 0xC187, 0xC187, emu.cpuType.gameboy, BUS) end)
to_title()
for _, d in ipairs({'right','left','right','right','left','left','right','left','right','left','left','right'}) do local b = {} b[d] = true press(b, 3) end
wait(30) press({a=true}) wait(120) at(function() shot('snd_'..VER) end)
press({b=true}) wait(300)
at(function() mode = {} end)
start_new() wait(60) at(function() shot('pre_'..VER) end)
hold({a=true, b=true, select=true, start=true}, 10) wait(200)
at(function() shot('rst_'..VER) print(VER, 'C187 writes after the combo', table.concat(mode, ',')) end)
