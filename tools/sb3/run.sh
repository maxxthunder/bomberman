#!/bin/sh
# Run a Lua script headless in Mesen 2 against an SB3 ROM.  Usage: tools/sb3/run.sh script.lua [eu|jp|beta]
here=$(cd "$(dirname "$0")" && pwd); r=$here/../../roms
# Portable Mesen (a settings.json next to the exe keeps its data folder there, off C:); built on first use, with a copy of the normal settings.
P=${SB3_MESEN_DIR:?set SB3_MESEN_DIR to a scratch folder for the portable Mesen (off C:)}
if [ -z "$MESEN" ]; then [ -f $P/Mesen.exe ] || { mkdir -p $P; cp /k/Emulators/Mesen/Mesen.exe $P/; echo "{}" > $P/settings.json; }; MESEN=$P/Mesen.exe; fi
export MESEN
case "${2:-eu}" in eu) rom="$r/Super Bomberman 3 (Europe).sfc";; jp) rom="$r/Super Bomberman 3 (Japan).sfc";; beta) rom="$r/Super Bomberman 3 (Europe) (Beta).sfc";; esac
python "$here/../emu/mesen.py" "$1" "$rom"
