-- Save the states the other tests load (into STATES): title screen, password screen (taken during its fade-in;
-- lib.lua's try/enter wait it out), and a 2-player battle in progress (default Battle Game settings).
-- Run first: tools/mega/run.sh tools/mega/mkstates.lua us (and eu).
wait(1200) tap("Start") wait(500)
savestate.save(STATES.."title_"..REG..".state")
tap("Down") tap("Down") tap("Start") wait(200)
savestate.save(STATES.."password_"..REG..".state")
savestate.load(STATES.."title_"..REG..".state") wait(30)
tap("Down") tap("Start") wait(300)
for i=1,5 do tap("Start") wait(200) end
wait(600)
savestate.save(STATES.."battleplay_"..REG..".state") shot("battle")
