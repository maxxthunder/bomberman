#!/bin/sh
# Run a Lua script in Mesen 2 headless on the English ROM: tools/sb5en/run.sh script.lua [jp|rom.sfc] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" sb5en "$@"
