#!/bin/sh
# Run a Mesen Lua script headless on the SB5 English ROM. Usage: tools/sb5en/run.sh script.lua [rom]  (default: the English ROM; "jp" = Japanese retail)
here=$(cd "$(dirname "$0")" && pwd -W)  # Windows form (D:/...), which Mesen can open
# MESEN = a portable Mesen.exe copy with settings.json beside it, so saves and CDL files stay in its folder
# (e.g. mkdir D:/tmp/<dir>/mesen; copy Mesen.exe there; touch settings.json)
export MESEN="${MESEN:?set MESEN to a portable Mesen.exe}"
rom="${2:-$here/../../roms/Super Bomberman 5 (English)[Official Localization].sfc}"
[ "$2" = jp ] && rom="$here/../../roms/Super Bomberman 5 (Japan).sfc"
python "$here/../emu/mesen.py" "$1" "$rom"
