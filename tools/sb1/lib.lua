-- sb1 helpers, prepend to test scripts (see run.sh). emu.getCdlData is 0-based: CDL dumps start at ROM offset 0.
W=emu.memType.snesWorkRam
function S(n) at(function() shot(n) end) end
function D(n) at(function() dump(n) end) end
function cdl_dump(n) at(function()
  local c=emu.getCdlData(emu.memType.snesPrgRom) local t={}
  for i=0,#c do t[#t+1]=string.format('%02x',c[i]) end print('CDLHEX '..(n or 'cdl')..' '..table.concat(t)) end) end
-- boot to the password screen (USA timing)
function to_password() wait(700) press({down=true},4) wait(30) press({down=true},4) wait(30) press({start=true},4) wait(120) end
