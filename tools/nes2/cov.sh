#!/bin/sh
# All nes2 coverage runs (cov.lua) for one region (default us); CDLs land in $SCRATCH/cov_*_<reg>/*.cdlhex. MESEN, SCRATCH set.
here=$(cd "$(dirname "$0")" && pwd); reg=${1:-us}
for a in 1 2 3 4 5 6; do
  code=$(node -e "import('file:///$(cd "$here" && pwd -W)/password.mjs').then(P=>console.log(P.encode({area:$a,stage:1,bombs:8,fire:5,key:3},'$reg')))")
  printf 'MODE="all" NST=8 CODE1="%s"\n' "$code" > "$SCRATCH/cov_all$a.lua"; cat "$here/cov.lua" >> "$SCRATCH/cov_all$a.lua"
  sh "$here/run.sh" "$SCRATCH/cov_all$a.lua" $reg | grep -v '^wrote'
done
sec=$(node -e "import('file:///$(cd "$here" && pwd -W)/password.mjs').then(P=>console.log(P.SECRETS.map(s=>'\"'+P.secretCode(s[2],'$reg')+'\"').join(',')))")
for m in over vs battle secret; do
  printf 'MODE="%s" CODES={%s}\n' $m "$sec" > "$SCRATCH/cov_$m.lua"; cat "$here/cov.lua" >> "$SCRATCH/cov_$m.lua"
  sh "$here/run.sh" "$SCRATCH/cov_$m.lua" $reg | grep -v '^wrote'
done
