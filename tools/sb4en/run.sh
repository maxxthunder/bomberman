#!/bin/sh
# Run a Mesen Lua script on the SB4 English ROM: tools/sb4en/run.sh script.lua
# Portable Mesen copy (settings.json next to the exe = portable mode, pad 2 enabled), so nothing lands on C:
: "${MESEN:?set MESEN to the portable Mesen.exe (kept off C:, with its settings.json next to it)}"; export MESEN
python "$(dirname "$0")/../emu/mesen.py" "$1" "${ROM:-D:/repos/bomberman/roms/Super Bomberman 4 (English)[Official Localization].sfc}"
