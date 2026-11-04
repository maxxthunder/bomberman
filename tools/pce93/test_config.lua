-- CONFIGRATION screen. JP: $3FFB bit 0 (set by I+Run at the ending, JP bank 8 $8C85, US $8C7D; the soft-reset
-- code clears only $2200-$3FF9, $E043) makes the world-map state far-call bank 8 $8620, which shows the screen.
-- Here $3FFB is written directly, the game soft-reset with Select+Run, and a Normal Game started.
-- US: same steps; the screen never comes (the call and the check were removed). PATCH=1 restores the call in US.
CFG=CFG or 0x8620 NAME=NAME or 'config'   -- set PATCH=1 CFG=... NAME=... in a line before this file to change
local P=emu.memType.pcePrgRom
at(function()
  if PATCH then for a,v in pairs({[0x4432]=0x00,[0x4433]=0x20,[0x4434]=0xe7,[0x4435]=0xea,[0x4436]=0x20,[0x4437]=0x86,[0x4438]=0x08}) do emu.write(a,v,P) end end
  on_exec(CFG,8,function() print('CONFIG screen entered at frame',FRAME) after(90,function() shot(NAME) end) end) end)
wait(300) at(function() wr(0x3ffb,1) end) press({select=true,run=true},4) wait(300)
press({run=true}) wait(400) press({run=true}) for i=1,30 do wait(100) if i%3==0 then press({run=true}) end end
at(function() print('end, $3FFB =',r(0x3ffb)) end)
