-- Special Select Room leftover ($01:A001, called from $00:EA43 only when mode $3380 = 0, $3384 = 0 and round $2849 != 8).
-- The title always sets $3380 = 1/2 and $2849 = 8, and $10 is only set by the dead attract-demo code in bank $0B, so the
-- room can't open in the shipped game. Here: patched-in password screen, MUVWLNPC (round 1), RAM $10 = DEMO, hundreds
-- digit $2001 = HI, END pressed with I, then HOLD (default Down+Run+Select+I+II) held from the next frame on.
DEMO = DEMO or 1 HI = HI or 3 HOLD = HOLD or {down=true, run=true, select=true, i=true, ii=true}
to_password()
at(function() emu.write(0x10, DEMO, W) emu.write(0x1, HI, W) end)
type_letters('MUVWLNPC') to_end()
for f=1,4 do q[#q+1]={i=true} end
for f=1,400 do q[#q+1]=HOLD end
at(function() print(string.format('ROOM demo=%d hi=%d mode=%d round=%d skate=%d', DEMO, HI, emu.read(0x1380,W), emu.read(0x849,W), emu.read(0x84D,W))) end)
S(SHOT or 'room')
