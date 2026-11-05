#!/bin/sh
# All nes1 coverage runs (cov.lua), US then JP; CDLs land in $SCRATCH/cov_*_<reg>/*.cdlhex. MESEN, SCRATCH set.
here=$(cd "$(dirname "$0")" && pwd)
for reg in ${1:-us jp}; do
  for s in 1 9 17 25 33 41 49; do
    code=$(node -e "import('file:///$(cd "$here" && pwd -W)/password.mjs').then(P=>console.log(P.encode({stage:$s,fire:5,bombs:10,speed:1,wallPass:1,detonator:1,flamePass:1,reveal:1})))")
    printf 'MODE="all" NST=8 CODE1="%s"\n' "$code" > "$SCRATCH/cov_all$s.lua"; cat "$here/cov.lua" >> "$SCRATCH/cov_all$s.lua"
    sh "$here/run.sh" "$SCRATCH/cov_all$s.lua" $reg | grep -v '^wrote'
  done
  for m in over glitch; do
    printf 'MODE="%s" GLITCH={"BABABAHIHABABABABABF","BAJDIHABAHIHIHIHIDJL","BANMKGCPCGKGKGKGKBAL","BACPIHABAHIHIHIHIDJL","BAKGDJNMNJDJDJDJDABH","BAJDIHABAHIHIHIHIFEF","BALOEFLOLFEFEFEFEOLA"}\n' $m > "$SCRATCH/cov_$m.lua"; cat "$here/cov.lua" >> "$SCRATCH/cov_$m.lua"
    sh "$here/run.sh" "$SCRATCH/cov_$m.lua" $reg | grep -v '^wrote'
  done
done
