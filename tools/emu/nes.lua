-- NES prelude: mesen.py adds it after its own for a .nes/.fds ROM. dump = the 2 KB of CPU RAM; an at() function may
-- return the input to hold (else the last input stays).
KEEP=true
function dump(name) local t={} for a=0,0x7FF do t[#t+1]=string.format('%02x',emu.read(a,emu.memType.nesInternalRam)) end print('DUMP '..name..' '..table.concat(t)) end
