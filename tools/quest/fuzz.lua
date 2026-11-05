-- Save-check fuzz: prepend IMGS = {'<488 hex digits>', ...} (244-byte cart RAM images). The title runs the load
-- ($00:0B28): at the CALL to the check (US $00:0B3B, Japan $00:0B48) a savestate is taken; each image is written over
-- the WRAM copy (US $CE72, Japan $CE71), the state reloaded, and the path taken recorded: the new-game template branch
-- (US $00:0B40, Japan $00:0B4D) = rejected, the other (US $00:0B4E, Japan $00:0B5B) = accepted. Prints RES <0/1 ...>.
local A = VER == 'jp' and {call=0x0B48, bad=0x0B4D, good=0x0B5B, copy=0xCE71} or {call=0x0B3B, bad=0x0B40, good=0x0B4E, copy=0xCE72}
local st, i, out = nil, 0, {}
local function nxt()
  i = i + 1
  if i > #IMGS then print('RES '..table.concat(out, ' ')) emu.stop(0) return end
  emu.loadSavestate(st)
  local h = IMGS[i]
  for k = 0, 243 do emu.write(A.copy + k, tonumber(h:sub(2 * k + 1, 2 * k + 2), 16), BUS) end
end
at(function()
  on_exec(0, A.call, function() if not st then st = emu.createSavestate() nxt() end end)
  on_exec(0, A.bad, function() if st then out[#out + 1] = '0' nxt() end end)
  on_exec(0, A.good, function() if st then out[#out + 1] = '1' nxt() end end)
end)
wait(3000)
