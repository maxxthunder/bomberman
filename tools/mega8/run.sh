#!/bin/sh
# Run a Lua test body in BizHawk on the 8-player demo: tools/mega8/run.sh script.lua [pad|tap]
# lib.lua is prepended. "tap" (default) plugs a Sega Team Player into each port (GPGX ControlType 4, P1-P8),
# "tap1" one Team Player in port 1 and a pad in port 2, "pad" plain pads. A copy of BizHawk's config.ini with that setting goes to $SCRATCH and is passed with --config,
# so the user's own config is never touched. Output lands in $SCRATCH/<script>_<mode>/.
export EMUHAWK="${EMUHAWK:-K:/Emulators/Bizhawk/EmuHawk.exe}"
here=$(cd "$(dirname "$0")" && pwd); m=${2:-tap}
S=${SCRATCH:?set SCRATCH to a scratch directory}; mkdir -p "$S"
case "$m" in tap) ct="4 4";; tap1) ct="4 1";; *) ct="1 1";; esac
python "$here/mkconfig.py" "$(dirname "$EMUHAWK")/config.ini" "$S/config_$m.ini" $ct
o=$S/$(basename "$1" .lua)_$m; mkdir -p "$o"
{ echo "MODE=\"$m\""; echo "STATES=\"$(cd "$S" && pwd -W)/\""; cat "$here/lib.lua" "$1"; } > "$o/body.lua"
CONFIG="$(cd "$S" && pwd -W)/config_$m.ini" python "$here/bizhawk8.py" "$o/body.lua" "$here/../../roms/Mega Bomberman - Special 8-Player-Demo (Europe) (Proto).md"
