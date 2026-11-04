-- Shared helpers for Mega Bomberman tests (prepended by run.sh after bizhawk.py's prelude).
-- RAM (68K RAM domain offsets, CPU $FF0000+): $9564-$9567 password digits (screen left..right = ones..thousands),
-- $9568 cursor, $956C ok flag, $956D bad flag, $953A world, $953B top world, $953C stage, $953D stage-clear nibbles.
DOMAIN="68K RAM"
STATES=STATES or "D:/tmp/bomberman/mega/"  -- run.sh sets it from $SCRATCH
client.speedmode(6400)
function tap(b,n) press({[b]=true},n or 3) end
function w8(a,v) memory.write_u8(a,v,DOMAIN) end
-- Try a password (string as shown on screen, left to right) from the password-screen state; returns ok, top world, $953D.
function try(code)
  savestate.load(STATES.."password_"..REG..".state")
  while r8(0xA3FC)~=0 do emu.frameadvance() end      -- the state is saved during the fade-in; input is ignored until it ends
  for i=1,4 do w8(0x9563+i, tonumber(code:sub(i,i))) end
  joypad.set({["P1 Start"]=true}) emu.frameadvance() emu.frameadvance()
  for i=1,20 do if r8(0x956C)~=0 or r8(0x956D)~=0 then break end emu.frameadvance() end
  return r8(0x956C)==1, r8(0x953B), r8(0x953D)
end
-- Enter a password with real button presses (Up per digit step, Right to the next digit) and press Start.
function enter(code)
  savestate.load(STATES.."password_"..REG..".state")
  while r8(0xA3FC)~=0 do emu.frameadvance() end
  for i=1,4 do for k=1,tonumber(code:sub(i,i)) do tap("Up") end if i<4 then tap("Right") end end
  tap("Start")
  return r8(0x956C)==1
end
