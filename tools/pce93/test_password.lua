-- Type one password with real presses and follow it into the stage (run by test_passwords.sh, which sets VER, TAG, END, CODE).
-- Prints the decoded state after END and in the stage, and how far the player sprite moves in 12 frames of Down.
local A0=(VER=='sp') and {0x388c,0x388d,0x388e,0x388f,0x3891,0x38a6,0x3898} or {0x3895,0x3896,0x3897,0x3898,0x389a,0x38af,0x38a1}
local function st(tag) at(function() local t={} for _,a in ipairs(A0) do t[#t+1]=string.format('%02x',r(a)) end
  print(tag..' world,stage,bombs,fire,speed,cleared,state: '..table.concat(t,' ')..string.format(' p9b=%02x pa0=%02x',r(0x209b),r(0x20a0))) end) end
local function sat() local t={} for n=0,63 do t[n]=emu.read(n*8,emu.memType.pceSpriteRam)|(emu.read(n*8+1,emu.memType.pceSpriteRam)<<8) end return t end
if VER=='sp' then sp_password() else to_password() end
type_pw(CODE) S(TAG..'_a') submit(END) wait(30) st(TAG..' after END') wait(400) S(TAG..'_b')
for i=1,6 do press({run=true}) wait(150) end wait(100) S(TAG..'_c') st(TAG..' in game')
local A at(function() A=sat() end) for i=1,12 do q[#q+1]={down=true} end
at(function() local B=sat() local bd=0 for k=0,63 do local d=math.abs(B[k]-A[k]) if d>bd and d<100 then bd=d end end print(TAG..' moved '..bd..' px in 12 frames of Down') end)
