-- Type a password for real on the PASSWORD screen (Up raises the digit under the cursor, Right moves on), then Start.
function pw_type(s) for i=1,4 do local d=tonumber(s:sub(i,i)) for k=1,d do press({up=true},3) end if i<4 then press({right=true},3) end end press({start=true}) end
