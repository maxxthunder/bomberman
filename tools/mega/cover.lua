-- Routine coverage: dofile or prepend this to a run.sh body (after lib.lua).
-- CAND = file of hex addresses (callgraph.py entries that are not plain branch targets + gap-run starts);
-- HITS = file the hit addresses are appended to. Each candidate gets an exec callback until it first runs, then it
-- is dropped (BizHawk checks every callback on every instruction, ~0.2 ms per callback per frame), so runs get
-- faster as coverage grows. cov_off()/cov_on() pause it over screens already covered. Hits persist across runs.
local hit, ids, cand, done = {}, {}, {}, {}
local hf
function cov_load(candf, hitsf)
  for l in io.lines(hitsf) do local a=tonumber(l:match("%x+"),16) if a then done[a]=true end end
  for l in io.lines(candf) do local a=tonumber(l,16) if a and not done[a] then cand[#cand+1]=a end end
  hf=io.open(hitsf,"a") log("coverage: "..#cand.." candidates not yet hit")
end
function cov_on()
  for _,a in ipairs(cand) do if not done[a] and not ids[a] then
    ids[a]=event.onmemoryexecute(function() hit[a]=true end,a,"cov","M68K BUS") end end
end
function cov_tick()
  for a,_ in pairs(hit) do
    if ids[a] then event.unregisterbyid(ids[a]) ids[a]=nil end
    if not done[a] then done[a]=true hf:write(string.format("%x %s\n",a,COV_TAG or "")) end
  end
  hit={} hf:flush()
end
function cov_off() cov_tick() for a,id in pairs(ids) do event.unregisterbyid(id) end ids={} end
local fa=emu.frameadvance
emu.frameadvance=function() fa() cov_tick() end
