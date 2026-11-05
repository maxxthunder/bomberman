-- Shop VRAM dump for items.py: tools/gb3/run.sh tools/gb3/items.lua (prepend CODE = '39C6418', Wood 6). Invincible and
-- stage end forced until the shop ($0A:7557, reached after an area's 6th stage) starts, then plain; vdump every 240 frames.
CODE = CODE or '39C6418'
local shop = false
at(function() emu.addCheat(emu.cheatType.gbGameShark, '0101BCC1') emu.addCheat(emu.cheatType.gbGameShark, '01FF80C4')
  on_exec(0x0A, 0x7557, function() if not shop then shop = FRAME print('shop at', FRAME) emu.clearCheats() end end) end)
start_game(CODE)
for k=1,40 do wait(60) at(function() if shop then shot('s'..k) if k%4==0 then vdump('v'..k) end end end) if k>20 and k%3==0 then press({a=true}) end end
