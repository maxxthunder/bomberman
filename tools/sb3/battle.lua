-- after a battle-mode password: walk SELECT MATCH -> PLAYER -> GAMEPLAY -> 5x COUNTRY -> SELECT STAGE (default settings)
function to_stage_select() wait(300) for i=1,9 do press({start=true}) wait(100) end end
function cycle_stages(n,tag) for i=1,n do at(function() print('STG', tag, i-1, r8(0x6C6E)) shot(tag..string.format('%02d',i-1)) end) press({right=true}) wait(40) end end
