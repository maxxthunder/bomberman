#!/bin/sh
# Run a Lua test in a portable Mesen 2 on any ROM, with that game's lib.lua:
#   tools/pcevc/run.sh <pce90|pce93|pce94> "<file name in roms/>" script.lua [VAR=value ...]
# Needs MESEN = portable Mesen.exe (settings.json beside it). Output (png, ram, log) goes to $OUT
# (default $SCRATCH/<script name>; set SCRATCH to a scratch folder). pce94: STATES (= the output folder) and GAME
# are set here; its savestates need "AllowIoOsAccess": true in the portable settings.json.
here=$(cd "$(dirname "$0")" && pwd); T=$here/..; g=$1; f=$2; s=$3; shift 3
: "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
rom=$(cd "$T/../roms" && pwd -W)/$f
n=$(basename "$s" .lua); d=${OUT:-${SCRATCH:?set SCRATCH or OUT}/$n}; mkdir -p "$d"; d=$(cd "$d" && pwd -W)
if [ "$g" = pce94 ]; then o=$d
  { echo "STATES=\"$(cd "$d" && pwd -W)/\""; echo 'GAME="card"'; for v in "$@"; do echo "$v"; done; cat "$T/pce94/lib.lua" "$s"; } > "$o/body.lua"
  python "$T/emu/mesen.py" "$o/body.lua" "$rom" "$o"
else { for v in "$@"; do echo "$v"; done; cat "$T/$g/lib.lua" "$s"; } > "$d/_full_$n.lua"
  python "$T/emu/mesen.py" "$d/_full_$n.lua" "$rom"; fi
