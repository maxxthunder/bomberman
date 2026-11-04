-- From the title-screen state, dump VRAM/CRAM/VSRAM and the screen for the logo rip (tools/mega/logo.py).
savestate.load(STATES.."title_"..REG..".state") wait(WAIT or 60)
log(table.concat(memory.getmemorydomainlist(),","))
for _,dname in ipairs({"VRAM","CRAM","VSRAM"}) do
  local f=io.open(OUT..dname..".bin","wb") local n=memory.getmemorydomainsize(dname)
  for a=0,n-1 do f:write(string.char(memory.read_u8(a,dname))) end f:close()
end
shot("title")
