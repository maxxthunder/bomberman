#!/bin/sh
# Run a Lua script in Mesen 2 headless with lib.lua prepended: tools/pceub/run.sh script.lua [rom]
# MESEN must point at a portable Mesen.exe (a copy with its own settings.json, so saves/states stay out of the user profile).
# rom defaults to Users Battle; "pce90" runs the 1990 JP card. Output (png/ram, printed lines) lands next to the script.
: "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms
case "${2:-ub}" in ub) r="Bomberman - Users Battle (Japan).pce";; pce90) r="Bomberman (Japan) (En).pce";; esac
d=$(dirname "$1"); cat "$here/lib.lua" "$1" > "$d/_full.lua"
python "$here/mesen.py" "$d/_full.lua" "$R/$r"
