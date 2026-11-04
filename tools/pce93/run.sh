#!/bin/sh
# Run a Lua test in Mesen 2 headless: tools/pce93/run.sh script.lua [us|jp|sp]. Output lands next to the script.
# MESEN must point at a portable Mesen.exe (a settings.json beside it keeps saves/states off the system drive).
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms
case "${2:-us}" in us) r="Bomberman '93 (USA)";; jp) r="Bomberman '93 (Japan)";; sp) r="Bomberman '93 - Special Version (Japan)";; esac
d=$(dirname "$1"); cat "$here/lib.lua" "$1" > "$d/_full.lua"
rom="$R/$r.pce"; command -v cygpath >/dev/null && rom=$(cygpath -m "$rom")  # MSYS skips path conversion for names with a quote
python "$here/mesen.py" "$d/_full.lua" "$rom"
