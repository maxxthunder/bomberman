-- Try passwords FROM..TO through the game's own checker ($1BE32); write "code topworld $953D" for the accepted ones.
FROM=FROM or 0 TO=TO or 9999
local f=io.open(OUT.."valid.txt","w") local t=os.clock()
for n=FROM,TO do
  local s=string.format("%04d",n)
  local ok,w,d=try(s)
  if ok then f:write(string.format("%s %d %02X\n",s,w,d)) f:flush() end
end
f:close() log(string.format("%d-%d done in %.0fs",FROM,TO,os.clock()-t))
