-- Draw every frame of a player sprite set, the way the animation ticker $1336 does it: write the frame number to
-- the sprite object's +4 and set +5 bit 4, which makes the sprite builder ($A1E) DMA that frame's tiles. +5 bits 0-2
-- pick the set: slot n's frame/DMA tables are at RAM $8A74+8n (0 = $EB6B4/$ECBC0, 1 = $EC250/$EE6C8,
-- 2 = $EDC6C/$EFA92, 3 = $EF17E/$F0D76; all four are loaded in battle). Uses player 1's sprite in a battle.
SLOTS=SLOTS or {{0,184},{1,108},{2,173},{3,102}}
savestate.load(STATES.."battleplay_"..REG..".state")
local spr=memory.read_u32_be(0xA43C,DOMAIN) & 0xFFFF
for _,s in ipairs(SLOTS) do
  for f=1,s[2] do
    w8(spr+4,f) w8(spr+5,(r8(spr+5)&0xF8)|s[1]|0x10)
    for k=1,3 do emu.frameadvance() end
    shot(string.format("s%d_%02X",s[1],f))
  end
end
