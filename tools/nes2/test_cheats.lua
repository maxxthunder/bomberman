-- Cheat check in Mesen 2's cheat engine. Set TEST first: 'inv' (RAM 04E6:01), 'gg' (Game Genie AVZGKT + AVGGKT, JP ATPGET + ATLGET),
-- 'lives' (04E5:02), 'clear' (US 00B7:F0, JP 00A9:F0) or 'none'. NORMAL MODE from the menu, a random bot for FR
-- frames; deaths counted on the rising edge of the dying flag (US $A5, JP $97); lives $04E5 and stage read back.
local function add(c, t) local ok, e = pcall(emu.addCheat, t or emu.cheatType.nesCustom, c) print('cheat', c, ok, e) end
local J = REG == 'jp'
local DY, AR, ST = J and 0x97 or 0xA5, J and 0x3D or 0x4B, J and 0x3E or 0x4C
local deaths, dying, changes, last = 0, 0, 0, nil
emu.addEventCallback(function()
  local d = rd(DY) if d ~= 0 and dying == 0 then deaths = deaths + 1 end dying = d
  local s = rd(AR) * 8 + rd(ST) if last and s ~= last then changes = changes + 1 end last = s
end, emu.eventType.endFrame)
if TEST == 'inv' then add('04E6:01') end
if TEST == 'gg' then for _, c in ipairs(J and {'ATPGET', 'ATLGET'} or {'AVZGKT', 'AVGGKT'}) do add(c, emu.cheatType.nesGameGenie) end end
if TEST == 'lives' then add('04E5:02') end
if TEST == 'clear' then add(J and '00A9:F0' or '00B7:F0') end
to_menu() press({start=true}) wait(200)
if TEST == 'clear' then wait(FR or 8000) else bot(FR or 12000, 11) end
S(TEST..'_'..REG) at(function() print(TEST, 'deaths', deaths, 'lives', rd(0x4E5), 'area', rd(AR) + 1, 'stage', rd(ST) + 1, 'stage changes', changes) end)
