-- Password entry behaviour: starting digits/cursor, Up/Down wrap, Left/Right wrap, which digit is on the left.
local function st(t) log(string.format("%-22s digits %d%d%d%d cursor %d", t, r8(0x9564),r8(0x9565),r8(0x9566),r8(0x9567), r8(0x9568))) end
savestate.load(STATES.."password_"..REG..".state")
while r8(0xA3FC)~=0 do emu.frameadvance() end
st("start") shot("start")
tap("Down") st("Down")
tap("Up") tap("Up") st("Up Up")
tap("Left") st("Left (from 0)")
tap("Up") tap("Up") tap("Up") st("Up x3")
tap("Right") st("Right (from 3)")
tap("Right") tap("Up") tap("Up") tap("Up") tap("Up") tap("Up") st("Right, Up x5")
shot("typed")
-- hold Up: auto-repeat?
press({Up=true},60) st("Up held 60 frames")
