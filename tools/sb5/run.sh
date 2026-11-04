#!/bin/sh
# Run a Mesen Lua script headless on SB5. Usage: tools/sb5/run.sh script.lua [rom]  (ROM default: retail; "caravan" = event version)
here=$(cd "$(dirname "$0")" && pwd)
# MESEN = a portable Mesen.exe copy with settings.json beside it, so saves and CDL files stay in its folder
# (e.g. mkdir D:/tmp/<dir>/mesen; copy Mesen.exe there; touch settings.json)
export MESEN="${MESEN:?set MESEN to a portable Mesen.exe}"
rom="${2:-$here/../../roms/Super Bomberman 5 (Japan).sfc}"
[ "$2" = caravan ] && rom="$here/../../roms/Super Bomberman 5 (Japan) (Caravan Event Ban).sfc"
python "$here/../emu/mesen.py" "$1" "$rom"
