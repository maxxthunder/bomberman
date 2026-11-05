-- Visit every room of the multi-room stages: start the stage from its password, play PLAY frames of random input in
-- each room, then send the game to the next room through its own room-change entry $9916 (the door object jumps
-- there from $C8D6) run in a live task. Needs rnd() from tour.lua. Logs $953E (room) and $953F (map) per room.
-- USA addresses.
local STAGES={{"5120",2},{"8111",2},{"7421",2},{"1051",2},{"8112",2},{"7422",3},{"1052",2},{"6803",2},{"0513",3},
  {"9723",2},{"3353",2},{"2814",2},{"1134",3},{"5654",3},{"0515",6}}
local function task(i) return memory.read_u32_be(0x62E+4*i,"M68K BUS") & 0xFFFF end
local function live()
  if memory.read_u32_be(task(2)+4,DOMAIN)~=0x1C96 then return end
  for i=0x1F,4,-1 do if memory.read_u32_be(task(i)+4,DOMAIN)~=0 then return i end end
end
for _,s in ipairs(STAGES) do
  if COVER then cov_off() end
  enter(s[1]) wait(700) tap("Start") wait(600)
  if s[1]~="0515" then tap("A") end
  for k=1,1500 do if live() then break end emu.frameadvance() end
  for r=1,s[2] do
    wait(60) log(string.format("%s room %d: 953E=%d 953F=%X",s[1],r,r8(0x953E),r8(0x953F))) shot(s[1].."_r"..r)
    if COVER then cov_on() end
    rnd(PLAY or 200)
    if COVER then cov_off() end
    if r<s[2] then
      local i=live() if not i then log("no task") break end
      local m=r8(0x953F) memory.write_u32_be(task(i)+4,0x9916,DOMAIN)
      for k=1,2000 do if r8(0x953F)~=m and live() then break end emu.frameadvance() end
    end
  end
end
