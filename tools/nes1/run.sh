#!/bin/sh
# Run a Lua test body in Mesen 2 headless: tools/nes1/run.sh script.lua [us|jp]
# lib.lua is prepended; output (printed lines, PNG shots, .ram dumps) lands in $SCRATCH/<script>_<region>/.
# MESEN must point at a portable Mesen.exe (a copy with its own settings.json, so saves/states stay out of the user profile).
: "${MESEN:?set MESEN to a portable Mesen.exe}"; : "${SCRATCH:?set SCRATCH to a scratch directory}"; export MESEN
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms; g=${2:-us}
case "$g" in us) r="(USA)";; jp) r="(Japan)";; esac
o=$SCRATCH/$(basename "$1" .lua)_$g; mkdir -p "$o"
{ echo "REG=\"$g\""; cat "$here/lib.lua" "$1"; } > "$o/body.lua"
python "$here/../emu/mesen_nes.py" "$o/body.lua" "$R/Bomberman $r.nes"
