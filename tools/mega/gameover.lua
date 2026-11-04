-- Encoder check: for each password, enter it, start the area (shot CODE_intro), dismiss the intro with A, set lives
-- ($9543) to 0 and drop bombs at Bomberman's feet until he dies into game over; log the password the continue screen
-- shows ($1BA3C writes it to $AED6-$AED9, leftmost digit first).
CODES=CODES or {"2200","5120","7420","7340","2730","1510","1051","3351","7791","0059","4128","9723","5653","0515"}
for _,c in ipairs(CODES) do
  enter(c) wait(700) tap("Start") wait(400) shot(c.."_intro") tap("A") wait(200)
  w8(0xAED6,0) w8(0xAED7,0) w8(0xAED8,0) w8(0xAED9,0)
  for k=1,3000 do
    w8(0x9543,0)
    local b=({"A","B","C"})[(k//40)%3+1]
    if k%40<3 then joypad.set({["P1 "..b]=true}) end
    emu.frameadvance()
    if k%30==0 and r8(0xAED6)+r8(0xAED7)+r8(0xAED8)+r8(0xAED9)>0 then break end
  end
  wait(200) shot(c.."_over")
  log(c.." -> "..r8(0xAED6)..r8(0xAED7)..r8(0xAED8)..r8(0xAED9))
end
