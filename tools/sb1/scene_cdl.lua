FROM=FROM or 0 TO=TO or 72 FR=FR or 450
-- visit every scene $00-$48 by writing the next-scene byte $00A4, mash inputs, dump the CDL
wait(900)
local keys={'up','down','left','right','a','b','start','y','x','l','r'}
for v=FROM,TO do
  at(function() emu.write(0xA4,v,W) end)
  for i=1,FR do local k=keys[(i*7+v)%#keys+1] if k=='start' and i%50~=0 then k='a' end q[#q+1]={[k]=(i%3~=0)} end
  at(function() print('scene',v,'now',emu.read(0xD10,W)) end)
end
cdl_dump('sweep')
