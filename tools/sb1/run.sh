#!/bin/sh
# Run a Lua test script in Mesen 2 headless with lib.lua prepended: tools/sb1/run.sh script.lua [us|eu|jp|beta] [rom.sfc]
# (a third argument runs another ROM, e.g. one patched by make_debug_ips.py)
# Output (png/ram, CDLHEX lines on stdout) lands next to the script.
export MESEN="${MESEN:?set MESEN to a portable Mesen.exe (settings.json next to it keeps saves/states in its own folder)}"
# Multitap in port 2 (pads 2-5): MESEN_ARGS=--snes.port2.type=Multitap (see test_sound_test_pad5.lua)
here=$(cd "$(dirname "$0")" && pwd); R=$here/../../roms
case "${2:-us}" in us) r="(USA)";; eu) r="(Europe)";; jp) r="(Japan)";; beta) r="(USA) (Beta) (1993-05-11)";; esac
d=$(dirname "$1"); cat "$here/lib.lua" "$1" > "$d/_full.lua"
python "$here/mesen.py" "$d/_full.lua" "${3:-$R/Super Bomberman $r.sfc}"
