-- Dump the title screen for logo.py: <name>_vram.bin (64 KB), _pal.bin (VCE, 512 words), _spr.bin (SAT) and a shot.
-- card: 800 frames, Run (skips the intro), 160 frames = the logo over the planets, before the menu text appears.
-- demo: Run at the System Card screen, then wait for the Special Version title (LEFT=1: the Japanese one): the first
-- frame with 20+ sprites in the SAT (the logo is sprites over the BG picture; CD timing varies between runs), +90.
local function vd(n) dump(n..'_vram', emu.memType.pceVideoRam) dump(n..'_pal', emu.memType.pcePaletteRam) dump(n..'_spr', emu.memType.pceSpriteRam) shot(n) end
if GAME=='card' then
  wait(800) press({run=true}) wait(150) at(function() vd('card') end)
else
  local hold = LEFT and {left=true} or {}
  for i=1,300 do q[#q+1]=hold end for i=1,10 do q[#q+1]={run=true} end local function nspr() local n=0 for k=0,63 do local y=emu.read(8*k,emu.memType.pceSpriteRam)|emu.read(8*k+1,emu.memType.pceSpriteRam)<<8 if (y&0x3FF)>=64 and (y&0x3FF)<304 then n=n+1 end end return n end
  local function poll() if nspr()>=20 then wait(90) at(function() vd(LEFT and 'demojp' or 'demo') end) else q[#q+1]=hold at(poll) end end
  for i=1,600 do q[#q+1]=hold end at(poll)
end
