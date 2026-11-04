-- Type a character password on the Config Battle password screen with real button presses.
-- The grid (cursor starts on A): row 0 ABCDEFGHJKLMN, row 1 PQRTUVWXY, row 2 1234567890 + back + OK.
GRID={"ABCDEFGHJKLMN","PQRTUVWXY","1234567890"}
function typecode(s)
  local r,c=0,0
  local function go(R,C)
    for i=1,c do press({left=true},2) wait(6) end
    for i=r+1,R do press({down=true},2) wait(6) end
    for i=R+1,r do press({up=true},2) wait(6) end
    for i=1,C do press({right=true},2) wait(6) end
    r,c=R,C
  end
  for i=1,#s do
    local ch=s:sub(i,i)
    for R=1,3 do local C=GRID[R]:find(ch,1,true) if C then go(R-1,C-1) break end end
    press({a=true},2) wait(10)
  end
  go(2,11) press({a=true},2)
end
