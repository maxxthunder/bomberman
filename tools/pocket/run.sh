#!/bin/sh
# Run a Lua script in Mesen 2 headless with lib.lua prepended: tools/pocket/run.sh script.lua [VER]
# MESEN: a portable Mesen.exe (own settings.json; Gameboy.Model "Gameboy" for DMG, "GameboyColor" for CGB). Output
# (png/ram/vram/cdl, printed lines) lands in $SCRATCH/pocket/<script>_<ver>/ (SCRATCH must be set),
# or in $OUT if set. ROM overrides the ROM (e.g. a patched copy).
: "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms; v=${2:-us}
case "$v" in us) r="Pocket Bomberman (USA, Europe) (SGB Enhanced) (GB Compatible).gbc";; esac
S=${SCRATCH:?set SCRATCH to a scratch folder}
o=${OUT:-$S/pocket/$(basename "$1" .lua)_$v}; mkdir -p "$o"
{ echo "VER=\"$v\""; cat "$here/lib.lua" "$1"; } > "$o/body.lua"
python "$here/../emu/mesen_gb.py" "$o/body.lua" "${ROM:-$R/$r}"
