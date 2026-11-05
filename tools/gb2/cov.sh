#!/bin/sh
# All coverage scenarios of cov.lua for one version: tools/gb2/cov.sh [jp|us]; CDLs land in $SCRATCH/gb2/cov_<scen>_<ver>/.
here=$(cd "$(dirname "$0")" && pwd); v=${1:-jp}; S=${SCRATCH:-/d/tmp/bomberman/gb}; mkdir -p "$S/gb2/_cov_$v"
for s in idle lesson snd battle power allA allB over; do
  f="$S/gb2/_cov_$v/cov_$s.lua"; { echo "SCEN='$s'"; cat "$here/cov.lua"; } > "$f"; sh "$here/run.sh" "$f" "$v" | grep -v '^wrote'
done
