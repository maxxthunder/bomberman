#!/bin/sh
# Run a Lua script in Mesen 2 headless with lib.lua prepended: tools/max/run.sh script.lua [VER]
# VER: blue, red (USA), hikari, yami (Japan), ain (Japan, Ain Version). MESEN: a portable Mesen.exe (own
# settings.json, Gameboy.Model "GameboyColor"). Output (png/ram/vram/cdl, printed lines) lands in
# $SCRATCH/max/<script>_<ver>/ (SCRATCH: a scratch folder, required), or in $OUT. ROM overrides the ROM.
: "${MESEN:?set MESEN to a portable Mesen.exe}"; export MESEN
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms; v=${2:-blue}
case "$v" in
  blue) r="Bomberman Max - Blue Champion (USA).gbc";; red) r="Bomberman Max - Red Challenger (USA).gbc";;
  hikari) r="Bomberman Max - Hikari no Yuusha (Japan).gbc";; yami) r="Bomberman Max - Yami no Senshi (Japan).gbc";;
  ain) r="Bomberman Max - Ain Version (Japan).gbc";;
esac
: "${SCRATCH:?set SCRATCH to a scratch folder}"; S=$SCRATCH
o=${OUT:-$S/max/$(basename "$1" .lua)_$v}; mkdir -p "$o"
{ echo "VER=\"$v\""; cat "$here/lib.lua" "$1"; } > "$o/body.lua"
# battery saves and CDLs persist in the Mesen folder between runs: start each run clean (KEEP=1 keeps them)
[ -n "$KEEP" ] || rm -f "$(dirname "$MESEN")"/Saves/*.srm "$(dirname "$MESEN")"/Debugger/*.cdl
python "$here/../emu/mesen_gb.py" "$o/body.lua" "${ROM:-$R/$r}"
