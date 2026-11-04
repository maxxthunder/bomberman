#!/bin/sh
# Run a Lua script in Mesen 2 headless with lib.lua prepended: tools/pce90/run.sh script.lua [us|jp]
# MESEN must point at a portable Mesen.exe (a copy with its own settings.json, so saves/states stay out of the user profile).
# Output (png/ram, printed lines) lands next to the script.
: "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms
case "${2:-us}" in us) r="(USA)";; jp) r="(Japan) (En)";; esac
d=$(dirname "$1"); cat "$here/lib.lua" "$1" > "$d/_full.lua"
python "$here/mesen.py" "$d/_full.lua" "$R/Bomberman $r.pce"
