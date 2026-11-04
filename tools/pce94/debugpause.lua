-- Restore the cut debug pause menu and use it. What is left in the ROM: the menu handler at bank $09 $135C4
-- (logical $B5C4 with banks $08/$09 at $8000-$BFFF), its sub-screens ($B633 enemy editor, $B6EB / $B731 value
-- editors, reached through the hook wrappers $D8D0 / $D8E7 / $D8FE), the value printer $B511 and the menu text at
-- $D844 (ROM $3844). Missing: the wrapper that calls $B5C4 and the code that prints $D844. Both editors return to
-- hook $D89C, so the menu sat where the normal paused handler is now. This script patches ROM in memory:
--   $DF66 (free $FF bytes in bank $01): BIT #$08 / BEQ / JMP $D8A2 (Run = unpause) / far call $08:$B5C4 / LDA #1 / RTS
--   $DF82: print $D844 with $C9FB, far call $08:$B511, hook = $DF66, LDA #1 / RTS
--   $D891 (end of the pause slide-in) -> JMP $DF82; $D89C (paused handler) -> JMP $DF66
-- Then it starts area 1 with 2200, pauses and drives the menu. INV_MODE = $3709 bit 1 (the death check at $DA5A
-- skips while $3709 != 0); MAP_CLEAR sets $B8 bit 5.
function pw_type(s)
  for i=1,4 do local d=tonumber(s:sub(i,i))
    if d<=5 then for k=1,d do press({up=true},3) end else for k=d,9 do press({down=true},3) end end
    if i<4 then press({right=true},3) end end
  press({i=true})
end
local function patch(off, hex) local i=0 for b in hex:gmatch('%x%x') do emu.write(off+i, tonumber(b,16), emu.memType.pcePrgRom) i=i+1 end end
patch(0x3F66, '8908F0034CA2D8858DA908858CA9C48567A9B5856820EAEEA90160')
patch(0x3F82, 'A9448508A9D8850920FBC9A908858CA9118567A9B5856820EAEEA9668523A9DF8524A90160')
patch(0x3891, '4C82DF') patch(0x389C, '4C66DF')
local function st(t) print(string.format('%s hook=%02X%02X 3709=%02X 3BFF=%02X B8=%02X lives=%d', t, r8(0x2024), r8(0x2023), r8(0x3709), r8(0x3BFF), r8(0x20B8), r8(0x3704))) end
loadfile('pw.mst') wait(4) pw_type(CODE or '2200') wait(430)
for k=1,14 do press({run=true}) wait(24) end
wait(150) press({run=true}) wait(60)
-- FONT=1: copy the ASCII font tiles ($100 + code, saved from the title screen by fontdump.lua) into VRAM so the
-- menu text is legible (the stage keeps only the HUD digits there); for the screenshots only.
if FONT then at(function() local f=io.open(STATES..'font.bin','rb') local s=f:read('a') f:close()
  for c=0x3B,0x5F do if c==0x3B or c==0x3E or c>=0x41 then for k=0,31 do emu.write(0x2000+c*32+k, s:byte(c*32+k+1), emu.memType.pceVideoRam) end end end end) wait(2) end
at(function() shot('m0') st('menu') end)
press({i=true}) wait(10) at(function() shot('m1_inv') st('I on INV_MODE') end)
press({i=true}) wait(10) press({i=true}) wait(10) at(function() st('I twice more') end)
press({right=true}) wait(10) at(function() shot('m2_enemy') st('Right') end)
press({up=true}) wait(10) press({up=true}) wait(10) at(function() shot('m3_enemy_up') st('Up x2') end)
press({left=true}) wait(10) at(function() shot('m4_back') st('Left') end)
press({run=true}) wait(60) at(function() shot('m5_unpaused') st('Run') end)
-- invincibility check: drop a bomb, stand on it
press({i=true}) wait(300) at(function() shot('m6_bomb') st('after bomb') end)
press({run=true}) wait(60) press({down=true}) wait(10) press({i=true}) wait(30) at(function() shot('m7_mapclear') st('MAP_CLEAR') end)
wait(400) at(function() shot('m8_after') st('after') end)
