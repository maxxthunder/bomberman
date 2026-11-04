-- Demo CD boot variants: LEFT=1 holds Left the whole time (Japanese title texts, read at demo $5640 after loading);
-- OLD=1 makes the System Card version check at $4014 see X=0 (the Super CD-ROM2 warning screen). Shots a-d.
if OLD then emu.addMemoryCallback(function() local s=emu.getState() if s['cpu.pc']==0x4014 then print('ver X='..s['cpu.x']) emu.setState({['cpu.x']=0}) end end, emu.callbackType.exec, 0x4014, 0x4014) end
local hold = LEFT and {left=true} or {}
for i=1,300 do q[#q+1]=hold end
for i=1,10 do q[#q+1]={run=true} end
for i=1,700 do q[#q+1]=hold end at(function() shot('a') end)
for i=1,300 do q[#q+1]=hold end at(function() shot('b') end)
for i=1,300 do q[#q+1]=hold end at(function() shot('c') end)
for i=1,600 do q[#q+1]=hold end at(function() shot('d') end)
