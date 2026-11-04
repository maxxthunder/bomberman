#!/bin/sh
# Fuzz the character-password checker against the game's own decoder in Mesen.
# Usage: tools/sb5/fuzz.sh <workdir> [caravan]   -> prints accepted/rejected/mismatch counts
#   CASES="CODE1 CODE2 ..." tests just those codes instead of the generated set
# Each case: load a savestate on the password screen, write the 6 symbols into the entry buffer,
# press A on the OK key, and read the accept flag and the decoded fields 40 frames later.
here=$(cd "$(dirname "$0")" && pwd); d=$1; mkdir -p "$d"
off=0; [ "$2" = caravan ] && off=31   # the Caravan build keeps the editor block $1F bytes higher
if [ -n "$CASES" ]; then printf "%s
" $CASES > "$d/cases.txt"; else python "$here/fuzzcases.py" "$d/cases.txt" ${N:+$N}; fi
{
  cat "$here/lib.lua"
  echo "OFF=$off"
  echo 'function inj(s) for i=1,6 do wr(0x62F1+OFF+i, A:find(s:sub(i,i),1,true)-1) end end'
  echo 'to_config_pw() save()'
  echo 'codes={'; sed 's/.*/"&",/' "$d/cases.txt"; echo '}'
  cat <<'L'
for _,c in ipairs(codes) do
  load(function() inj(c) end) press({a=true}) wait(40)
  at(function() local t={} for a=0x62DE,0x62F1 do if a<0x62E0 or a>0x62E5 then t[#t+1]=rd(a+OFF) end end print('F',c,rd(0x62F8+OFF),table.concat(t,',')) end)
end
L
} > "$d/fuzz.lua"
"$here/run.sh" "$d/fuzz.lua" $2 > "$d/fuzz.out"
python - "$d/fuzz.out" "$here" <<'P'
import sys; sys.path.insert(0, sys.argv[2])
from password import decode
acc = rej = 0; bad = []
for l in open(sys.argv[1]):
    if not l.startswith("F"): continue
    _, c, flag, st = l.split()
    game = flag == "1"; d = decode(c); acc += game; rej += not game
    if (d is not None) != game: bad.append(c); continue
    if game:
        v = list(map(int, st.split(",")))
        if dict(body=v[0], color=v[1], bomb=v[2], fire=v[3], speed=v[4], items=sum(v[5 + i] << i for i in range(9))) != d: bad.append(c)
print("cases", acc + rej, "accepted", acc, "rejected", rej, "mismatches", len(bad), bad[:10])
P
