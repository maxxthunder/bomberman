-- Enter each password by hand, screenshot the planet map, press Start and log the area/stage the game starts.
CODES=CODES or {"2200","6800","5120","7420","7340","2730","1510","4501","8111","7421","1051","3351","7791","4502","8112","7422","1052","3352","6803","0513","9723","3353","5653","8114","2814","1134","5654","7954","0515","0059","4128","1234"}
for _,c in ipairs(CODES) do
  local ok=enter(c) wait(700) shot(c.."_planet") tap("Start") wait(300) shot(c)
  log(string.format("%s ok=%s 953A=%d 953B=%d 953C=%d 953D=%02X",c,tostring(ok),r8(0x953A),r8(0x953B),r8(0x953C),r8(0x953D)))
end
