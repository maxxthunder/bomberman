-- Dump VRAM/CRAM/VSRAM and the screen at the splash screen (boot + WAIT frames) for tools/mega8/logo.py.
wait(WAIT or 120)
for _,dname in ipairs({"VRAM","CRAM","VSRAM"}) do
  local f=io.open(OUT..dname..".bin","wb") local n=memory.getmemorydomainsize(dname)
  for a=0,n-1 do f:write(string.char(memory.read_u8(a,dname))) end f:close()
end
shot("splash")
