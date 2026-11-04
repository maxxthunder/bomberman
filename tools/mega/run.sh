#!/bin/sh
# Run a Lua test body in BizHawk (Genesis): tools/mega/run.sh script.lua [us|eu]
# lib.lua is prepended; output (log.txt, PNG shots) lands in $SCRATCH/<script>_<region>/ (SCRATCH defaults to /d/tmp/bomberman/mega).
export EMUHAWK="${EMUHAWK:-K:/Emulators/Bizhawk/EmuHawk.exe}"
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms; g=${2:-us}
case "$g" in us) r="(USA)";; eu) r="(Europe, Korea) (En)";; esac
S=${SCRATCH:-/d/tmp/bomberman/mega}
o=$S/$(basename "$1" .lua)_$g; mkdir -p "$o"
{ echo "REG=\"$g\""; echo "STATES=\"$(cd "$S" && pwd -W)/\""; cat "$here/lib.lua" "$1"; } > "$o/body.lua"
python "$here/../emu/bizhawk.py" "$o/body.lua" "$R/Mega Bomberman $r.md"
