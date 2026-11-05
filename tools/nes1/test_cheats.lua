-- Cheat check in Mesen 2's cheat engine. Set TEST first: 'inv' (RAM 007A:FF), 'gg' (Game Genie OXTKPV + OZTSYE, JP OXTGPV + OZTIYE),
-- 'lives' (0068:02), 'clear' (005E:01) or 'none'. inv/gg/lives/none: new game (START), a random bot for FR frames,
-- deaths counted ($5C rising), lives $68 read back. clear: new game, no input; stage changes ($58) counted.
local function add(c, t) local ok, e = pcall(emu.addCheat, t or emu.cheatType.nesCustom, c) print('cheat', c, ok, e) end
local deaths, dying, clears, st = 0, 0, 0, nil
emu.addEventCallback(function()
  local d = rd(0x5C) if d ~= 0 and dying == 0 then deaths = deaths + 1 end dying = d
  local s = rd(0x58) if st and s ~= st then clears = clears + 1 end st = s
end, emu.eventType.endFrame)
if TEST == 'inv' then add('007A:FF') end
if TEST == 'gg' then for _, c in ipairs(REG == 'jp' and {'OXTGPV', 'OZTIYE'} or {'OXTKPV', 'OZTSYE'}) do add(c, emu.cheatType.nesGameGenie) end end
if TEST == 'lives' then add('0068:02') end
if TEST == 'clear' then add('005E:01') end
wait(200) press({start=true}) wait(300)
if TEST == 'clear' then wait(FR or 6000) else bot(FR or 12000, 11) end
S(TEST..'_'..REG) at(function() print(TEST, 'deaths', deaths, 'lives', rd(0x68), 'stage', rd(0x58), 'stage changes', clears) end)
