#!/bin/sh
# Run a Lua script headless in a portable Mesen 2: tools/pce94/run.sh script.lua [card|demo] [VAR=value ...]
# lib.lua is prepended, then the VAR=value lines. Needs $SCRATCH (scratch folder). The portable Mesen lives in
# $SCRATCH/mesen (a settings.json next to the exe keeps its data folder there); the demo CD wants a System Card at
# $SCRATCH/mesen/Firmware/syscard3.pce. Output lands in $SCRATCH/<script>_<game>/.
here=$(cd "$(dirname "$0")" && pwd); R=$(cd "$here/../../roms" && pwd -W); S=${SCRATCH:?set SCRATCH}
script=$1; g=${2:-card}; shift; [ $# -gt 0 ] && shift
export MESEN=${MESEN:-$S/mesen/Mesen.exe}
case "$g" in card) rom="$R/Bomberman '94 (Japan).pce";; demo) rom="$R/Bomberman '94 (Japan) (Demo).cue";; esac
o=$S/$(basename "$script" .lua)_$g; mkdir -p "$o"
{ echo "STATES=\"$(cd "$S" && pwd -W)/\""; echo "GAME=\"$g\""; for v in "$@"; do echo "$v"; done; cat "$here/lib.lua" "$script"; } > "$o/body.lua"
python "$here/mesen.py" "$o/body.lua" "$rom" "$o"
