#!/bin/sh
# All coverage scenarios of cov.lua for one version: tools/gb1/cov.sh [jp|wario]; CDLs land in $SCRATCH/gb1/cov_<scen>[_w]_<ver>/.
here=$(cd "$(dirname "$0")" && pwd); v=${1:-jp}; S=${SCRATCH:-/d/tmp/bomberman/gb}; mkdir -p "$S/gb1/_cov_$v"
for s in idle pw battle all; do for p in b w; do
  [ "$p" = w ] && [ "$v" != wario ] && continue
  f="$S/gb1/_cov_$v/cov_${s}_$p.lua"; { echo "SCEN='$s' P='$p'"; cat "$here/cov.lua"; } > "$f"; sh "$here/run.sh" "$f" "$v" | grep -v '^wrote'
done; done
