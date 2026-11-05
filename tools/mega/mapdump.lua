-- Dump VRAM, CRAM and the cell table pointer ($9E6C, 8 bytes = 4 name-table words per cell) in every tileset:
-- each area's hub and first stage, and the 10 battle stages. maps.py draws all 59 maps from these.
-- Files: OUT/<scene>.vram/.cram and OUT/scenes.txt (scene, $953A tileset, $953F map, $9E6C). USA addresses.
local sc=io.open(OUT.."scenes.txt",BATTLE_ONLY and "a" or "w")
local function dump(n)
  for _,dn in ipairs({"VRAM","CRAM"}) do
    local f=io.open(OUT..n.."."..dn:lower(),"wb") for a=0,memory.getmemorydomainsize(dn)-1 do f:write(string.char(memory.read_u8(a,dn))) end f:close()
  end
  sc:write(string.format("%s %d %X %X\n",n,r8(0x953A),r8(0x953F),memory.read_u32_be(0x9E6C,DOMAIN))) sc:flush() shot(n)
end
for ar,c in ipairs({"2200","4501","4502","6803","8114","0515"}) do
  if not BATTLE_ONLY then enter(c) wait(700) tap("Start") wait(600) if ar<6 then dump("hub"..ar) tap("A") wait(500) end dump("stage"..ar) end
end
for st=0,9 do
  savestate.load(STATES.."title_"..REG..".state") wait(30)
  tap("Down") tap("Start") wait(300)
  for i=1,3 do tap("Start") wait(200) end
  for k=1,st do tap("Right") end tap("Start") wait(200) tap("Start") wait(400) dump("battle"..st)
end
sc:close()
