#!/bin/sh
# Run a Lua script in Mesen 2 headless with lib.lua prepended: tools/gb2/run.sh script.lua [VER]
# MESEN: a portable Mesen.exe (own settings.json, Gameboy.Model "Gameboy"). Output (png/ram/vram/cdl, printed lines)
# lands in $SCRATCH/gb2/<script>_<ver>/ (SCRATCH defaults to /d/tmp/bomberman/gb), or in $OUT if set.
: "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms; v=${2:-jp}
case "$v" in jp) r="Bomberman GB 2 (Japan) (SGB Enhanced).gb";; us) r="Bomberman GB (USA, Europe) (SGB Enhanced).gb";; esac
S=${SCRATCH:-/d/tmp/bomberman/gb}
o=${OUT:-$S/gb2/$(basename "$1" .lua)_$v}; mkdir -p "$o"
{ echo "VER=\"$v\""; cat "$here/lib.lua" "$1"; } > "$o/body.lua"
python "$here/../emu/mesen_gb.py" "$o/body.lua" "$R/$r"
