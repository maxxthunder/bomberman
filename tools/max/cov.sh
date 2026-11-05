#!/bin/sh
# All coverage scenarios of cov.lua for one version: tools/max/cov.sh [VER]; CDLs land in $SCRATCH/max/cov_<scen>_<ver>/.
here=$(cd "$(dirname "$0")" && pwd); : "${SCRATCH:?set SCRATCH}"; S=$SCRATCH; v=${1:-blue}; mkdir -p "$S/max/_cov"
for s in idle sound battle pitch over play; do
  f="$S/max/_cov/cov_$s.lua"; { echo "SCEN='$s'"; cat "$here/cov.lua"; } > "$f"; sh "$here/run.sh" "$f" "$v" | grep -v '^wrote'
done
