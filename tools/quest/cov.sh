#!/bin/sh
# All coverage scenarios of cov.lua plus the CDLs of the test runs: tools/quest/cov.sh [us|jp]; CDLs land in
# $SCRATCH/quest/_cov/cov_<scen>_<ver>/.
here=$(cd "$(dirname "$0")" && pwd); S=${SCRATCH:?set SCRATCH to a scratch folder}/quest/_cov; mkdir -p "$S"; v=${1:-us}
for s in idle battle new debug test; do
  f="$S/cov_$s.lua"; { echo "SCEN='$s'"; cat "$here/cov.lua"; } > "$f"; OUT=$S/cov_${s}_$v sh "$here/run.sh" "$f" $v | grep -v '^wrote'
done
