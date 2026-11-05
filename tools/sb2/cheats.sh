#!/bin/sh
# Run every cheats.lua test: tools/sb2/cheats.sh <scratch dir> <rom.sfc> [test ...]   (MESEN = portable Mesen)
here=$(cd "$(dirname "$0")" && pwd); d=$1; rom=$2; shift 2
for t in ${*:-none inv kit stages jump sudden}; do
  mkdir -p "$d/$t"; cp "$here/cheats.lua" "$d/$t/c.lua"
  python "$here/run.py" "$d/$t/c.lua" "$rom" "TEST='$t'" | sed "s/^/$t: /"
done
