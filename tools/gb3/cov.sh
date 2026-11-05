#!/bin/sh
# All coverage scenarios of cov.lua: tools/gb3/cov.sh; CDLs land in $SCRATCH/gb3/cov_<scen>_jp/.
here=$(cd "$(dirname "$0")" && pwd); S=${SCRATCH:-/d/tmp/bomberman/gb}; mkdir -p "$S/gb3/_cov"
for s in idle story champ boss all0 all1 all2 over; do
  f="$S/gb3/_cov/cov_$s.lua"; { echo "SCEN='$s'"; cat "$here/cov.lua"; } > "$f"; sh "$here/run.sh" "$f" jp | grep -v '^wrote'
done
