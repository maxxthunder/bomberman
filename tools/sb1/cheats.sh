#!/bin/sh
# Run every cheats.lua test on one version: tools/sb1/cheats.sh <scratch dir> [us|eu|jp|beta] [test ...]
# (MESEN must point at a portable Mesen; output and screenshots go to the scratch dir)
here=$(cd "$(dirname "$0")" && pwd); d=$1; v=${2:-us}; shift 2
mkdir -p "$d"
for t in ${*:-none inv lives fire kit small nine snd stage map1 map2}; do
  mkdir -p "$d/$t"; { echo "TEST='$t'"; cat "$here/cheats.lua"; } > "$d/$t/c.lua"
  sh "$here/run.sh" "$d/$t/c.lua" "$v" | grep -v '^CDLHEX' | sed "s/^/$t: /"
done
