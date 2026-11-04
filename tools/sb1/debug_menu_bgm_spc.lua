-- BGM NO. on the debug menu: plays every track and dumps APU RAM 90 frames later (patched ROM; compare versions).
-- play every BGM number from the debug menu (A on BGM NO.), dump APU RAM 90 frames later
wait(700) press({start=true},4) wait(60) press({start=true},4) wait(700)
press({select=true},2) wait(4) press({up=true},2) press({up=true},2)
for n=0,41 do
  if n>0 then press({right=true},2) end
  press({a=true},2) wait(90)
  at(function() local t={} for a=0,0xFFFF do t[#t+1]=string.format('%02x',emu.read(a,emu.memType.spcRam)) end print('SPC '..n..' '..table.concat(t)) end)
end
