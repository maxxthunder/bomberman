#!/bin/sh
# Run a Lua script in Mesen 2 headless: tools/sb5/run.sh script.lua [caravan|rom.sfc] (see tools/emu/run.sh)
exec sh "$(dirname "$0")/../emu/run.sh" sb5 "$@"
