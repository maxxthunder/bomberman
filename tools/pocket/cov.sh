#!/bin/sh
# All coverage scenarios of cov.lua: tools/pocket/cov.sh; CDLs land in $SCRATCH/pocket/cov_<scen>_us/.
here=$(cd "$(dirname "$0")" && pwd); S=${SCRATCH:?set SCRATCH to a scratch folder}; mkdir -p "$S/pocket/_cov"
codes=$(cd "$here" && node --input-type=module -e "import {TABLE} from './password.mjs'; console.log(TABLE.join(' '))")
for s in idle new jump over ending $(for c in $codes; do echo s$c; done); do
  f="$S/pocket/_cov/cov_$s.lua"; { echo "SCEN='$s'"; cat "$here/cov.lua"; } > "$f"; sh "$here/run.sh" "$f" | grep -v '^wrote'
done
